from re import T
import sqlalchemy as sa
from .. import db


class TaskMember(db.Base):
    __tablename__ = "task_member"

    id = sa.Column(sa.Integer, primary_key=True)
    task_id = sa.Column(sa.Integer)
    node_id = sa.Column(sa.String)
    joined = sa.Column(sa.Boolean)
