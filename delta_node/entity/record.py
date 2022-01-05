from dataclasses import dataclass, field
from typing import Optional

import sqlalchemy as sa
from delta_node.db import mapper_registry

from .base import BaseTable

__all__ = ["Record"]


@mapper_registry.mapped
@dataclass
class Record(BaseTable):
    __tablename__ = "log_record"
    __sa_dataclass_metadata_key__ = "sa"

    level: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=True)}
    )
    message: str = field(
        metadata={"sa": sa.Column(sa.String, nullable=False, index=False)}
    )
    task_id: Optional[str] = field(
        default=None, metadata={"sa": sa.Column(sa.String, nullable=True, index=True)}
    )
    tx_hash: Optional[str] = field(
        default=None, metadata={"sa": sa.Column(sa.String, nullable=True, index=False)}
    )
