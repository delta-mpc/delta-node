from delta_node.data import dataset
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import desc
from .. import db, model
from ..exceptions import *
from typing import Tuple

@db.with_session
def _task_existed(task_id: int, *, session: Session = None):
    assert session is not None
    task = session.query(model.Task).filter(model.Task.task_id == task_id).first()
    return task is not None


@db.with_session
def add_task(
    task_id: int,
    url: str,
    creator_id: str,
    metadata: model.TaskMetadata,
    *,
    session: Session = None
):
    assert session is not None
    if not _task_existed(task_id, session=session):
        task = model.Task(
            name=metadata.name,
            type=metadata.type,
            dataset=metadata.dataset,
            url=url,
            node_id=creator_id,
            task_id=task_id,
            status=model.TaskStatus.RUNNING,
        )
        session.add(task)
        session.commit()


@db.with_session
def member_start_round(
    task_id: int, member_id: str, round_id: int, *, session: Session = None
):
    assert session is not None
    round = (
        session.query(model.Round)
        .filter(model.Round.task_id == task_id)
        .filter(model.Round.node_id == member_id)
        .filter(model.Round.round_id == round_id)
        .first()
    )
    if round is None:
        round = model.Round(
            task_id=task_id,
            node_id=member_id,
            round_id=round_id,
            status=model.RoundStatus.RUNNING,
        )
        session.add(round)
        session.commit()


@db.with_session
def member_finish_round(
    task_id: int, member_id: str, round_id: int, *, session: Session = None
):
    assert session is not None
    round = (
        session.query(model.Round)
        .filter(model.Round.task_id == task_id)
        .filter(model.Round.node_id == member_id)
        .filter(model.Round.round_id == round_id)
        .one()
    )
    round.status = model.RoundStatus.FINISHED  # type: ignore
    session.commit()


@db.with_session
def get_member_round(
    task_id: int, member_id: str, *, session: Session = None
) -> model.Round:
    assert session is not None
    round = (
        session.query(model.Round)
        .filter(model.Round.task_id == task_id)
        .filter(model.Round.node_id == member_id)
        .one_or_none()
    )
    if round is None:
        return model.Round(
            task_id=task_id,
            node_id=member_id,
            round_id=0,
            status=model.RoundStatus.FINISHED,
        )
    return round
