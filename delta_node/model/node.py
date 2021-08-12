import sqlalchemy as sa

from .. import db
from . import utils


class Node(db.Base):
    __tablename__ = "node"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.Integer, default=utils.timestamp)
    url = sa.Column(sa.String)
    node_id = sa.Column(sa.String, index=True)
