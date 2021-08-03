import sqlalchemy as sa
from .. import db

from enum import IntEnum


class RoundStatus(IntEnum):
    FINISHED = 1
    RUNNING = 0


class Round(db.Base):
    __tablename__ = "round"

    id = sa.Column(sa.Integer, primary_key=True)
    task_id = sa.Column(sa.Integer)
    node_id = sa.Column(sa.String)
    round_id = sa.Column(sa.Integer)
    status = sa.Column(sa.Integer)
