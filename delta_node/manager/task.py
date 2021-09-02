from typing import List, Optional, Tuple

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from .. import db, model
from ..exceptions import *

__all__ = [
    "get_task",
    "join_task",
    "member_start_round",
    "get_member_round_status",
    "get_latest_rounds",
    "member_finish_round",
    "get_finished_round_member",
    "start_task",
    "finish_task",
    "get_member_round",
]


@db.with_session
def add_task(
    name: str,
    type: str,
    secure_level: int,
    algorithm: str,
    members: List[str],
    url: str,
    node_id: str,
    task_id: int,
    status: model.TaskStatus,
    *,
    session: Session = None,
):
    assert session is not None
    task = session.query(model.Task).filter(model.Task.task_id == task_id).first()
    if task is None:
        task = model.Task(
            name=name,
            type=type,
            secure_level=secure_level,
            algorithm=algorithm,
            member_count=len(members),
            url=url,
            node_id=node_id,
            task_id=task_id,
            status=status,
        )
        session.add(task)

        task_members = []
        for member_id in members:
            task_member = model.TaskMember(
                task_id=task_id, node_id=member_id, joined=False
            )
            task_members.append(task_member)
        session.bulk_save_objects(task_members)
        session.commit()
    else:
        task.status = status  # type: ignore
        session.commit()


@db.with_session
def get_task(task_id: int, *, session: Session = None) -> Optional[model.Task]:
    assert session is not None
    task = (
        session.query(model.Task)
        .options(joinedload("members"))
        .filter(model.Task.task_id == task_id)
        .one_or_none()
    )
    return task


@db.with_session
def join_task(task_id: int, member_id: str, *, session: Session = None):
    assert session is not None
    member = (
        session.query(model.TaskMember)
        .filter(model.TaskMember.task_id == task_id)
        .filter(model.TaskMember.node_id == member_id)
        .one_or_none()
    )
    if member is None:
        raise TaskNoMemberError(task_id, member_id)
    if not member.joined:
        member.joined = True  # type: ignore
        session.add(member)
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
def get_member_round_status(
    task_id: int, member_id: str, *, session: Session = None
) -> Tuple[int, model.RoundStatus]:
    assert session is not None
    round = (
        session.query(model.Round)
        .filter(model.Round.task_id == task_id)
        .filter(model.Round.node_id == member_id)
        .order_by(desc(model.Round.round_id))
        .first()
    )
    if round is None:
        return 0, model.RoundStatus.FINISHED
    else:
        return round.round_id, round.status  # type: ignore


@db.with_session
def get_latest_rounds(task_id: int, *, session: Session = None) -> List[model.Round]:
    assert session is not None
    latest_round = (
        session.query(model.Round)
        .filter(model.Round.task_id == task_id)
        .order_by(desc(model.Round.round_id))
        .first()
    )
    if latest_round is not None:
        rounds = (
            session.query(model.Round)
            .filter(model.Round.task_id == task_id)
            .filter(model.Round.round_id == latest_round.round_id)
            .all()
        )
        return rounds
    else:
        return []


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
def get_finished_round_member(
    task_id: int, round_id: int, *, session: Session = None
) -> List[str]:
    assert session is not None
    rounds = (
        session.query(model.Round)
        .filter(model.Round.task_id == task_id)
        .filter(model.Round.round_id == round_id)
        .filter(model.Round.status == model.RoundStatus.FINISHED)
        .all()
    )
    res = [r.node_id for r in rounds]
    return res


@db.with_session
def start_task(task_id: int, *, session: Session = None):
    assert session is not None
    task = session.query(model.Task).filter(model.Task.task_id == task_id).one_or_none()
    if task is None:
        raise NoSuchTaskError(task_id)
    task.status = model.TaskStatus.RUNNING  # type: ignore
    session.add(task)
    session.commit()


@db.with_session
def finish_task(task_id: int, *, session: Session = None):
    assert session is not None
    task = session.query(model.Task).filter(model.Task.task_id == task_id).one_or_none()
    if task is None:
        raise NoSuchTaskError(task_id)
    task.status = model.TaskStatus.FINISHED  # type: ignore
    session.add(task)
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
