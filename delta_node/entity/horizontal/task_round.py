from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from delta_node.db import mapper_registry
from sqlalchemy.orm import relationship

from ..base import BaseTable

if TYPE_CHECKING:
    from .round_member import RoundMember

__all__ = ["RoundStatus", "TaskRound"]


class RoundStatus(Enum):
    STARTED = 0
    RUNNING = 1
    CALCULATING = 2
    AGGREGATING = 3
    FINISHED = 4


@mapper_registry.mapped
@dataclass
class TaskRound(BaseTable):
    __tablename__ = "task_round"
    __sa_dataclass_metadata_key__ = "sa"

    task_id: str = field(
        metadata={"sa": sa.Column(sa.String, index=True, nullable=False)}
    )
    round: int = field(
        metadata={"sa": sa.Column(sa.Integer, nullable=False, index=True)}
    )
    status: RoundStatus = field(
        metadata={"sa": sa.Column(sa.Enum(RoundStatus), nullable=False, index=True)}
    )

    clients: List[str] = field(default_factory=list)

    members: List["RoundMember"] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "delta_node.entity.horizontal.round_member.RoundMember",
                primaryjoin="foreign(delta_node.entity.horizontal.round_member.RoundMember.round_id) == delta_node.entity.horizontal.task_round.TaskRound.id",
                back_populates="round",
            )
        },
    )
