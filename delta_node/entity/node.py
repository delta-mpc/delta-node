from typing import Optional, TYPE_CHECKING
from .base import BaseTable
import sqlalchemy as sa
from dataclasses import dataclass, field
from delta_node.db import mapper_registry


__all__ = ["Node"]


@mapper_registry.mapped
@dataclass
class Node(BaseTable):
    __tablename__ = "Node"
    __sa_dataclass_metadata_key__ = "sa"

    url: str = field(metadata={"sa": sa.Column(sa.String, nullable=False, index=True)})
    name: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=False)}
    )
    address: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=True)}
    )
