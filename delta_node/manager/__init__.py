import logging
import threading
from collections import defaultdict
from typing import Dict

from sqlalchemy.orm import Session
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

from ..exceptions import TaskError, TaskNotReadyError
from .create import create_task
from .location import task_cfg_file, task_result_file, task_weight_file
from .task import get_task
from .horizontol import HorizontolTaskManager
from .base import TaskManager

__all__ = [
    "get_task_manager",
    "create_task",
    "task_cfg_file",
    "task_weight_file",
    "task_result_file",
    "TaskManager",
    "HorizontolTaskManager",
]

_logger = logging.getLogger(__name__)

_task_manager_registry: Dict[int, TaskManager] = {}
_task_manager_lock: Dict[int, threading.Lock] = defaultdict(threading.Lock)


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TaskNotReadyError),
    reraise=True,
)
def _new_task_manager(task_id: int, *, session: Session = None):
    task = get_task(task_id, session=session)
    if task is None:
        _logger.error(f"task {task_id} is not ready", extra={"task_id": task_id})
        raise TaskNotReadyError(task_id)

    if task.type == "horizontol":
        return HorizontolTaskManager(task)
    else:
        raise ValueError(f"unknown task type {task.type}")


def get_task_manager(task_id: int, *, session: Session = None) -> TaskManager:
    lock = _task_manager_lock[task_id]
    with lock:
        try:
            if task_id not in _task_manager_registry:
                manager = _new_task_manager(task_id, session=session)
                _task_manager_registry[task_id] = manager
        except TaskError as e:
            _logger.error(e)
            raise
        except Exception as e:
            _logger.exception(e)
            raise
        res = _task_manager_registry[task_id]
        return res
