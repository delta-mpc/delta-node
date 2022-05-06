from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Dict, List, TypeVar

import sqlalchemy as sa
from delta_node import chain, config, db, entity, pool, registry
from typing_extensions import Protocol

from .dataset import check_datasets
from .event_box import EventBox
from .manager import Manager

_logger = logging.getLogger(__name__)


T = TypeVar("T", contravariant=True)


class EventCallback(Protocol[T]):
    __name__: str

    async def __call__(self, monitor: T, event: entity.TaskEvent):
        ...


class Monitor(object):
    def __init__(self) -> None:
        self.callbacks: Dict[
            entity.EventType, List[EventCallback[Monitor]]
        ] = defaultdict(list)

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
                    fut = asyncio.create_task(callback(self, event))

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

    def register(self, event: entity.EventType, callback: EventCallback[Monitor]):
        self.callbacks[event].append(callback)

    def unregister(self, event: entity.EventType, callback: EventCallback[Monitor]):
        self.callbacks[event].remove(callback)


managers: Dict[str, Manager] = {}


async def create_task_manager(monitor: Monitor, task: entity.RunnerTask):
    node_address = await registry.get_node_address()

    if task.type == "horizontal":
        from .horizontal import ClientTaskManager
        event_box = EventBox(task.task_id)

        async def monitor_event(monitor: Monitor, event: entity.TaskEvent):
            _logger.debug(f"monitor event {event.type}")
            await event_box.recv_event(event)

        monitor.register("round_started", monitor_event)
        monitor.register("partner_selected", monitor_event)
        monitor.register("calculation_started", monitor_event)
        monitor.register("aggregation_started", monitor_event)
        monitor.register("round_ended", monitor_event)

        manager = ClientTaskManager(node_address, task, event_box)
        await manager.init()
        _logger.debug(f"client task manager {task.task_id} initialized")

        managers[task.task_id] = manager

        return manager
    else:
        raise TypeError(f"unknown task type {task.type}")


def run_task_manager(manager: Manager):
    fut = asyncio.ensure_future(manager.run())

    def _task_finish(fut: asyncio.Future):
        try:
            fut.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _logger.error(f"task {manager.task_id} error: {e}")
            _logger.exception(e)

    fut.add_done_callback(_task_finish)


async def monitor_task_create(monitor: Monitor, event: entity.TaskEvent):
    assert isinstance(event, entity.TaskCreateEvent)
    datasets = event.dataset.split(",")
    accept = await pool.run_in_io(check_datasets, datasets)

    if not accept:
        _logger.info(f"reject task {event.task_id}")
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
            status=entity.TaskStatus.PENDING,
        )
        sess.add(task)
        await sess.commit()

    manager = await create_task_manager(monitor, task)
    run_task_manager(manager)


async def monitor_task_finish(monitor: Monitor, event: entity.TaskEvent):
    assert isinstance(event, entity.TaskFinishEvent)
    task_id = event.task_id

    manager = managers.get(task_id)
    if manager is not None:
        await manager.finish(True)
        managers.pop(task_id)
    _logger.info(f"task {task_id} finish", extra={"task_id": task_id})


async def create_unfinished_task(monitor: Monitor, task: entity.RunnerTask):
    # check remote task
    try:
        remote_task = await chain.get_client().get_task(task.task_id)
        if remote_task.status == entity.TaskStatus.FINISHED:
            async with db.session_scope() as sess:
                task.status = entity.TaskStatus.FINISHED
                sess.add(task)
                await sess.commit()
        else:
            manager = await create_task_manager(monitor, task)
            run_task_manager(manager)

    except Exception as e:
        _logger.error(e)


async def start():
    monitor = Monitor()
    monitor.register("task_created", monitor_task_create)

    monitor.register("task_finish", monitor_task_finish)

    await monitor.start()
