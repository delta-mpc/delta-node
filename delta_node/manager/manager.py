import logging
import os.path
import threading
from collections import defaultdict
from concurrent import futures
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

from delta import task as delta_task
from sqlalchemy.orm.session import Session
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

from .. import agg, channel, contract, model, node
from ..exceptions import *
from .location import task_cfg_file, task_weight_file
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

        self._metadata = model.TaskMetadata(
            task.name, task.type, task.secure_level, task.algorithm, self._members
        )

        self._node_id = node.get_node_id(session=session)

        self._round_cond = threading.Condition()
        round_id, round_status = self._round_status()
        self._round_id = round_id
        self._round_finished = round_status == model.RoundStatus.FINISHED

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
            _logger.info(f"member {member_id} join the task {self._task_id}")

    def finish_task(self, member_id: str, *, session: Session = None):
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        with self._round_cond:
            last_round_id, status = get_member_round_status(self._task_id, member_id, session=session)
            if status == model.RoundStatus.RUNNING:
                member_finish_round(self._task_id, member_id, last_round_id, session=session)
            if self._round_finished:
                finish_task(self._task_id)
                _logger.info(f"task {self._task_id} finished")

    def get_round_id(self, member_id: str, *, session: Session = None) -> int:
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        last_round, status = get_member_round_status(
            self._task_id, member_id, session=session
        )
        _logger.debug(
            f"task {self._task_id} member {member_id} round {last_round} status {status}"
        )
        with self._round_cond:
            if self._round_finished:
                _logger.debug("round finished")
                if status == model.RoundStatus.RUNNING:
                    # if member doesn't finish last round, finish it and start the new round
                    member_finish_round(
                        self._task_id, member_id, last_round, session=session
                    )
                    _logger.info(
                        f"task {self._task_id} member {member_id} finish round {last_round}"
                    )
                # new round
                round_id = contract.start_round(self._node_id, self._task_id)
                _logger.info(f"start new round {round_id}")
                assert last_round < round_id, f"last round {last_round}, new round {round_id}"
                self._round_id = round_id
                self._round_finished = False
                member_start_round(self._task_id, member_id, round_id, session=session)
                _logger.info(
                    f"task {self._task_id} member {member_id} start round {round_id}"
                )
                self._round_cond.notify_all()
                return round_id
            else:
                _logger.info("round unfinished")
                if last_round < self._round_id:
                    _logger.info
                    if status == model.RoundStatus.RUNNING:
                        # if member doesn't finish last round, finish it and start the new round
                        member_finish_round(
                            self._task_id, member_id, last_round, session=session
                        )
                        _logger.info(
                            f"task {self._task_id} member {member_id} finish round {last_round}"
                        )

                    # if member has finished last round, start the new round
                    member_start_round(
                        self._task_id, member_id, self._round_id, session=session
                    )
                    _logger.info(
                        f"task {self._task_id} member {member_id} start round {self._round_id}"
                    )
                    return self._round_id
                else:
                    if status == model.RoundStatus.RUNNING:
                        # member is running in the current round
                        _logger.info(
                            f"task {self._task_id} member {member_id} runs in round {self._round_id}"
                        )
                        return self._round_id
                    else:
                        # member finished current round, wait for current round to finish
                        _logger.info(
                            f"task {self._task_id} member {member_id} wait for next round"
                        )
                        self._round_cond.wait_for(lambda: last_round < self._round_id)
                        return self._round_id

    def _round_status(
        self, *, session: Session = None
    ) -> Tuple[int, model.RoundStatus]:
        result_round_id = 0
        result_status = model.RoundStatus.FINISHED
        for member_id in self._members:
            max_round_id, status = get_member_round_status(
                self._task_id, member_id, session=session
            )
            if result_round_id == 0:
                result_round_id = max_round_id
                result_status = status
            elif max_round_id < result_round_id:
                result_round_id = max_round_id
                result_status = status
            elif max_round_id == result_round_id:
                if status == model.RoundStatus.RUNNING:
                    result_status = status
        return result_round_id, result_status

    def _finish_round(self):
        with self._round_cond:
            self._round_finished = True
        for member_id in self._members:
            round_id, status = get_member_round_status(self._task_id, member_id)
            if status != model.RoundStatus.FINISHED:
                member_finish_round(self._task_id, member_id, round_id)

    def get_metadata(self, member_id: str) -> model.TaskMetadata:
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        return self._metadata

    def get_file(self, member_id: str, round_id: int, file_type: str) -> str:
        if self.has_joined_member(member_id):
            if file_type == "cfg":
                filename = task_cfg_file(self._task_id)
            elif file_type == "weight":
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
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        in_ch, out_ch = channel.new_channel_pair()
        master = False
        with self._agg_lock:
            if self._agg_group is None:
                self._agg_group = channel.ChannelGroup()
                _logger.info(
                    f"create agg group for task {self._task_id} round {self._round_id}"
                )
                master = True

        pool: Optional[futures.ThreadPoolExecutor] = None
        fut: Optional[futures.Future] = None
        if master:
            agg_method = agg.get_agg_method(self._metadata.secure_level)

            def agg_update(member_ids: List[str], group: channel.ChannelGroup):
                result = agg_method(member_ids, group)
                _logger.info(f"task {self._task_id} round {self._round_id} agg finished")
                try:
                    self._task_item.update(result)
                    weight_file = task_weight_file(self._task_id, self._round_id)
                    with open(weight_file, mode="wb") as f:
                        self._task_item.dump_weight(f)
                    _logger.info(f"task {self._task_id} round {self._round_id} update weight")
                except Exception as e:
                    _logger.error(e)

            pool = futures.ThreadPoolExecutor(1)
            fut = pool.submit(agg_update, self._joined_members, self._agg_group)

        self._agg_group.register(member_id, in_ch)
        _logger.debug(
            f"register {member_id} for agg of task {self._task_id} round {self._round_id}"
        )

        yield out_ch
        
        with self._round_cond:
            member_finish_round(self._task_id, member_id, self._round_id)
            if master:
                assert fut is not None
                assert pool is not None
                fut.result()
                pool.shutdown(True)
                _logger.debug("agg update finish")
                with self._agg_lock:
                    self._agg_group = None
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
        res = _task_manager_registry[task_id]
        return res
