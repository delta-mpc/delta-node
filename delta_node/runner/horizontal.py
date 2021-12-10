import asyncio

from delta_node import db, entity, pool

from .dataset import check_dataset


async def monitor_task_create(event: entity.TaskCreateEvent):
    loop = asyncio.get_running_loop()
    accept = await loop.run_in_executor(pool.IO_POOL, check_dataset, event.dataset)

    if accept:
        async with db.get_session() as sess:
            task = entity.Task(
                creator=event.address,
                task_id=event.task_id,
                dataset=event.dataset,
                commitment=event.commitment,
                status=entity.TaskStatus.PENDING,
                url=event.url
            )
            sess.add(task)
            await sess.commit()


