from sqlalchemy.orm import Mapped, mapped_column

from delta_node.db import Base

from ..base import BaseMixin

__all__ = ["Node"]


class Node(Base, BaseMixin):
    __tablename__ = "Node"

    url: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False, index=False)
    address: Mapped[str] = mapped_column(nullable=False, index=True)
