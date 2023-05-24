from __future__ import annotations

import asyncio
import logging

import delta.serialize
from delta.core.task import DataLocation, Step, Task

from delta_node import db, entity, pool
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
        self, node_address: str, task: entity.horizontal.RunnerTask, event_box: EventBox
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

        await pool.run_in_io(self.ctx.clear)
        await pool.run_in_io(self.client.close)

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
