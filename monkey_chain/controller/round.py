from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import db, model

round_router = APIRouter()


class RoundIn(BaseModel):
    task_id: int
    node_id: int


class RoundOut(BaseModel):
    round_id: int


@round_router.post("/round", response_model=RoundOut)
def start_round(round_in: RoundIn, session: Session = Depends(db.get_session)):
    # check if task exists
    task = session.query(model.Task) \
        .filter(model.Task.id == round_in.task_id) \
        .one_or_none()
    if task is None:
        raise HTTPException(400, f"task {round_in.task_id} not exists")
    if task.creator != round_in.node_id:
        raise HTTPException(403, f"Unauthorized. Only task creator can start a round")
    # create round
    r = model.Round(task_id=round_in.task_id)
    session.add(r)
    session.commit()
    session.refresh(r)
    round_out = RoundOut(round_id=r.id)
    return round_out
