from dataclasses import dataclass, field
from enum import Enum

import sqlalchemy as sa
from delta_node.db import mapper_registry

from .base import BaseTable

__all__ = ["TaskStatus", "Task", "RunnerTask"]


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1
    FINISHED = 2
    ERROR = 3


@mapper_registry.mapped
@dataclass
class Task(BaseTable):
    __tablename__ = "task"
    __sa_dataclass_metadata_key__ = "sa"

    creator: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=True)}
    )
    task_id: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=True)}
    )
    dataset: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=False)}
    )
    commitment: bytes = field(
        metadata={"sa": sa.Column(sa.BINARY, nullable=False, index=False)}
    )
    name: str = field(metadata={"sa": sa.Column(sa.String, nullable=True, index=False)})
    type: str = field(metadata={"sa": sa.Column(sa.String, nullable=True, index=False)})

    status: TaskStatus = field(
        default=TaskStatus.PENDING,
        metadata={"sa": sa.Column(sa.Enum(TaskStatus), nullable=False, index=True)},
    )


@mapper_registry.mapped
@dataclass
class RunnerTask(BaseTable):
    __tablename__ = "runner_task"
    __sa_dataclass_metadata_key__ = "sa"

    creator: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=True)}
    )
    task_id: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=True)}
    )
    dataset: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=False)}
    )
    commitment: bytes = field(
        metadata={"sa": sa.Column(sa.BINARY, nullable=False, index=False)}
    )
    url: str = field(metadata={"sa": sa.Column(sa.String, nullable=True, index=False)})
    type: str = field(metadata={"sa": sa.Column(sa.String, nullable=True, index=False)})

    status: TaskStatus = field(
        default=TaskStatus.PENDING,
        metadata={"sa": sa.Column(sa.Enum(TaskStatus), nullable=False, index=True)},
    )
