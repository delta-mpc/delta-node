from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from delta_node.db import Base

from .base import BaseMixin

__all__ = ["TaskStatus", "Task"]


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1
    FINISHED = 2
    ERROR = 3
    CONFIRMED = 4


class Task(Base, BaseMixin):
    __tablename__ = "task"

    creator: Mapped[str] = mapped_column(nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(nullable=False, index=True)
    dataset: Mapped[str] = mapped_column(nullable=False, index=False)
    commitment: Mapped[bytes] = mapped_column(sa.BINARY, nullable=False, index=False)
    name: Mapped[str] = mapped_column(nullable=True, index=False)
    type: Mapped[str] = mapped_column(nullable=True, index=False)
    enable_verify: Mapped[bool] = mapped_column(sa.Boolean, nullable=True, index=False)
    tolerance: Mapped[int] = mapped_column(nullable=True, index=False)

    status: Mapped[TaskStatus] = mapped_column(
        sa.Enum(TaskStatus), nullable=False, index=True, default=TaskStatus.PENDING
    )
