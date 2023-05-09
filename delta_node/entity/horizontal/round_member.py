from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delta_node.db import Base

from ..base import BaseMixin
from .task_round import RoundStatus

if TYPE_CHECKING:
    from .secret_share import SecretShare
    from .task_round import TaskRound

__all__ = ["RoundMember"]


class RoundMember(Base, BaseMixin):
    __tablename__ = "round_member"

    round_id: Mapped[int] = mapped_column(index=True, nullable=False)
    address: Mapped[str] = mapped_column(index=True, nullable=False)
    status: Mapped[RoundStatus] = mapped_column(
        sa.Enum(RoundStatus), index=True, nullable=False
    )

    round: Mapped[Optional["TaskRound"]] = relationship(
        "delta_node.entity.horizontal.task_round.TaskRound",
        primaryjoin="foreign(delta_node.entity.horizontal.round_member.RoundMember.round_id) == delta_node.entity.horizontal.task_round.TaskRound.id",
        back_populates="members",
        init=False,
        default=None,
    )

    send_shares: Mapped[List["SecretShare"]] = relationship(
        "delta_node.entity.horizontal.secret_share.SecretShare",
        primaryjoin="foreign(delta_node.entity.horizontal.secret_share.SecretShare.sender_id) == delta_node.entity.horizontal.round_member.RoundMember.id",
        back_populates="sender",
        init=False,
        default_factory=list,
    )

    received_shares: Mapped[List["SecretShare"]] = relationship(
        "delta_node.entity.horizontal.secret_share.SecretShare",
        primaryjoin="foreign(delta_node.entity.horizontal.secret_share.SecretShare.receiver_id) == delta_node.entity.horizontal.round_member.RoundMember.id",
        back_populates="receiver",
        init=False,
        default_factory=list,
    )
