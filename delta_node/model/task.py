import sqlalchemy as sa

from .. import db


class Task(db.Base):
    __tablename__ = "task"

    id = sa.Column(sa.Integer, primary_key=True)
    node_id = sa.Column(sa.String)  # creator of the task
    task_id = sa.Column(sa.Integer)
    type = sa.Column(sa.String)
    status = sa.Column(sa.Integer)  # 0: running 1: finished
    member_count = sa.Column(sa.Integer)  # 0 means unlimited member count
