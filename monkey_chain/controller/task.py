from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import db, model

task_router = APIRouter()


class TaskIn(BaseModel):
    creator: int
    name: str


class TaskOut(BaseModel):
    id: int


@task_router.post("/task", response_model=TaskOut)
def create_task(task_in: TaskIn, session: Session = Depends(db.get_session)):
    # check if creator exist
    q = session.query(model.Node).filter(model.Node.id == task_in.creator)
    existed = session.query(q.exists()).scalar()
    if not existed:
        raise HTTPException(400, f"creator {task_in.creator} not exists")

    # create task
    task = model.Task(name=task_in.name, creator=task_in.creator)
    session.add(task)
    session.commit()
    session.refresh(task)

    task_out = TaskOut(id=task.id)
    return task_out
