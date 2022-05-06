from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from delta_node.db import mapper_registry
from sqlalchemy.orm import relationship

from .base import BaseTable
from .task_round import RoundStatus

if TYPE_CHECKING:
    from .secret_share import SecretShare
    from .task_round import TaskRound

__all__ = ["RoundMember"]


@mapper_registry.mapped
@dataclass
class RoundMember(BaseTable):
    __tablename__ = "round_member"
    __sa_dataclass_metadata_key__ = "sa"

    round_id: int = field(
        metadata={"sa": sa.Column(sa.Integer, index=True, nullable=False)}
    )
    address: str = field(
        metadata={"sa": sa.Column(sa.String, index=True, nullable=False)}
    )
    status: RoundStatus = field(
        metadata={"sa": sa.Column(sa.Enum(RoundStatus), index=True, nullable=False)}
    )

    round: Optional["TaskRound"] = field(
        init=False,
        metadata={
            "sa": relationship(
                "TaskRound",
                primaryjoin="foreign(RoundMember.round_id) == TaskRound.id",
                back_populates="members",
            )
        },
    )

    send_shares: List["SecretShare"] = field(
        init=False,
        metadata={
            "sa": relationship(
                "SecretShare",
                primaryjoin="foreign(SecretShare.sender_id) == RoundMember.id",
                back_populates="sender"
            )
        },
    )
    
    received_shares: List["SecretShare"] = field(
        init=False,
        metadata={
            "sa": relationship(
                "SecretShare",
                primaryjoin="foreign(SecretShare.receiver_id) == RoundMember.id",
                back_populates="receiver"
            )
        },
    )
