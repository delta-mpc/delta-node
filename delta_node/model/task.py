import sqlalchemy as sa
from enum import IntEnum
from .. import db


class TaskStatus(IntEnum):
    INIT = 0
    RUNING = 2
    FINISHED = 3
    ERROR = 4


class Task(db.Base):
    __tablename__ = "task"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    type = sa.Column(sa.String)
    secure_level = sa.Column(sa.Integer)
    algorithm = sa.Column(sa.String)
    url = sa.Column(sa.String)
    member_count = sa.Column(sa.Integer)  # 0 means unlimited member count

    node_id = sa.Column(sa.String)  # creator of the task
    task_id = sa.Column(sa.Integer)
    status = sa.Column(sa.Integer)  # 0: initial  1: running  2: finished  4: error
