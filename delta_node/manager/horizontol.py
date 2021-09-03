import logging
import os.path
import shutil
import threading
from concurrent import futures
from contextlib import contextmanager
from typing import Generator, List, Optional

from delta.serialize import load_task
from delta.task import HorizontolTask
from sqlalchemy.orm.session import Session

from .. import algorithm, channel, contract, model, node, serialize
from ..exceptions import *
from .base import TaskManager
from .location import task_cfg_file, task_result_file, task_weight_file, task_metrics_file
from .task import (
    get_member_round,
    member_start_round,
    member_finish_round,
    get_latest_rounds,
    start_task,
    finish_task,
    get_task,
)

_logger = logging.getLogger(__name__)


class HorizontolTaskManager(TaskManager):
    def __init__(self, task: model.Task, *, session: Session = None) -> None:
        super().__init__(task, session=session)

        assert self._task_item.type == "horizontol" and isinstance(self._task_item, HorizontolTask)
        self._alg = self._task_item.algorithm()

        latest_rounds = get_latest_rounds(self._task_id, session=session)
        self._round_id = 0
        self._round_status = model.RoundStatus.FINISHED
        self._joined_members = []
        # used for aggregate metrics, aggregate metrics should be called after aggregate result,
        # and joined members will be cleared in aggregate result
        self._last_joined_members = []  

        if len(latest_rounds) > 0:
            self._round_id == latest_rounds[0].round_id
            if any(
                round.status == model.RoundStatus.FINISHED for round in latest_rounds
            ):
                self._round_status = model.RoundStatus.FINISHED
            else:
                self._round_status = model.RoundStatus.RUNNING
                self._joined_members = [round.node_id for round in latest_rounds]

        self._lock = threading.Lock()

        self._join_event = threading.Event()
        self._in_join_phase = False

        self._metadata = model.TaskMetadata(task.name, task.type, task.dataset)

        self._node_id = node.get_node_id(session=session)

        self._agg_result_group: Optional[channel.ChannelGroup] = None
        self._agg_metrics_group: Optional[channel.ChannelGroup] = None

    def join(self, member_id: str, *, session: Session = None) -> bool:
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)
        if self._round_status != model.RoundStatus.FINISHED:
            raise TaskRoundNotFinishedError(self._task_id, self._round_id)

        if len(self._joined_members) > 0 and not self._in_join_phase:
            # not in join phase
            return False
        if len(self._joined_members) >= self._alg.max_clients:
            # reach max clients
            return False

        def end_join_phase():
            with self._lock:
                if len(self._joined_members) >= self._alg.min_clients:
                    self._round_id = contract.start_round(self._node_id, self._task_id)
                    self._round_status = model.RoundStatus.RUNNING
                self._in_join_phase = False
                self._join_event.set()

        timer = None
        try:
            with self._lock:
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

            if (
                self._alg.wait_timeout is None
                and len(self._joined_members) >= self._alg.min_clients
            ):
                end_join_phase()

            if self._join_event.wait(self._alg.wait_timeout):
                self._join_event.clear()
                member_start_round(
                    self._task_id, member_id, self._round_id, session=session
                )
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
        if self._round_status != model.RoundStatus.FINISHED:
            raise TaskRoundNotFinishedError(self._task_id, self._round_id)

        member_round = get_member_round(self._task_id, member_id, session=session)
        if member_round.status == model.RoundStatus.RUNNING:
            member_finish_round(
                self._task_id, member_id, member_round.round_id, session=session
            )

        with self._lock:
            if self._task_status != model.TaskStatus.FINISHED:
                finish_task(self._task_id)
                self._task_status = model.TaskStatus.FINISHED
                last_weight_file = task_weight_file(self._task_id, self._round_id)
                result_file = task_result_file(self._task_id)
                shutil.copyfile(last_weight_file, result_file)
                _logger.info(
                    f"task {self._task_id} finished", extra={"task_id": self._task_id}
                )

    def get_round_id(self, member_id: str, *, session: Session = None) -> int:
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)
        if self._round_status != model.RoundStatus.RUNNING:
            raise TaskRoundNotStartedError(self._task_id)

        return self._round_id

    def get_metadata(self, member_id: str) -> model.TaskMetadata:
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)

        return self._metadata

    def get_file(self, member_id: str, file_type: str) -> str:
        if file_type == "cfg":
            filename = task_cfg_file(self._task_id)
        elif file_type == "weight":
            if member_id not in self._joined_members:
                raise MemberNotJoinedError(self._task_id, member_id)
            if self._task_status == model.TaskStatus.FINISHED:
                raise TaskFinishedError(self._task_id)
            if self._round_status != model.RoundStatus.RUNNING:
                raise TaskRoundNotStartedError(self._task_id)

            filename = task_weight_file(self._task_id, self._round_id - 1)
        else:
            raise TaskUnknownFileTypeError(self._task_id, file_type)
        if os.path.exists(filename):
            return filename
        else:
            raise TaskFileNotExistedError(self._task_id, filename)

    @contextmanager
    def aggregate_result(self, member_id: str, extra_msg: bytes):
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)
        if self._round_status != model.RoundStatus.RUNNING:
            raise TaskRoundNotStartedError(self._task_id)

        in_ch, out_ch = channel.new_channel_pair()
        master = False
        with self._lock:
            if self._agg_result_group is None:
                self._agg_result_group = channel.ChannelGroup()
                _logger.info(
                    f"create agg group for task {self._task_id} round {self._round_id}"
                )
                master = True

        pool: Optional[futures.ThreadPoolExecutor] = None
        fut: Optional[futures.Future] = None
        if master:

            def agg_update(member_ids: List[str], group: channel.ChannelGroup):
                alg = algorithm.new_algorithm(self._alg.name, self._task_id, self._alg.connnection_timeout)
                result = alg.aggregate_result(member_ids, group, extra_msg)
                try:
                    weight_file = task_weight_file(self._task_id, self._round_id)
                    serialize.dump_arr(weight_file, result)
                    _logger.info(
                        f"task {self._task_id} round {self._round_id} update weight",
                        extra={"task_id": self._task_id},
                    )
                except Exception as e:
                    _logger.error(e)

            pool = futures.ThreadPoolExecutor(1)
            fut = pool.submit(agg_update, self._joined_members, self._agg_result_group)

        self._agg_result_group.register(member_id, in_ch)
        _logger.debug(
            f"register {member_id} for agg of task {self._task_id} round {self._round_id}"
        )

        yield out_ch

        member_finish_round(self._task_id, member_id, self._round_id)
        if master:
            assert fut is not None
            assert pool is not None
            fut.result()
            pool.shutdown(True)
            _logger.debug("agg update finish")
            with self._lock:
                self._agg_result_group = None
                self._round_status = model.RoundStatus.FINISHED
                self._last_joined_members = self._joined_members.copy()
                self._joined_members = []

    @contextmanager
    def aggregate_metrics(self, member_id: str, extra_msg: bytes) -> Generator[channel.OuterChannel, None, None]:
        if member_id not in self._joined_members:
            raise MemberNotJoinedError(self._task_id, member_id)
        if self._task_status == model.TaskStatus.FINISHED:
            raise TaskFinishedError(self._task_id)

        in_ch, out_ch = channel.new_channel_pair()
        master = False
        with self._lock:
            if self._agg_metrics_group is None:
                self._agg_metrics_group = channel.ChannelGroup()
                _logger.info(
                    f"create agg group for task {self._task_id} round {self._round_id}"
                )
                master = True

        pool: Optional[futures.ThreadPoolExecutor] = None
        fut: Optional[futures.Future] = None
        if master:

            def agg_update(member_ids: List[str], group: channel.ChannelGroup):
                alg = algorithm.new_algorithm(self._alg.name, self._task_id, self._alg.connnection_timeout)
                metrics = alg.aggregate_metrics(member_ids, group, extra_msg)
                try:
                    metrics_file = task_metrics_file(self._task_id, self._round_id)
                    serialize.dump_metrics(metrics_file, metrics)
                    _logger.info(
                        f"task {self._task_id} round {self._round_id} update weight",
                        extra={"task_id": self._task_id},
                    )
                except Exception as e:
                    _logger.error(e)

            pool = futures.ThreadPoolExecutor(1)
            fut = pool.submit(agg_update, self._last_joined_members, self._agg_result_group)

        self._agg_metrics_group.register(member_id, in_ch)
        _logger.debug(
            f"register {member_id} for agg of task {self._task_id} round {self._round_id}"
        )

        yield out_ch

        member_finish_round(self._task_id, member_id, self._round_id)
        if master:
            assert fut is not None
            assert pool is not None
            fut.result()
            pool.shutdown(True)
            _logger.debug("agg update finish")
            with self._lock:
                self._agg_metrics_group = None
                self._last_joined_members = []
