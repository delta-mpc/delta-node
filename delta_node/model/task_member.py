import sqlalchemy as sa
from .. import db
from . import utils


class TaskMember(db.Base):
    __tablename__ = "task_member"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.Integer, default=utils.timestamp)
    task_id = sa.Column(sa.Integer, index=True)
    node_id = sa.Column(sa.String)
    joined = sa.Column(sa.Boolean)
