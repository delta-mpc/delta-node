import logging
from concurrent import futures
from functools import partial
from io import BytesIO
from typing import Dict

import delta.task as delta_task

from .. import contract, node, config
from ..commu import CommuClient
from ..model import TaskStatus
from .node import LocalNode
from .task import add_task, join_task


_logger = logging.getLogger(__name__)


def execute_task(task_id: int, url: str, creator_id: str):
    logging.basicConfig(level=logging.INFO)
    client = CommuClient(url)
    node_id = node.get_node_id()
    if client.join_task(task_id, node_id):
        _logger.info(f"member {node_id} join task {task_id}")
        metadata = client.get_metadata(task_id, node_id)
        _logger.info(f"member {node_id} get metadata of task {task_id}")
        add_task(task_id, url, creator_id, metadata)
        join_task(task_id, node_id)
        local_node = LocalNode(config.data_dir, task_id, metadata, client)

        with BytesIO() as f:
            client.get_file(task_id, node_id, 0, "cfg", f)
            task = delta_task.load(f)
            _logger.info(f"member {node_id} get task cfg of task {task_id}")
        task.run(local_node)
    else:
        _logger.info(f"member {node_id} cannot join task {task_id}")


class Executor(object):
    def __init__(self) -> None:
        self._event_filter = contract.new_event_filter()
        self._pool = futures.ProcessPoolExecutor()

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
                event = self._event_filter.wait_for_event("Task")
                _logger.info(event)
                if event is not None:
                    fut = self._pool.submit(
                        execute_task,
                        task_id=event.task_id,
                        url=event.url,
                        creator_id=event.address,
                    )
                    self._task_status[event.task_id] = TaskStatus.RUNNING
                    fut.add_done_callback(
                        partial(self._task_done, task_id=event.task_id)
                    )
        finally:
            self._event_filter.terminate()
            self._event_filter.join()


def run():
    executor = Executor()
    executor.run()
