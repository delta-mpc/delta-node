import asyncio
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Optional

import sqlalchemy as sa
from delta_node import chain, db, entity, pool, registry, shutdown, config

from .dataset import check_dataset
from .horizontal import HFLTaskRunner

if TYPE_CHECKING:
    from .runner import TaskRunner

_logger = logging.getLogger(__name__)


EventCallback = Callable[[entity.TaskEvent], Coroutine[None, None, None]]


class Monitor(object):
    def __init__(self) -> None:
        self.callbacks: Dict[entity.EventType, List[EventCallback]] = defaultdict(list)

    async def start(self):
        _logger.info("monitor started")
        node_address = await registry.get_node_address()
        try:
            async for event in chain.get_client().subscribe(
                node_address,
                timeout=config.chain_heartbeat,
                retry_attemps=config.chain_retry,
            ):
                _logger.debug(f"event: {event.type}")
                callbacks = self.callbacks[event.type]
                for callback in callbacks:
                    fut = asyncio.create_task(callback(event))

                    def _done_callback(fut: asyncio.Task):
                        try:
                            fut.result()
                            _logger.debug(
                                f"event {event.type} callback {callback.__name__} done"
                            )
                        except Exception as e:
                            _logger.error(
                                f"event {event.type} callback {callback.__name__} error"
                            )
                            _logger.exception(e)

                    fut.add_done_callback(_done_callback)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _logger.exception(e)
            raise
        finally:
            _logger.info("monitor closed")

    def register(self, event: entity.EventType, callback: EventCallback):
        self.callbacks[event].append(callback)

    def unregister(self, event: entity.EventType, callback: EventCallback):
        self.callbacks[event].remove(callback)


runners: "Dict[str, TaskRunner]" = {}
runners_lock = asyncio.Lock()


def create_task_runner(task: entity.RunnerTask):
    if task.type == "horizontal":
        task_runner = HFLTaskRunner(task)
        _logger.debug(f"create task runner for {task.task_id}")
        return task_runner
    else:
        raise ValueError(f"unknown task type {task.type}")


async def monitor_task_create(event: entity.TaskEvent):
    assert isinstance(event, entity.TaskCreateEvent)
    loop = asyncio.get_running_loop()
    accept = await loop.run_in_executor(pool.IO_POOL, check_dataset, event.dataset)

    if not accept:
        _logger.debug(f"reject task {event.task_id}")
        return

    _logger.info(f"start run task {event.task_id}", extra={"task_id": event.task_id})
    async with db.session_scope() as sess:
        task = entity.RunnerTask(
            creator=event.address,
            task_id=event.task_id,
            dataset=event.dataset,
            commitment=event.commitment,
            url=event.url,
            type=event.task_type,
        )
        sess.add(task)
        await sess.commit()

    async with runners_lock:
        task_runner = create_task_runner(task)

        await task_runner.dispatch(event)

        async with db.session_scope() as sess:
            task.status = entity.TaskStatus.RUNNING
            sess.add(task)
            await sess.commit()
            _logger.debug(f"task {event.task_id} start running")

        runners[event.task_id] = task_runner


async def monitor_event(event: entity.TaskEvent):
    task_id = event.task_id

    async with runners_lock:
        if task_id not in runners:
            return
        async with db.session_scope() as sess:
            q = (
                sa.select(entity.RunnerTask)
                .where(entity.RunnerTask.task_id == task_id)
                .where(entity.RunnerTask.status == entity.TaskStatus.RUNNING)
            )
            task: Optional[entity.RunnerTask] = (
                await sess.execute(q)
            ).scalar_one_or_none()
        if task is None:
            return

    runner = runners[task_id]
    try:
        await runner.dispatch(event)
    except Exception as e:
        _logger.error(f"task {task_id} error {str(e)}")
        _logger.exception(e)

        await runner.finish()

        async with runners_lock:
            async with db.session_scope() as sess:
                task.status = entity.TaskStatus.ERROR
                sess.add(task)
                await sess.commit()
            del runners[task_id]


async def monitor_task_finish(event: entity.TaskEvent):
    assert isinstance(event, entity.TaskFinishEvent)
    task_id = event.task_id

    async with runners_lock:
        if task_id not in runners:
            return
        async with db.session_scope() as sess:
            q = (
                sa.select(entity.RunnerTask)
                .where(entity.RunnerTask.task_id == task_id)
                .where(
                    sa.or_(
                        entity.RunnerTask.status == entity.TaskStatus.RUNNING,  # type: ignore
                        entity.RunnerTask.status == entity.TaskStatus.PENDING,  # type: ignore
                    )
                )
            )
            task: Optional[entity.RunnerTask] = (
                await sess.execute(q)
            ).scalar_one_or_none()
        if task is None:
            return

    runner = runners[task_id]
    _logger.debug(f"task {task_id} finish")

    await runner.finish()

    async with runners_lock:
        async with db.session_scope() as sess:
            task.status = entity.TaskStatus.FINISHED
            sess.add(task)
            await sess.commit()

        del runners[task_id]


async def create_unfinished_task(task: entity.RunnerTask):
    # check remote task
    try:
        remote_task = await chain.get_client().get_task(task.task_id)
        if remote_task.status == entity.TaskStatus.FINISHED:
            async with db.session_scope() as sess:
                task.status = entity.TaskStatus.FINISHED
                sess.add(task)
                await sess.commit()
        else:
            runner = create_task_runner(task)
            runners[task.task_id] = runner
    except Exception as e:
        _logger.error(e)


async def start():
    monitor = Monitor()
    monitor.register("task_created", monitor_task_create)

    monitor.register("round_started", monitor_event)
    monitor.register("partner_selected", monitor_event)
    monitor.register("calculation_started", monitor_event)
    monitor.register("aggregation_started", monitor_event)
    monitor.register("round_ended", monitor_event)

    monitor.register("task_finish", monitor_task_finish)

    await monitor.start()
