import time
import shutil
import logging
import os.path
import threading
from collections import defaultdict
from concurrent import futures
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

from delta.serialize import load_task
from delta.task import HorizontolTask
import numpy as np
from sqlalchemy.orm.session import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .. import agg, channel, contract, model, node
from ..exceptions import *
from .location import task_cfg_file, task_result_file, task_weight_file
from .task import *

_logger = logging.getLogger(__name__)


class TaskManager(object):
    def __init__(self, task_id: int, *, session: Session = None) -> None:
        self._task_id = task_id
        task = get_task(task_id, session=session)
        if task is None:
            err = f"task {task_id} is not ready"
            _logger.error(err, extra={"task_id": task_id})
            raise TaskNotReadyError(task_id)

        self._task_status = task.status
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(task_id)

        cfg_file = task_cfg_file(task.task_id)
        self._task_item = load_task(cfg_file)
        assert self._task_item.type == "horizontol" and isinstance(self._task_item, HorizontolTask)
        self._alg = self._task_item.algorithm()

        latest_rounds = get_latest_rounds(task_id, session=session)
        self._round_id = 0
        self._round_status = model.RoundStatus.FINISHED
        self._joined_members = []
        
        if len(latest_rounds) > 0:
            self._round_id == latest_rounds[0].round_id
            if any(round.status == model.RoundStatus.FINISHED for round in latest_rounds):
                self._round_status = model.RoundStatus.FINISHED
            else:
                self._round_status = model.RoundStatus.RUNNING
                self._joined_members = [round.node_id for round in latest_rounds]
        
        self._join_lock = threading.Lock()
        self._join_event = threading.Event()
        self._in_join_phase = False        

        self._metadata = model.TaskMetadata(
            task.name, task.type, task.dataset
        )

        self._node_id = node.get_node_id(session=session)

        self._round_cond = threading.Condition()
        self._agg_lock = threading.Lock()
        self._agg_group: Optional[channel.ChannelGroup] = None


    def has_joined_member(self, member_id: str) -> bool:
        return member_id in self._joined_members

    def join(self, member_id: str, *, session: Session = None) -> bool:
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)
        if self._round_status == model.RoundStatus.FINISHED:
            raise TaskUnfinishedRoundError(self._task_id, self._round_id)

        if len(self._joined_members) > 0 and not self._in_join_phase:
            # not in join phase
            return False
        if len(self._joined_members) >= self._alg.max_clients:
            # reach max clients
            return False        
        
        def end_join_phase():
            with self._join_lock:
                if len(self._joined_members) >= self._alg.min_clients:
                    self._round_id = contract.start_round(self._node_id, self._task_id)
                    self._round_status = model.RoundStatus.RUNNING
                self._in_join_phase = False
                self._join_event.set()

        timer = None
        try:
            with self._join_lock:
                if len(self._joined_members) == 0:
                    # start the task
                    if self._task_status == model.TaskStatus.PENDING:
                        start_task(self._task_id, session=session)
                        self._task_status == model.TaskStatus.RUNNING

                    # start new join phase
                    self._in_join_phase = True
                    if self._alg.wait_timeout is not None:
                        timer = threading.Timer(self._alg.wait_timeout, end_join_phase)
                        timer.start()

                if member_id not in self._joined_members:
                    self._joined_members.append(member_id)

                if self._alg.wait_timeout is None and len(self._joined_members) >= self._alg.min_clients:
                    end_join_phase()

            if self._join_event.wait(self._alg.wait_timeout):
                self._join_event.clear()
                member_start_round(self._task_id, member_id, self._round_id, session=session)
                return True
            return False
        except Exception as e:
            _logger.exception(e)
            if timer is not None:
                timer.cancel()
            raise
        finally:
            if timer is not None:
                timer.join()


    def finish_task(self, member_id: str, *, session: Session = None):
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        with self._round_cond:
            last_round_id, status = get_member_round_status(
                self._task_id, member_id, session=session
            )
            if status == model.RoundStatus.RUNNING:
                member_finish_round(
                    self._task_id, member_id, last_round_id, session=session
                )
            if self._round_finished and not self._task_finished:
                finish_task(self._task_id)
                self._task_finished = True
                last_weight_file = task_weight_file(self._task_id, self._round_id)
                result_file = task_result_file(self._task_id)
                shutil.copyfile(last_weight_file, result_file)
                _logger.info(
                    f"task {self._task_id} finished", extra={"task_id": self._task_id}
                )

    def get_round_id(self, member_id: str, *, session: Session = None) -> int:
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        if self._task_finished:
            raise TaskFinishedError(self._task_id)

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
                _logger.info(
                    f"task {self._task_id} start new round {round_id}",
                    extra={"task_id": self._task_id},
                )
                assert (
                    last_round < round_id
                ), f"last round {last_round}, new round {round_id}"
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
                        self._round_cond.wait_for(
                            lambda: last_round < self._round_id or self._task_finished
                        )
                        if self._task_finished:
                            raise TaskFinishedError(self._task_id)
                        return self._round_id

    def get_metadata(self, member_id: str) -> model.TaskMetadata:
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        if self._task_finished:
            raise TaskFinishedError(self._task_id)

        start_task(self._task_id)
        return self._metadata

    def get_file(self, member_id: str, round_id: int, file_type: str) -> str:
        if self._task_finished:
            raise TaskFinishedError(self._task_id)
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
        if self._task_finished:
            raise TaskFinishedError(self._task_id)

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

            def agg_update(member_ids: List[str], group: channel.ChannelGroup):
                aggregator = agg.new_aggregator(
                    self._metadata.name, self._task_id
                )
                result = aggregator.aggregate(member_ids, group)
                try:
                    weight_file = task_weight_file(self._task_id, self._round_id)
                    with open(weight_file, mode="wb") as f:
                        np.savez_compressed(result)
                    _logger.info(
                        f"task {self._task_id} round {self._round_id} update weight",
                        extra={"task_id": self._task_id},
                    )
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
                with self._join_lock:
                    self._round_status = model.RoundStatus.FINISHED


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
        except TaskError as e:
            _logger.error(e)
            raise
        except Exception as e:
            _logger.exception(e)
            raise
        res = _task_manager_registry[task_id]
        return res
