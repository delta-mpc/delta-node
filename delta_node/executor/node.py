import logging
import os
import shutil
from functools import partial
from typing import IO, Any, Callable, Dict, Iterable

from delta.node import Node

from .. import agg, data, node, utils
from ..commu import CommuClient
from ..model import RoundStatus, TaskMetadata
from .location import task_state_file
from .task import (get_member_round_status, member_finish_round,
                   member_start_round)

_logger = logging.getLogger(__name__)


class LocalNode(Node):
    def __init__(
        self, data_dir, task_id: int, metadata: TaskMetadata, client: CommuClient
    ) -> None:
        self._data_dir = data_dir
        self._round_id = 0
        self._round_finished = True
        self._task_id = task_id
        self._client = client
        self._metadata = metadata
        self._node_id = node.get_node_id()

    def new_dataloader(
        self, dataset: str, dataloader: Dict[str, Any], preprocess: Callable
    ) -> Iterable:
        return data.new_dataloader(
            os.path.join(self._data_dir, dataset), dataloader, preprocess
        )

    def download_state(self, dst: IO[bytes]) -> bool:
        filename = task_state_file(self._task_id, self._round_id)
        if os.path.exists(filename):
            with open(filename, mode="rb") as f:
                shutil.copyfileobj(f, dst)
            _logger.info(
                f"task {self._task_id} round {self._round_id} download state",
                extra={"task_id": self._task_id},
            )
            return True
        else:
            _logger.info(
                f"task {self._task_id} round {self._round_id} round does not exist",
                extra={"task_id": self._task_id},
            )
            return False

    def upload_state(self, file: IO[bytes]):
        filename = task_state_file(self._task_id, self._round_id)
        with open(filename, mode="wb") as f:
            shutil.copyfileobj(file, f)
        _logger.info(
            f"task {self._task_id} round {self._round_id} upload state",
            extra={"task_id": self._task_id},
        )

    def download_weight(self, dst: IO[bytes]) -> bool:
        try:
            round_id = self._client.get_round_id(self._task_id, self._node_id)
            _logger.info(f"task {self._task_id} round {round_id} start")
            self._round_id = round_id
            self._round_finished = False
            member_start_round(self._task_id, self._node_id, round_id)
            self._client.get_file(
                self._task_id, self._node_id, round_id - 1, "weight", dst
            )
            _logger.info(
                f"task {self._task_id} get weight file of round {self._round_id}",
                extra={"task_id": self._task_id},
            )
            return True
        except Exception as e:
            _logger.error(
                f"task {self._task_id} round {self._round_id} error {e}",
                extra={"task_id": self._task_id},
            )
            return False

    def upload_result(self, data: IO[bytes]):
        try:
            result_arr = utils.load_arr(data)
            uploader = agg.new_uploader(self._metadata.secure_level, self._node_id, self._task_id)
            uploader.upload_result(result_arr)
            self._client.upload_result(
                self._task_id, self._node_id, self._round_id, uploader.callback
            )
            _logger.info(
                f"task {self._task_id} upload result of round {self._round_id}",
                extra={"task_id": self._task_id},
            )
            self._round_finished = True
            member_finish_round(self._task_id, self._node_id, self._round_id)
            _logger.info(
                f"task {self._task_id} finish round {self._round_id}",
                extra={"task_id": self._task_id},
            )
        except Exception as e:
            _logger.error(
                f"task {self._task_id} round {self._round_id} error {e}",
                extra={"task_id": self._task_id},
            )

    def finish(self):
        try:
            last_round_id, status = get_member_round_status(
                self._task_id, self._node_id
            )
            if status == RoundStatus.RUNNING:
                member_finish_round(self._task_id, self._node_id, last_round_id)
            self._client.finish_task(self._task_id, self._node_id)
            _logger.info(
                f"task {self._task_id} finished, total round {self._round_id}",
                extra={"task_id": self._task_id},
            )
        except Exception as e:
            _logger.error(
                f"task {self._task_id} round {self._round_id} error {e}",
                extra={"task_id": self._task_id},
            )
