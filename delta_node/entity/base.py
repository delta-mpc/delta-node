from datetime import datetime

from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass


__all__ = ["BaseMixin"]

BaseDatetime = DATETIME(
    storage_format="%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d",
    regexp=r"(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)",
)


class BaseMixin(MappedAsDataclass):
    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        BaseDatetime,
        init=False,
        default_factory=datetime.now,
        insert_default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        BaseDatetime,
        init=False,
        default_factory=datetime.now,
        onupdate=datetime.now,
        insert_default=datetime.now,
    )
