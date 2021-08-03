from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import db, model

event_router = APIRouter()


class Event(BaseModel):
    event_id: int
    name: str = ""
    address: str = ""
    url: str = ""
    task_id: int = 0
    epoch: int = 0
    key: str = ""


@event_router.get("/create_task", response_model=List[Event])
def get_create_task_events(
    start: int = 1,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(db.get_session),
):
    """
    get create task events
    :param start: start event id
    :param page:
    :param page_size:
    :param session:
    :return:
    """
    task_nodes = (
        session.query(model.Task, model.Node)
        .join(model.Node, model.Node.id == model.Task.creator)
        .filter(model.Task.id >= start)
        .order_by(model.Task.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    events = []
    for t, n in task_nodes:
        event = Event(
            address=str(n.id), url=n.url, task_id=t.id, name="Task", event_id=t.id
        )
        events.append(event)
    return events


@event_router.get("/join_task", response_model=List[Event])
def get_join_task_events(
    start: int = 1,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(db.get_session),
):
    """
    get join task events
    :param start: start event id
    :param page:
    :param page_size:
    :param session:
    :return:
    """
    member_nodes = (
        session.query(model.TaskMember, model.Node)
        .join(model.Node, model.TaskMember.member_id == model.Node.id)
        .filter(model.TaskMember.id >= start)
        .order_by(model.TaskMember.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    events = []
    for m, n in member_nodes:
        event = Event(
            address=str(n.id), url=n.url, task_id=m.task_id, name="Join", event_id=m.id
        )
        events.append(event)

    return events


@event_router.get("/start_round", response_model=List[Event])
def get_start_round_events(
    start: int = 1,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(db.get_session),
):
    """
    get start round events
    :param start: start event id
    :param page:
    :param page_size:
    :param session:
    :return:
    """
    rounds = (
        session.query(model.Round)
        .filter(model.Round.id >= start)
        .order_by(model.Round.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    events = []
    for r in rounds:
        event = Event(task_id=r.task_id, epoch=r.id, name="Train", event_id=r.id)
        events.append(event)

    return events


@event_router.get("/pub_key", response_model=List[Event])
def get_pub_key_events(
    start: int = 1,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(db.get_session),
):
    """
    get pub key events
    :param start: start event id
    :param page:
    :param page_size:
    :param session:
    :return:
    """
    keys = (
        session.query(model.PubKey)
        .filter(model.PubKey.id >= start)
        .order_by(model.PubKey.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    events = []
    for k in keys:
        event = Event(
            address=k.node_id,
            task_id=k.task_id,
            epoch=k.round_id,
            key=k.key,
            name="PublicKey",
            event_id=k.id,
        )
        events.append(event)

    return events
