import sqlalchemy as sa

from .. import db


class Node(db.Base):
    __tablename__ = "node"

    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.String, index=True, nullable=False)
