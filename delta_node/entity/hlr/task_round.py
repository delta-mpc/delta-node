from dataclasses import field
from enum import Enum
from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, mapped_column, Mapped

from delta_node.db import Base

from ..base import BaseMixin

if TYPE_CHECKING:
    from .round_member import RoundMember

__all__ = ["RoundStatus", "TaskRound"]


class RoundStatus(Enum):
    STARTED = 0
    RUNNING = 1
    CALCULATING = 2
    AGGREGATING = 3
    FINISHED = 4


class TaskRound(Base, BaseMixin):
    __tablename__ = "hlr_task_round"

    task_id: Mapped[str] = mapped_column(index=True, nullable=False)
    round: Mapped[int] = mapped_column(nullable=False, index=True)
    status: Mapped[RoundStatus] = mapped_column(
        sa.Enum(RoundStatus), nullable=False, index=True
    )
    weight_commitment: Mapped[bytes] = mapped_column(
        sa.BINARY, nullable=False, index=False
    )

    joined_clients: List[str] = field(default_factory=list)
    finished_clients: List[str] = field(default_factory=list)

    members: Mapped[List["RoundMember"]] = relationship(
        "delta_node.entity.hlr.round_member.RoundMember",
        primaryjoin="foreign(delta_node.entity.hlr.round_member.RoundMember.round_id) == delta_node.entity.hlr.task_round.TaskRound.id",
        back_populates="round",
        default_factory=list,
    )
