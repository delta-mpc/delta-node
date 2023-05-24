from __future__ import annotations

import asyncio
import logging

import delta.serialize
import sqlalchemy as sa
from delta.core.strategy import Strategy
from delta.core.task import DataLocation, EarlyStop
from delta.core.task import Task as DTask

from delta_node import db, pool, serialize, utils
from delta_node.chain import hlr as chain
from delta_node.coord import Manager, loc
from delta_node.entity import Task, TaskStatus
from delta_node.entity.hlr import RoundStatus, TaskRound
from delta_node.utils import free_memory

from .agg import ServerAggregator
from .context import ServerTaskContext

_logger = logging.getLogger(__name__)


class ServerTaskManager(Manager):
    def __init__(self, node_address: str, task: Task) -> None:
        self.node_address = node_address
        self.task_entity = task

        self.task: DTask
        self.strategy: Strategy

        self.round = 0

        self.ctx = ServerTaskContext(task.task_id)
        super().__init__(task.task_id, self.ctx)

    async def init(self):
        config_file = loc.task_config_file(self.task_id)
        self.task = await pool.run_in_io(delta.serialize.load_task, config_file)
        self.strategy = self.task.strategy

        # save server var to context
        pairs = []
        for var in self.task.inputs:
            if var.location == DataLocation.SERVER and var.default is not None:
                pairs.append((var, var.default))
        self.ctx.set(*pairs)

        async with db.session_scope() as sess:
            self.task_entity.status = TaskStatus.RUNNING
            task_entity = await sess.merge(self.task_entity)
            sess.add(task_entity)
            await sess.commit()

            q = (
                sa.select(TaskRound)
                .where(TaskRound.task_id == self.task_id)
                .order_by(sa.desc(TaskRound.round))
                .limit(1)
                .offset(0)
            )
            task_round: TaskRound | None = (await sess.execute(q)).scalars().first()
        self.round = 1 if task_round is None else task_round.round

    async def execute_round(self, round: int) -> bool:
        res = True
        # calculate weight commitment
        try:
            weight = self.ctx.get_weight()
            weight_commitment = utils.calc_weight_commitment(weight)
        except ValueError:
            weight_commitment = b""
        # start round
        tx_hash = await chain.get_client().start_round(
            self.node_address, self.task_id, round, weight_commitment
        )
        _logger.info(
            f"[Start Round] task {self.task_id} round {round} start",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        # save task round to db
        task_round = TaskRound(
            task_id=self.task_id,
            round=round,
            status=RoundStatus.STARTED,
            weight_commitment=weight_commitment,
        )
        async with db.session_scope() as sess:
            sess.add(task_round)
            await sess.commit()
        # run step
        step = self.task.steps[round - 1]

        aggregator = ServerAggregator(
            self.node_address, task_round, self.strategy, step.agg_names
        )
        try:
            async with aggregator.aggregate(self.ctx):
                _logger.debug("server complete aggregating")
                try:
                    await pool.run_in_worker(step.reduce, self.ctx)
                finally:
                    free_memory()
        except EarlyStop:
            res = False
        # end round
        tx_hash = await chain.get_client().end_round(
            self.node_address, self.task_id, round
        )
        _logger.info(
            f"[End Round] task {self.task_id} round {round} finish",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        return res

    def save_result(self):
        vars = self.ctx.get(*self.task.outputs)
        if len(vars) == 1:
            result = vars[0]
        else:
            result = tuple(vars)
        serialize.dump_obj(loc.task_result_file(self.task_id), result)

    async def finish(self):
        await pool.run_in_io(self.save_result)

        async with db.session_scope() as sess:
            self.task_entity.status = TaskStatus.FINISHED
            task_entity = await sess.merge(self.task_entity)
            sess.add(task_entity)
            await sess.commit()
        tx_hash = await chain.get_client().finish_task(self.node_address, self.task_id)
        _logger.info(
            f"[Finish Task] task {self.task_id} finished",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        if self.task_entity.enable_verify:
            await self.wait_verify()

    async def wait_verify(self):
        await asyncio.sleep(self.strategy.verify_timeout)
        state = await chain.get_client().get_verifier_state(self.task_id)
        if state.valid and len(state.unfinished_clients) == 0:
            tx_hash = await chain.get_client().confirm_verification(
                self.node_address, self.task_id
            )
            async with db.session_scope() as sess:
                self.task_entity.status = TaskStatus.CONFIRMED
                task_entity = await sess.merge(self.task_entity)
                sess.add(task_entity)
                await sess.commit()
            _logger.info(
                f"[Verify Task] task {self.task_id} zk verification confirmed",
                extra={"task_id": self.task_id, "tx_hash": tx_hash},
            )
        elif not state.valid:
            raise ValueError(
                f"task verification failed, invalid members {state.invalid_clients}"
            )
        elif len(state.unfinished_clients) > 0:
            raise ValueError(
                f"task verification timeout, unfinished members {state.unfinished_clients}"
            )

    async def run(self):
        await self.init()
        max_rounds = len(self.task.steps)
        while self.round < max_rounds + 1:
            has_next = await self.execute_round(self.round)
            if not has_next:
                break
            self.round += 1
        await self.finish()
