import sqlalchemy as sa

from .. import db


class Round(db.Base):
    __tablename__ = "round"

    id = sa.Column(sa.Integer, primary_key=True)
    task_id = sa.Column(sa.Integer, index=True, nullable=False)
