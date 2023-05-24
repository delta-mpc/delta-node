from __future__ import annotations

import logging

import delta.serialize
import sqlalchemy as sa
from delta.core.strategy import Strategy
from delta.core.task import DataLocation, EarlyStop, Task

from delta_node import db, entity, pool, serialize
from delta_node.chain import horizontal as chain
from delta_node.coord import Manager, loc
from delta_node.utils import free_memory

from .agg import ServerAggregator
from .context import ServerTaskContext

_logger = logging.getLogger(__name__)


class ServerTaskManager(Manager):
    def __init__(self, node_address: str, task: entity.Task) -> None:
        self.node_address = node_address
        self.task_entity = task

        self.task: Task
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
            self.task_entity.status = entity.TaskStatus.RUNNING
            task_entity = await sess.merge(self.task_entity)
            sess.add(task_entity)
            await sess.commit()

            q = (
                sa.select(entity.horizontal.TaskRound)
                .where(entity.horizontal.TaskRound.task_id == self.task_id)
                .order_by(sa.desc(entity.horizontal.TaskRound.round))
                .limit(1)
                .offset(0)
            )
            task_round: entity.horizontal.TaskRound | None = (
                (await sess.execute(q)).scalars().first()
            )
        self.round = 1 if task_round is None else task_round.round

    async def execute_round(self, round: int) -> bool:
        res = True
        # start round
        tx_hash = await chain.get_client().start_round(
            self.node_address, self.task_id, round
        )
        _logger.info(
            f"[Start Round] task {self.task_id} round {round} start",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        # save task round to db
        task_round = entity.horizontal.TaskRound(
            task_id=self.task_id,
            round=round,
            status=entity.horizontal.RoundStatus.STARTED,
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
            self.task_entity.status = entity.TaskStatus.FINISHED
            task_entity = await sess.merge(self.task_entity)
            sess.add(task_entity)
            await sess.commit()
        tx_hash = await chain.get_client().finish_task(self.node_address, self.task_id)
        _logger.info(
            f"[Finish Task] task {self.task_id} finished",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
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
