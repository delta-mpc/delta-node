from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import db, model

pub_key_router = APIRouter()


class PubKeyIn(BaseModel):
    task_id: int
    round_id: int
    node_id: int
    pub_key: str


class PubKeyOut(BaseModel):
    status: str


@pub_key_router.post("/pub_key", response_model=PubKeyOut)
def upload_pub_key(pub_key_in: PubKeyIn, session: Session = Depends(db.get_session)):
    # check if node is a member of the task
    member = session.query(model.TaskMember) \
        .filter(model.TaskMember.task_id == pub_key_in.task_id) \
        .filter(model.TaskMember.member_id == pub_key_in.node_id) \
        .one_or_none()

    # check if round exists
    r = session.query(model.Round).filter(model.Round.id == pub_key_in.round_id).one_or_none()
    if r is None:
        raise HTTPException(400, f"round {pub_key_in.round_id} not exists")
    if r.task_id != pub_key_in.task_id:
        raise HTTPException(400, f"round {pub_key_in.round_id} not belongs to task {pub_key_in.task_id}")

    if member is None:
        raise HTTPException(400, f"{pub_key_in.node_id} is not in task {pub_key_in.task_id}'s member list")

    pub_key = model.PubKey(task_id=pub_key_in.task_id, round_id=pub_key_in.round_id, node_id=pub_key_in.node_id,
                           key=pub_key_in.pub_key)
    session.add(pub_key)
    session.commit()
    return PubKeyOut(status="ok")
