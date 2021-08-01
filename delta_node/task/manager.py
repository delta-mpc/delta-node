import logging
import threading
from collections import defaultdict
from typing import Dict, List

from delta_node import contract
from sqlalchemy.orm.session import Session
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

from .. import config, model, node
from .exceptions import *
from .metadata import TaskMetadata
from .task import *

_logger = logging.getLogger(__name__)


class TaskManager(object):
    def __init__(self, task_id: int, *, session: Session = None) -> None:
        self._task_id = task_id
        task = get_task(task_id, session=session)
        if task is None:
            err = f"task {task_id} is not ready"
            _logger.error(err)
            raise TaskNotReadyError(task_id)
        self._members = [member.node_id for member in task.members]
        self._joined_members = [
            member.node_id for member in task.members if member.joined
        ]

        self._metadata = TaskMetadata(
            task.name, task.type, task.secure_level, task.algorithm, self._members
        )

        self._node_id = node.get_node_id(session=session)

        self._round_cond = threading.Condition()
        self._round_id = 0
        self._round_finished = False

    @property
    def task_metadata(self) -> TaskMetadata:
        return self._metadata

    def has_member(self, member_id: str) -> bool:
        return member_id in self._members

    def has_joined_member(self, member_id: str) -> bool:
        return member_id in self._joined_members

    def join(self, member_id: str, *, session: Session = None):
        if member_id not in self._members:
            raise TaskNoMemberError(self._task_id, member_id)
        if member_id not in self._joined_members:
            join_task(self._task_id, member_id, session=session)
            self._joined_members.append(member_id)
            contract.join_task(member_id, self._task_id)

    def start_new_round(self, member_id: str, *, session: Session = None) -> int:
        last_round, status = get_member_round_status(
            self._task_id, member_id, session=session
        )
        with self._round_cond:
            if self._round_finished:
                if status == model.RoundStatus.RUNNING:
                    # if member doesn't finish last round, finish it and start the new round
                    member_finish_round(
                        self._task_id, member_id, last_round, session=session
                    )
                # new round
                round_id = contract.start_round(self._node_id, self._task_id)
                assert last_round < round_id
                self._round_id = round_id
                self._round_finished = False
                member_start_round(self._task_id, member_id, round_id, session=session)
                self._round_cond.notify_all()
                return round_id
            else:
                if last_round < self._round_id:
                    if status == model.RoundStatus.RUNNING:
                        # if member doesn't finish last round, finish it and start the new round
                        member_finish_round(
                            self._task_id, member_id, last_round, session=session
                        )
                    # if member has finished last round, start the new round
                    member_start_round(
                        self._task_id, member_id, self._round_id, session=session
                    )
                    return self._round_id
                else:
                    if status == model.RoundStatus.RUNNING:
                        # member is running in the current round
                        return self._round_id
                    else:
                        # member finished current round, wait for current round to finish
                        self._round_cond.wait_for(lambda: last_round < self._round_id)
                        return self._round_id

    def start_round(self, member_id: str, *, session: Session = None) -> int:
        if self._round_id == 0 or self._round_finished:
            # the first round or last round is finished, start a new round
            round_id = contract.start_round(self._node_id, self._task_id)
            self._round_id = round_id
            member_start_round(self._task_id, member_id, round_id, session=session)
            return self._round_id
        else:
            # current round is not finished
            round_id, status = get_member_round_status(
                self._task_id, member_id, session=session
            )
            if status == model.RoundStatus.RUNNING:
                # return running round id
                return round_id
            elif round_id < self._round_id:
                # start new round for member who finished last round
                member_start_round(
                    self._task_id, member_id, self._round_id, session=session
                )
                return self._round_id
            else:
                # member who finished current round
                # cannot start new round until current round is finished
                raise TaskUnfinishedRoundError(self._task_id, self._round_id)

    def round_status(
        self, member_id: str, round_id: int, *, session: Session = None
    ) -> model.RoundStatus:
        max_round_id, status = get_member_round_status(
            self._task_id, member_id, session=session
        )
        if round_id == max_round_id:
            return status
        elif round_id < max_round_id:
            return model.RoundStatus.FINISHED
        else:
            raise TaskNoSuchRoundError(self._task_id, member_id, round_id)

    def finish_round(self, member_id: str, round_id: int, *, session: Session = None):
        member_finish_round(self._task_id, member_id, round_id, session=session)
        self._update_round_finished(session=session)

    def _update_round_finished(self, *, session: Session = None):
        members = get_finished_round_member(
            self._task_id, self._round_id, session=session
        )
        if len(members) == len(self._members):
            self._round_finished = True


_task_manager_registry: Dict[int, TaskManager] = {}
_task_manager_lock: Dict[int, threading.Lock] = defaultdict(threading.Lock)


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TaskNotReadyError),
    reraise=True,
)
def _new_task_manager(task_id: int, *, session: Session = None):
    return TaskManager(task_id=task_id, session=session)


def get_task_manager(task_id: int, *, session: Session = None) -> TaskManager:
    lock = _task_manager_lock[task_id]
    with lock:
        try:
            if task_id not in _task_manager_registry:
                manager = _new_task_manager(task_id, session=session)
                _task_manager_registry[task_id] = manager
        except TaskError:
            raise NoSuchTaskError(task_id)
        return _task_manager_registry[task_id]
