import sqlalchemy as sa

from .. import db


class Task(db.Base):
    __tablename__ = "task"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    creator = sa.Column(sa.Integer, nullable=False, index=True)  # creator node id
