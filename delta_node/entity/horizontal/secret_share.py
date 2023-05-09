from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delta_node.db import Base

from ..base import BaseMixin

if TYPE_CHECKING:
    from .round_member import RoundMember

__all__ = ["SecretShareData", "SecretShare"]


@dataclass
class SecretShareData:
    sender: str
    receiver: str
    seed: bytes = b""
    seed_commitment: bytes = b""
    secret_key: bytes = b""
    secret_key_commitment: bytes = b""


class SecretShare(Base, BaseMixin):
    __tablename__ = "secret_share"

    sender_id: Mapped[int] = mapped_column(nullable=False, index=True)
    receiver_id: Mapped[int] = mapped_column(nullable=False, index=True)
    seed_share: Mapped[bytes] = mapped_column(sa.BINARY, nullable=False, index=False)
    sk_share: Mapped[bytes] = mapped_column(sa.BINARY, nullable=False, index=False)

    sender: Mapped["RoundMember"] = relationship(
        "delta_node.entity.horizontal.round_member.RoundMember",
        primaryjoin="foreign(delta_node.entity.horizontal.secret_share.SecretShare.sender_id) == delta_node.entity.horizontal.round_member.RoundMember.id",
        back_populates="send_shares",
        init=False,
    )

    receiver: Mapped["RoundMember"] = relationship(
        "delta_node.entity.horizontal.round_member.RoundMember",
        primaryjoin="foreign(delta_node.entity.horizontal.secret_share.SecretShare.receiver_id) == delta_node.entity.horizontal.round_member.RoundMember.id",
        back_populates="received_shares",
        init=False,
    )
