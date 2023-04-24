from __future__ import annotations

import asyncio
import gc
import logging
from collections import defaultdict
from typing import Dict, List, TypeVar

from delta_node import chain, config, db, entity, pool, registry
from typing_extensions import Protocol

from .dataset import check_datasets
from .manager import Manager
from .event_box import EventBox

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
            async for event in chain.subscribe.get_client().subscribe(
                node_address,
                timeout=config.chain_heartbeat,
                retry_attemps=config.chain_retry,
                yield_heartbeat=False,
            ):
                if not isinstance(event, entity.TaskEvent):
                    continue
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


class ManagerStore(object):
    managers: Dict[str, Manager] = {}
    lock = asyncio.Lock()

    @classmethod
    async def get(cls, task_id: str) -> Manager:
        async with cls.lock:
            return cls.managers[task_id]

    @classmethod
    async def set(cls, task_id: str, manager: Manager):
        async with cls.lock:
            cls.managers[task_id] = manager

    @classmethod
    async def pop(cls, task_id: str) -> Manager:
        async with cls.lock:
            return cls.managers.pop(task_id)

    @classmethod
    def delete(cls, task_id: str):
        del cls.managers[task_id]


class EventBoxStore(object):
    event_boxes: Dict[str, EventBox] = {}
    lock = asyncio.Lock()

    @classmethod
    async def get(cls, task_id: str) -> EventBox:
        async with cls.lock:
            if task_id not in cls.event_boxes:
                event_box = EventBox(task_id)
                cls.event_boxes[task_id] = event_box
            return cls.event_boxes[task_id]

    @classmethod
    async def pop(cls, task_id: str) -> EventBox:
        async with cls.lock:
            return cls.event_boxes.pop(task_id)

    @classmethod
    def delete(cls, task_id: str):
        del cls.event_boxes[task_id]


async def create_task_manager(
    monitor: Monitor, task: entity.horizontal.RunnerTask | entity.hlr.RunnerTask
) -> Manager:
    node_address = await registry.get_node_address()
    if task.type == "horizontal":
        assert isinstance(task, entity.horizontal.RunnerTask)
        from .horizontal import ClientTaskManager

        event_box = await EventBoxStore.get(task.task_id)
        manager = ClientTaskManager(node_address, task, event_box)
    elif task.type == "hlr":
        assert isinstance(task, entity.hlr.RunnerTask)
        from .hlr import ClientTaskManager

        event_box = await EventBoxStore.get(task.task_id)
        manager = ClientTaskManager(node_address, task, event_box)
    else:
        raise TypeError(f"unknown task type {task.type}")

    await ManagerStore.set(task.task_id, manager)
    return manager


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
            _finish_task(manager.task_id)

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
        if event.task_type == "horizontal":
            task = entity.horizontal.RunnerTask(
                creator=event.address,
                task_id=event.task_id,
                dataset=event.dataset,
                commitment=event.commitment,
                url=event.url,
                type=event.task_type,
                status=entity.TaskStatus.PENDING,
            )
        elif event.task_type == "hlr":
            task = entity.hlr.RunnerTask(
                creator=event.address,
                task_id=event.task_id,
                dataset=event.dataset,
                commitment=event.commitment,
                url=event.url,
                type=event.task_type,
                status=entity.TaskStatus.PENDING,
                enable_verify=event.enable_verify,
                tolerance=event.tolerance,
            )
        else:
            raise TypeError(f"unknown task type {event.task_type}")

        sess.add(task)
        await sess.commit()

    manager = await create_task_manager(monitor, task)
    try:
        await manager.init()
    except:
        manager = await ManagerStore.pop(event.task_id)
        if manager is not None:
            await manager.finish(True)
        await EventBoxStore.pop(event.task_id)
        gc.collect()

    run_task_manager(manager)


async def monitor_task_finish(monitor: Monitor, event: entity.TaskEvent):
    assert isinstance(event, entity.TaskFinishEvent)
    task_id = event.task_id

    try:
        manager = await ManagerStore.pop(task_id)
        if manager is not None:
            await manager.finish(True)
        await EventBoxStore.pop(task_id)
    finally:
        gc.collect()

    _logger.info(f"task {task_id} finish", extra={"task_id": task_id})


def _finish_task(task_id: str):
    ManagerStore.delete(task_id)
    EventBoxStore.delete(task_id)
    gc.collect()


async def create_unfinished_task(
    monitor: Monitor, task: entity.horizontal.RunnerTask | entity.hlr.RunnerTask
):
    # check remote task
    try:
        if task.type == "horizontal":
            remote_task = await chain.horizontal.get_client().get_task(task.task_id)
        elif task.type == "hlr":
            remote_task = await chain.hlr.get_client().get_task(task.task_id)
        else:
            raise TypeError(f"unknown task type {task.type}")
        if remote_task.status == entity.TaskStatus.FINISHED:
            async with db.session_scope() as sess:
                task.status = entity.TaskStatus.FINISHED
                task = await sess.merge(task)
                sess.add(task)
                await sess.commit()
        else:
            manager = await create_task_manager(monitor, task)
            await manager.init()
            run_task_manager(manager)

    except Exception as e:
        _logger.error(e)


async def monitor_task_event(monitor: Monitor, event: entity.TaskEvent):
    task_id = event.task_id
    event_box = await EventBoxStore.get(task_id)
    await event_box.recv_event(event)


async def start():
    monitor = Monitor()
    monitor.register("task_created", monitor_task_create)

    monitor.register("round_started", monitor_task_event)
    monitor.register("partner_selected", monitor_task_event)
    monitor.register("calculation_started", monitor_task_event)
    monitor.register("aggregation_started", monitor_task_event)
    monitor.register("round_ended", monitor_task_event)

    monitor.register("task_finish", monitor_task_finish)

    await monitor.start()
