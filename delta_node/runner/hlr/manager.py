from __future__ import annotations

import asyncio
import logging

import delta.serialize
from delta.core.task import DataLocation, Step, Task

from delta_node import chain, db, entity, pool, serialize, utils, zk
from delta_node.runner import loc
from delta_node.runner.event_box import EventBox
from delta_node.runner.manager import Manager
from delta_node.utils import free_memory

from .agg import ClientAggregator, NotSelected
from .commu import CommuClient
from .context import ClientTaskContext

_logger = logging.getLogger(__name__)


class ClientTaskManager(Manager):
    def __init__(
        self, node_address: str, task: entity.hlr.RunnerTask, event_box: EventBox
    ) -> None:
        assert (
            task.task_id == event_box.task_id
        ), "task.task_id is not equal to event_box.task_id"
        self.node_address = node_address
        self.task_entity = task

        self.task: Task
        self.event_box = event_box
        self.client = CommuClient(task.url)

        self.running_fut: asyncio.Future | None = None

        self.ctx = ClientTaskContext(task.task_id)
        super().__init__(task.task_id, self.ctx)

    def _check_step(self, step: Step) -> bool:
        for var in step.inputs:
            if var.location == DataLocation.CLIENT and not self.ctx.has(var):
                return False
        return True

    async def init(self):
        def download_task() -> Task:
            config_file = loc.task_config_file(self.task_id)
            with open(config_file, mode="wb") as f:
                self.client.download_task_config(self.task_id, f)

            return delta.serialize.load_task(config_file)

        self.task = await pool.run_in_io(download_task)
        _logger.info(
            f"task {self.task_id} download task config", extra={"task_id": self.task_id}
        )

        async with db.session_scope() as sess:
            self.task_entity.status = entity.TaskStatus.RUNNING
            task_entity = await sess.merge(self.task_entity)
            sess.add(task_entity)
            await sess.commit()

    async def execute_round(self) -> int:
        event = await self.event_box.wait_for_event("round_started")
        assert isinstance(event, entity.RoundStartedEvent)
        assert event.task_id == self.task_id
        round = event.round

        step = self.task.steps[round - 1]

        if self._check_step(step):
            aggregator = ClientAggregator(
                self.node_address,
                self.task_id,
                round,
                self.task.strategy,
                step.agg_names,
                self.event_box,
                self.client,
            )
            async with aggregator.aggregate(self.ctx):
                server_vars = [
                    var for var in step.inputs if var.location == DataLocation.SERVER
                ]
                futs = [
                    pool.run_in_io(self.ctx.download, self.client, var)
                    for var in server_vars
                ]
                await asyncio.gather(*futs)
                _logger.debug("start running step map")
                try:
                    await pool.run_in_worker(step.map, self.ctx)
                finally:
                    free_memory()
                _logger.debug("complete running step map")

        event = await self.event_box.wait_for_event(
            "round_ended", self.task.strategy.connection_timeout * 2
        )
        assert isinstance(event, entity.RoundEndedEvent)
        assert (
            event.task_id == self.task_id
        ), f"event task id {event.task_id} is not equla to local task id {self.task_id}"
        assert (
            event.round == round
        ), f"event round {event.round} is not equal to local round {round}"
        _logger.info(
            f"task {self.task_id} round {round} finish",
            extra={"task_id": self.task_id},
        )
        return round

    async def finish(self, success: bool):
        async with db.session_scope() as sess:
            if success:
                self.task_entity.status = entity.TaskStatus.FINISHED
            else:
                self.task_entity.status = entity.TaskStatus.ERROR
            task_entity = await sess.merge(self.task_entity)
            sess.add(task_entity)
            await sess.commit()

        if self.running_fut is not None:
            self.running_fut.cancel()

        if success and self.task_entity.enable_verify:
            await self.verify()

        await pool.run_in_io(self.ctx.clear)
        await pool.run_in_io(self.client.close)

    async def verify(self):
        # upload data commitment
        data = self.ctx.get_data()
        data_commitments = utils.calc_data_commitment(data)
        data_futs = []
        for i, data_commitment in enumerate(data_commitments):
            _logger.debug(
                f"task {self.task_id} data commitment {serialize.bytes_to_hex(data_commitment)}"
            )
            data_fut = asyncio.create_task(
                chain.datahub.get_client().register(
                    self.node_address, self.task_entity.dataset, i, data_commitment
                )
            )
            data_fut.add_done_callback(
                lambda _: _logger.info(
                    f"task {self.task_id} upload data commitment",
                    extra={"task_id": self.task_id},
                )
            )
            data_futs.append(data_fut)
        # get weight
        weight = self.ctx.get_weight()
        # generate proof
        proof_fut = asyncio.create_task(
            zk.get_client().prove(weight.tolist(), data.tolist())
        )
        proof_fut.add_done_callback(
            lambda _: _logger.info(
                f"task {self.task_id} generate zk proof",
                extra={"task_id": self.task_id},
            )
        )
        proofs = (await asyncio.gather(proof_fut, *data_futs))[0]
        # verify
        verify_futs = []
        block_size = utils.constant.data_block_size()
        for proof in proofs:
            if proof.index == len(proofs) - 1:
                samples = len(data) % block_size
            else:
                samples = block_size
            fut = asyncio.create_task(
                chain.hlr.get_client().verify(
                    self.node_address,
                    self.task_id,
                    len(weight),
                    proof.proof,
                    proof.pub_signals,
                    proof.index,
                    samples,
                )
            )

            def _done(task):
                try:
                    _, valid = task.result()
                    if valid:
                        _logger.info(
                            f"task {self.task_id} proof {proof.index} verification approved",
                            extra={"task_id": self.task_id},
                        )
                    else:
                        _logger.info(
                            f"task {self.task_id} proof {proof.index} verification failed",
                            extra={"task_id": self.task_id},
                        )
                except:
                    _logger.info(
                        f"task {self.task_id} proof {proof.index} verification failed",
                        extra={"task_id": self.task_id},
                    )

            fut.add_done_callback(_done)
            verify_futs.append(fut)
        await asyncio.wait(verify_futs, return_when=asyncio.FIRST_EXCEPTION)

    async def run(self):
        while True:
            try:
                self.running_fut = asyncio.ensure_future(self.execute_round())
                round = await self.running_fut
                self.running_fut = None
                if round >= len(self.task.steps):
                    break
            except NotSelected:
                continue
            except Exception:
                await self.finish(False)
                raise

    async def recv_event(self, event: entity.TaskEvent):
        await self.event_box.recv_event(event)
