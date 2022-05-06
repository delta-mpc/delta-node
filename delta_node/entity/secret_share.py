from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import sqlalchemy as sa
from delta_node.db import mapper_registry
from sqlalchemy.orm import relationship

from .base import BaseTable

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


@mapper_registry.mapped
@dataclass
class SecretShare(BaseTable):
    __tablename__ = "secret_share"
    __sa_dataclass_metadata_key__ = "sa"

    sender_id: int = field(
        metadata={"sa": sa.Column(sa.Integer, nullable=False, index=True)}
    )
    receiver_id: int = field(
        metadata={"sa": sa.Column(sa.Integer, nullable=False, index=True)}
    )
    seed_share: bytes = field(
        metadata={"sa": sa.Column(sa.BINARY, nullable=False, index=False)}
    )
    sk_share: bytes = field(
        metadata={"sa": sa.Column(sa.BINARY, nullable=False, index=False)}
    )

    sender: "RoundMember" = field(
        init=False,
        metadata={
            "sa": relationship(
                "RoundMember",
                primaryjoin="foreign(SecretShare.sender_id) == RoundMember.id",
                back_populates="send_shares"
            )
        },
    )

    receiver: "RoundMember" = field(
        init=False,
        metadata={
            "sa": relationship(
                "RoundMember",
                primaryjoin="foreign(SecretShare.receiver_id) == RoundMember.id",
                back_populates="received_shares"
            )
        },
    )
