from dataclasses import dataclass
from enum import IntEnum
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .. import db
from . import utils


class TaskStatus(IntEnum):
    INIT = 0
    RUNNING = 1
    FINISHED = 2
    ERROR = 3


class Task(db.Base):
    __tablename__ = "task"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.Integer, default=utils.timestamp)

    name = sa.Column(sa.String)
    type = sa.Column(sa.String)
    secure_level = sa.Column(sa.Integer)
    algorithm = sa.Column(sa.String)
    url = sa.Column(sa.String)
    member_count = sa.Column(sa.Integer)  # 0 means unlimited member count

    node_id = sa.Column(sa.String, index=True)  # creator of the task
    task_id = sa.Column(sa.Integer, index=True)
    status = sa.Column(sa.Integer)  # 0: initial  1: running  2: finished  4: error

    members = relationship(
        "TaskMember", primaryjoin="foreign(TaskMember.task_id) == Task.task_id"
    )


@dataclass
class TaskMetadata(object):
    name: str
    type: str
    secure_level: int
    algorithm: str
    members: List[str]
