from enum import IntEnum

import sqlalchemy as sa

from .. import db
from . import utils


class RoundStatus(IntEnum):
    FINISHED = 1
    RUNNING = 0


class Round(db.Base):
    __tablename__ = "round"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.Integer, default=utils.timestamp)
    task_id = sa.Column(sa.Integer, index=True)
    node_id = sa.Column(sa.String, index=True)
    round_id = sa.Column(sa.Integer, index=True)
    status = sa.Column(sa.Integer)
