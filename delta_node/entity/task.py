from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from delta_node.db import mapper_registry

from .base import BaseTable


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1
    FINISHED = 2
    ERROR = 3


@mapper_registry.mapped
@dataclass
class Task(BaseTable):
    __tablename__ = "Task"
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
    status: TaskStatus = field(
        default=TaskStatus.PENDING,
        metadata={"sa": sa.Column(sa.Enum(TaskStatus), nullable=False, index=True)},
    )

    name: Optional[str] = field(
        default=None, metadata={"sa": sa.Column(sa.String, nullable=True, index=False)}
    )
    type: Optional[str] = field(
        default=None, metadata={"sa": sa.Column(sa.String, nullable=True, index=False)}
    )
    url: Optional[str] = field(
        default=None, metadata={"sa": sa.Column(sa.String, nullable=True, index=False)}
    )

    run: bool = field(
        default=False,
        metadata={
            "sa": sa.Column(sa.Boolean, nullable=False, index=True, default=False)
        },
    )
