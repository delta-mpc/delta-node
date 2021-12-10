from delta_node import db, entity
import sqlalchemy as sa

from . import horizontal


async def run_task(task_id: str):
    async with db.get_session() as sess:
        q = (
            sa.select(entity.Task)
            .where(entity.Task.task_id == task_id)
            .where(entity.Task.url.is_(None))  # type: ignore
        )
        task: entity.Task = (await sess.execute(q)).scalar_one()

    if task.type == "horizontal":
        await horizontal.run_task(task)
    else:
        raise ValueError(f"unknown task type {task.type}")
