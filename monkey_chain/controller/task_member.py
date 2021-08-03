from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import db, model

task_member_router = APIRouter()


class TaskMemberIn(BaseModel):
    node_id: int
    task_id: int


class TaskMemberOut(BaseModel):
    status: str


@task_member_router.post("/task_member", response_model=TaskMemberOut)
def join_task(task_member_in: TaskMemberIn, session: Session = Depends(db.get_session)):
    # check if node existed
    q = session.query(model.Node).filter(model.Node.id == task_member_in.node_id)
    existed = session.query(q.exists()).scalar()
    if not existed:
        raise HTTPException(400, f"node {task_member_in.node_id} not exists")
    # check if node is a member of the task
    q = session.query(model.TaskMember) \
        .filter(model.TaskMember.task_id == task_member_in.task_id) \
        .filter(model.TaskMember.member_id == task_member_in.node_id)
    existed = session.query(q.exists()).scalar()
    if existed:
        raise HTTPException(400, "the node has already participate in the task")
    # change member status
    member = model.TaskMember(task_id=task_member_in.task_id, member_id=task_member_in.node_id)
    session.add(member)
    session.commit()
    session.refresh(member)

    return TaskMemberOut(status="ok")
