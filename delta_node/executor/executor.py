import logging
import multiprocessing as mp
import os
import queue
import time
from concurrent import futures
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from typing import Dict

from delta.serialize import load_task
from delta.task import HorizontalTask

from .. import config, contract, log, node
from ..commu import CommuClient
from ..exceptions import TaskContinue
from ..model import TaskStatus
from .node import HorizontalLocalNode
from .task import add_task

_logger = logging.getLogger(__name__)


@dataclass
class TaskEvent(object):
    task_id: int
    url: str
    creator_id: str


def _check_dataset(dataset: str) -> bool:
    return os.path.exists(os.path.join(config.data_dir, dataset))


def execute_task(
    log_queue: mp.Queue, task_id: int, url: str, creator_id: str
):
    log.init(log_queue)
    client = CommuClient(url)
    node_id = node.get_node_id()
    metadata = client.get_metadata(task_id, node_id)
    _logger.info(
        f"member {node_id} get metadata of task {task_id}",
    )

    try:
        if _check_dataset(metadata.dataset):
            _logger.info(f"member {node_id} can join the task {task_id}")
            add_task(task_id, url, creator_id, metadata)

            with BytesIO() as f:
                client.get_file(task_id, node_id, "cfg", f)
                f.seek(0)
                task = load_task(f)
                _logger.info(
                    f"member {node_id} get task cfg of task {task_id}",
                    extra={"task_id": task_id},
                )
                if task.type == "horizontal":
                    assert isinstance(task, HorizontalTask)
                    local_node = HorizontalLocalNode(
                        task_id, client, config.data_dir, metadata, task.algorithm()
                    )
                    task.run(local_node)
                else:
                    raise TypeError(f"unknown task type {task.type}")
        else:
            _logger.info(f"member {node_id} cannot join the task {task_id}")
    except Exception as e:
        _logger.exception(e)
        raise


class Executor(object):
    def __init__(self) -> None:
        self._event_filter = contract.new_event_filter()
        self._pool = futures.ProcessPoolExecutor()
        self._task_queue: queue.Queue[TaskEvent] = mp.Manager().Queue()

        self._task_status: Dict[int, TaskStatus] = {}

    def _task_done(self, fut: futures.Future, task_event: TaskEvent):
        try:
            fut.result()
            self._task_status[task_event.task_id] = TaskStatus.FINISHED
            _logger.info(f"task {task_event.task_id} finish")
        except TaskContinue:
            _logger.info(f"task {task_event.task_id} should continue")
            time.sleep(10)
            self._task_queue.put(task_event)
        except:
            _logger.info(f"task {task_event.task_id} error")
            self._task_status[task_event.task_id] = TaskStatus.ERROR

    def run(self):
        try:
            self._event_filter.start()
            while True:
                event = self._event_filter.wait_for_event("Task", timeout=0.1)
                if event is not None:
                    self._task_queue.put(
                        TaskEvent(event.task_id, event.url, event.address)
                    )
                else:
                    try:
                        task_event = self._task_queue.get(block=False)
                        _logger.info(f"execute task {task_event.task_id}")
                        fut = self._pool.submit(
                            execute_task,
                            log_queue=log.get_log_queue(),
                            task_id=task_event.task_id,
                            url=task_event.url,
                            creator_id=task_event.creator_id,
                        )
                        self._task_status[task_event.task_id] = TaskStatus.RUNNING
                        fut.add_done_callback(
                            partial(self._task_done, task_event=task_event)
                        )
                    except queue.Empty:
                        continue
        finally:
            self._event_filter.terminate()
            self._event_filter.join()


def run():
    executor = Executor()
    executor.run()
