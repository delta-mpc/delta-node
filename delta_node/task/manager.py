import logging
import os.path
import threading
from collections import defaultdict
from concurrent import futures
from contextlib import contextmanager
from typing import Dict, Optional

from delta import task as delta_task
from sqlalchemy.orm.session import Session
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

from .. import agg, channel, contract, model, node
from .exceptions import *
from .location import task_cfg_file, task_weight_file
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

        self._agg_lock = threading.Lock()
        self._agg_group: Optional[channel.ChannelGroup] = None

        cfg_file = task_cfg_file(task_id)
        with open(cfg_file, mode="rb") as f:
            self._task_item = delta_task.load(f)

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

    def _finish_member_round(
        self, member_id: str, round_id: int, *, session: Session = None
    ):
        member_finish_round(self._task_id, member_id, round_id, session=session)

    def _finish_round(self):
        with self._round_cond:
            self._round_finished = True

    def get_metadata(self, member_id: str) -> TaskMetadata:
        self.join(member_id)
        return self._metadata

    def get_file(self, member_id: str, file_type: str) -> str:
        if self.has_joined_member(member_id):
            if file_type == "cfg":
                filename = task_cfg_file(self._task_id)
            elif file_type == "weight":
                round_id = self.start_new_round(member_id)
                filename = task_weight_file(self._task_id, round_id)
            else:
                raise TaskUnknownFileTypeError(self._task_id, file_type)
            if os.path.exists(filename):
                return filename
            else:
                raise TaskFileNotExistedError(self._task_id, filename)
        else:
            raise MemberNotJoinedError(self._task_id, member_id)

    @contextmanager
    def aggregate(self, member_id: str):
        in_ch, out_ch = channel.new_channel_pair()
        master = False
        with self._agg_lock:
            if self._agg_group is None:
                self._agg_group = channel.ChannelGroup()
                master = True

        self._agg_group.register(member_id, in_ch)
        pool: Optional[futures.ThreadPoolExecutor] = None
        fut: Optional[futures.Future] = None
        if master:
            agg_method = agg.get_agg_method(self._metadata.secure_level)
            pool = futures.ThreadPoolExecutor(1)
            fut = pool.submit(agg_method, self._joined_members, self._agg_group)

        yield out_ch

        self._finish_member_round(member_id, self._round_id)
        if master:
            assert fut is not None
            assert pool is not None
            result = fut.result()
            pool.shutdown(True)
            self._task_item.update(result)
            weight_file = task_weight_file(self._task_id, self._round_id)
            with open(weight_file, mode="wb") as f:
                self._task_item.dump_weight(f)
            self._finish_round()


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
