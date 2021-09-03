from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator

from delta.serialize import load_task
from sqlalchemy.orm import Session

from .. import channel, model
from ..exceptions import TaskFinishedError
from .location import task_cfg_file


class TaskManager(ABC):
    def __init__(self, task: model.Task, *, session: Session = None) -> None:
        self._task = task
        self._task_id = task.task_id
        self._task_status = task.status
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)

        cfg_file = task_cfg_file(self._task_id)
        self._task_item = load_task(cfg_file)

    @property
    def type(self) -> str:
        return self._task.type

    @abstractmethod
    def get_metadata(self, member_id: str) -> model.TaskMetadata:
        ...

    @abstractmethod
    def join(self, member_id: str, *, session: Session = None) -> bool:
        ...

    @abstractmethod
    def finish_task(self, member_id: str, *, session: Session = None):
        ...

    @abstractmethod
    def get_file(self, member_id: str, file_type: str) -> str:
        ...

    @abstractmethod
    @contextmanager
    def aggregate_result(self, member_id: str, extra_msg: bytes) -> Generator[channel.OuterChannel, None, None]:
        ...

    @abstractmethod
    @contextmanager
    def aggregate_metrics(self, member_id: str, extra_msg: bytes) -> Generator[channel.OuterChannel, None, None]:
        ...
