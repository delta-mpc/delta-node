from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa

__all__ = ["BaseTable"]


@dataclass
class BaseTable:
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(
        init=False,
        metadata={"sa": sa.Column(sa.Integer, primary_key=True, autoincrement=True)},
    )
    created_at: datetime = field(
        init=False,
        metadata={
            "sa": sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
        },
    )
    updated_at: Optional[datetime] = field(
        init=False,
        metadata={
            "sa": sa.Column(
                sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now()
            )
        },
    )
