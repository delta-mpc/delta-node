from dataclasses import dataclass
import logging
import multiprocessing as mp
from concurrent import futures
from functools import partial
from io import BytesIO
import os
import queue
from typing import Dict

import delta.task as delta_task
from delta.task import HorizontolTask

from .. import config, contract, log, node
from ..exceptions import TaskContinue
from ..commu import CommuClient
from ..model import TaskStatus
from .node import HorizontolLocalNode
from .task import add_task

_logger = logging.getLogger(__name__)


@dataclass
class TaskEvent(object):
    task_id: int
    url: str
    creator_id: str


def _check_dataset(dataset: str) -> bool:
    return os.path.exists(os.path.join(config.data_dir, dataset))


def execute_task(log_queue: mp.Queue, task_id: int, url: str, creator_id: str, task_queue: mp.Queue):
    log.init(log_queue)
    client = CommuClient(url)
    node_id = node.get_node_id()
    metadata = client.get_metadata(task_id, node_id)
    _logger.info(
        f"member {node_id} get metadata of task {task_id}",
    )

    if _check_dataset(metadata.dataset):
        _logger.info(
            f"member {node_id} can join the task {task_id}"
        )
        _logger.info(
            f"member {node_id} join task {task_id}", extra={"task_id": task_id}
        )
        add_task(task_id, url, creator_id, metadata)

        with BytesIO() as f:
            client.get_file(task_id, node_id, 0, "cfg", f)
            task = delta_task.load(f)
            _logger.info(
                f"member {node_id} get task cfg of task {task_id}",
                extra={"task_id": task_id},
            )
            if task.type == "horizontol":
                assert isinstance(task, HorizontolTask)
                local_node = HorizontolLocalNode(task_id, client, config.data_dir, metadata, task.algorithm())
                try:
                    task.run(local_node)
                except TaskContinue:
                    task_queue.put(TaskEvent(task_id, url, creator_id))
            else:
                raise RuntimeError(f"unknown task type {task.type}")
    else:
        _logger.info(
            f"member {node_id} cannot join the task {task_id}"
        )


class Executor(object):
    def __init__(self) -> None:
        self._event_filter = contract.new_event_filter()
        self._pool = futures.ProcessPoolExecutor()
        self._task_queue = mp.Manager().Queue()

        self._task_status: Dict[int, TaskStatus] = {}

    def _task_done(self, fut: futures.Future, task_id: int):
        try:
            fut.result()
            self._task_status[task_id] = TaskStatus.FINISHED
        except:
            self._task_status[task_id] = TaskStatus.ERROR

    def run(self):
        try:
            self._event_filter.start()
            while True:
                event = self._event_filter.wait_for_event("Task", timeout=0.1)
                _logger.info(event)
                if event is not None:
                    self._task_queue.put(TaskEvent(event.task_id, event.url, event.address))
                try:
                    task_event = self._task_queue.get(block=False)
                    fut = self._pool.submit(
                        execute_task,
                        log_queue=log.get_log_queue(),
                        task_id=task_event.task_id,
                        url=task_event.url,
                        creator_id=task_event.address,
                        task_queue=self._task_queue
                    )
                    self._task_status[task_event.task_id] = TaskStatus.RUNNING
                    fut.add_done_callback(
                        partial(self._task_done, task_id=task_event.task_id)
                    )
                except queue.Empty:
                    pass
        finally:
            self._event_filter.terminate()
            self._event_filter.join()


def run():
    executor = Executor()
    executor.run()
