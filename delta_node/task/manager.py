from collections import defaultdict

from sqlalchemy.orm.session import Session
from delta_node import contract
import logging
from typing import Dict, List

from .. import config, node, model
from .location import task_cfg_file, task_weight_file, task_result_file
from .task import *
from .exceptions import *

_logger = logging.getLogger(__name__)


class TaskManager(object):
    def __init__(self, task_id: int, *, session: Session = None) -> None:
        self._task_id = task_id
        task = get_task(task_id, session=session)
        if task is None:
            err = f"task {task_id} is not ready"
            _logger.error(err)
            raise TaskNotReadyError(task_id)
        member_ids = [member.node_id for member in task.members]
        self._members = member_ids
        self._joined_members = []

        self._node_id = node.get_node_id(session=session)

        self._round_id = 0
        self._round_finished = False

    def has_member(self, member_id: str) -> bool:
        return member_id in self._members

    def join(self, member_id: str, *, session: Session = None):
        if member_id not in self._members:
            raise TaskNoMemberError(self._task_id, member_id)
        if member_id not in self._joined_members:
            join_task(self._task_id, member_id, session=session)
            self._joined_members.append(member_id)
            contract.join_task(member_id, self._task_id)
        
    def start_round(self, member_id: str, *, session: Session = None) -> int:
        if self._round_id == 0 or self._round_finished:
            # the first round or last round is finished, start a new round
            round_id = contract.start_round(self._node_id, self._task_id)
            self._round_id = round_id
            member_start_round(self._task_id, member_id, round_id, session=session)
            return self._round_id
        else:
            # current round is not finished
            round_id, status = get_member_round_status(self._task_id, member_id, session=session)
            if status == model.RoundStatus.RUNNING:
                # return running round id
                return round_id
            elif round_id < self._round_id:
                # start new round for member who finished last round 
                member_start_round(self._task_id, member_id, self._round_id, session=session)
                return self._round_id
            else:
                # member who finished current round
                # cannot start new round until current round is finished
                raise TaskUnfinishedRoundError(self._task_id, self._round_id)
    
    def round_status(self, member_id: str, round_id: int, *, session: Session = None) -> model.RoundStatus:
        max_round_id, status = get_member_round_status(self._task_id, member_id, session=session)        
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
        members = get_finished_round_member(self._task_id, self._round_id, session=session)
        if len(members) == len(self._members):
            self._round_finished = True
