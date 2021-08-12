import sqlalchemy as sa

from .. import db


class Log(db.Base):
    __tablename__ = "Log"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.Integer)
    level = sa.Column(sa.String)
    task_id = sa.Column(sa.Integer)
    message = sa.Column(sa.String)
