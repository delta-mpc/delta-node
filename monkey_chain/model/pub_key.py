import sqlalchemy as sa

from .. import db


class PubKey(db.Base):
    __tablename__ = "pub_key"

    id = sa.Column(sa.Integer, primary_key=True)
    task_id = sa.Column(sa.Integer, index=True, nullable=False)
    round_id = sa.Column(sa.Integer, index=True, nullable=False)
    node_id = sa.Column(sa.Integer, index=True, nullable=False)
    key = sa.Column(sa.String, index=True, nullable=False)
