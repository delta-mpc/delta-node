from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import db, model

node_router = APIRouter()


class NodeIn(BaseModel):
    url: str


class NodeOut(BaseModel):
    id: str


@node_router.post("/node", response_model=NodeOut)
def register_node(node_in: NodeIn, session: Session = Depends(db.get_session)):
    # check if node exists
    q = session.query(model.Node).filter(model.Node.url == node_in.url)
    existed = session.query(q.exists()).scalar()
    if existed:
        raise HTTPException(400, "the node url has been registered")
    # create node
    node = model.Node(url=node_in.url)
    session.add(node)
    session.commit()
    session.refresh(node)
    node_out = NodeOut(id=str(node.id))
    return node_out
