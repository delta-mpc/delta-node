from __future__ import annotations

import asyncio
from logging import getLogger
from typing import Dict, List

import sqlalchemy as sa
from delta_node import db, entity

from . import loc
from .create import create_task, TaskConfig
from .manager import Manager

_logger = getLogger(__name__)

_managers: Dict[str, Manager] = {}


def get_task_manager(task_id: str) -> Manager | None:
    return _managers.get(task_id)


async def run_task(node_address: str, task: entity.Task):
    try:
        if task.type == "horizontal":
            from .horizontal import ServerTaskManager

            manager = ServerTaskManager(node_address, task)
            _managers[task.task_id] = manager
            await manager.run()
            _managers.pop(task.task_id)
        elif task.type == "hlr":
            from .hlr import ServerTaskManager

            manager = ServerTaskManager(node_address, task)
            _managers[task.task_id] = manager
            await manager.run()
            _managers.pop(task.task_id)
        else:
            raise TypeError(f"unknown task type {task.type}")
    except Exception as e:
        async with db.session_scope() as sess:
            task.status = entity.TaskStatus.ERROR
            task = await sess.merge(task)
            sess.add(task)
            await sess.commit()
        _logger.error(
            f"task {task.task_id} error: {str(e)}", extra={"task_id": task.task_id}
        )
        raise


async def run_unfinished_tasks(node_address: str):
    async with db.session_scope() as sess:
        q = (
            sa.select(entity.Task)
            .where(entity.Task.status != entity.TaskStatus.FINISHED)
            .order_by(entity.Task.id)
        )
        tasks: List[entity.Task] = (await sess.execute(q)).scalars().all()

    for task in tasks:
        asyncio.create_task(run_task(node_address, task))


__all__ = [
    "loc",
    "create_task",
    "TaskConfig",
    "get_task_manager",
    "run_task",
    "run_unfinished_tasks",
    "Manager",
]
