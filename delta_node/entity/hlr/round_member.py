from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from delta_node.db import mapper_registry
from sqlalchemy.orm import relationship

from ..base import BaseTable
from .task_round import RoundStatus

if TYPE_CHECKING:
    from .secret_share import SecretShare
    from .task_round import TaskRound

__all__ = ["RoundMember"]


@mapper_registry.mapped
@dataclass
class RoundMember(BaseTable):
    __tablename__ = "hlr_round_member"
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
                "delta_node.entity.hlr.task_round.TaskRound",
                primaryjoin="foreign(delta_node.entity.hlr.round_member.RoundMember.round_id) == delta_node.entity.hlr.task_round.TaskRound.id",
                back_populates="members",
            )
        },
    )

    send_shares: List["SecretShare"] = field(
        init=False,
        metadata={
            "sa": relationship(
                "delta_node.entity.hlr.secret_share.SecretShare",
                primaryjoin="foreign(delta_node.entity.hlr.secret_share.SecretShare.sender_id) == delta_node.entity.hlr.round_member.RoundMember.id",
                back_populates="sender"
            )
        },
    )
    
    received_shares: List["SecretShare"] = field(
        init=False,
        metadata={
            "sa": relationship(
                "delta_node.entity.hlr.secret_share.SecretShare",
                primaryjoin="foreign(delta_node.entity.hlr.secret_share.SecretShare.receiver_id) == delta_node.entity.hlr.round_member.RoundMember.id",
                back_populates="receiver"
            )
        },
    )
