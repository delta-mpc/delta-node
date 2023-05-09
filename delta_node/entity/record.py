from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from delta_node.db import Base

from .base import BaseMixin

__all__ = ["Record"]


class Record(Base, BaseMixin):
    __tablename__ = "log_record"

    level: Mapped[str] = mapped_column(nullable=False, index=True)
    message: Mapped[str] = mapped_column(nullable=False, index=False)
    task_id: Mapped[Optional[str]] = mapped_column(
        nullable=True, index=True, default=None
    )
    tx_hash: Mapped[Optional[str]] = mapped_column(
        nullable=True, index=False, default=None
    )
