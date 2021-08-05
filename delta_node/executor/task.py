from sqlalchemy.orm import Session
from .. import db, model
from ..exceptions import *


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
            secure_level=metadata.secure_level,
            algorithm=metadata.algorithm,
            member_count=len(metadata.members),
            url=url,
            node_id=creator_id,
            task_id=task_id,
            status=model.TaskStatus.RUNNING,
        )
        session.add(task)

        task_members = []
        for member_id in metadata.members:
            task_member = model.TaskMember(
                task_id=task_id, node_id=member_id, joined=False
            )
            task_members.append(task_member)
        session.bulk_save_objects(task_members)
        session.commit()


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
