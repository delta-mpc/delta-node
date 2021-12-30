import asyncio
from typing import List

import sqlalchemy as sa
from delta_node import db, entity

from . import horizontal


async def _run_task(task: entity.Task):
    if task.type == "horizontal":
        await horizontal.run_task(task)
    else:
        raise ValueError(f"unknown task type {task.type}")


async def run_task(task_id: str):
    async with db.session_scope() as sess:
        q = sa.select(entity.Task).where(entity.Task.task_id == task_id)
        task: entity.Task = (await sess.execute(q)).scalar_one()

    await _run_task(task)


async def run_unfinished_tasks():
    async with db.session_scope() as sess:
        q = (
            sa.select(entity.Task)
            .where(entity.Task.status != entity.TaskStatus.FINISHED)
            .order_by(entity.Task.id)
        )
        tasks: List[entity.Task] = (await sess.execute(q)).scalars().all()

    for task in tasks:
        asyncio.create_task(_run_task(task))
