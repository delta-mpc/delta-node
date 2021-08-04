from typing import IO
import os
import shutil
import logging

from delta.node import Node

from .location import task_state_file
from ..commu import CommuClient
from .. import node

_logger = logging.getLogger(__name__)

class LocalNode(Node):
    def __init__(self, task_id: int, url: str) -> None:
        self._round_id = 0
        self._task_id = task_id
        self._client = CommuClient(url)
        self._node_id = node.get_node_id()

    def download_state(self, dst: IO[bytes]) -> bool:
        filename = task_state_file(self._task_id, self._round_id)
        if os.path.exists(filename):
            with open(filename, mode="rb") as f:
                shutil.copyfileobj(f, dst)
            _logger.info(f"task {self._task_id} round {self._round_id} download state")
            return True
        else:
            _logger.info(f"task {self._task_id} round {self._round_id} round does not exist")
            return False

    def upload_state(self, file: IO[bytes]):
        filename = task_state_file(self._task_id, self._round_id)
        with open(filename, mode="wb") as f:
            shutil.copyfileobj(file, f)
        _logger.info(f"task {self._task_id} round {self._round_id} upload state")

    def download_weight(self, dst: IO[bytes]) -> bool:
        try:
            round_id = self._client.get_round_id(self._task_id, self._node_id)
            self._round_id = round_id
            file = self._client.get_file(self._task_id, self._node_id, round_id - 1, "weight")
            shutil.copyfileobj(file, dst)
            return True
        except Exception as e:
            _logger.error(f"task {self._task_id} round {self._round_id} error {e}")
            return False

    