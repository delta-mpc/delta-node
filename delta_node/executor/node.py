import json
import logging
import os
import shutil
from typing import IO, Any, Callable, Dict, Iterable, Tuple

import numpy as np
from delta.algorithm.horizontal import HorizontalAlgorithm
from delta.node import Node
from delta.serialize import load_arr

from .. import agg, data, node
from ..commu import CommuClient
from ..exceptions import TaskContinue
from ..model import RoundStatus, TaskMetadata
from .location import task_state_file
from .task import get_member_round, member_finish_round, member_start_round

_logger = logging.getLogger(__name__)


class HorizontolLocalNode(Node):
    def __init__(
        self,
        task_id: int,
        client: CommuClient,
        data_dir: str,
        metadata: TaskMetadata,
        algorithm: HorizontalAlgorithm,
    ):
        self._task_id = task_id
        self._node_id = node.get_node_id()
        r = get_member_round(self._task_id, self._node_id)
        self._round_id = r.round_id
        self._round_status = r.status
        self._client = client
        self._data_dir = data_dir
        self._metadata = metadata
        self._alg = algorithm

    def new_dataloader(
        self,
        dataset: str,
        validate_frac: float,
        cfg: Dict[str, Any],
        preprocess: Callable,
    ) -> Tuple[Iterable, Iterable]:
        return data.new_train_val_dataloader(
            os.path.join(self._data_dir, dataset), validate_frac, cfg, preprocess
        )

    def download(self, type: str, dst: IO[bytes]) -> bool:
        if type == "state":
            return self.download_state(dst)
        elif type == "weight":
            return self.download_weight(dst)
        raise ValueError(f"unknown download type {type}")

    def upload(self, type: str, src: IO[bytes]):
        if type == "state":
            return self.upload_state(src)
        elif type == "result":
            return self.upload_result(src)
        elif type == "metrics":
            return self.upload_metrics(src)
        raise ValueError(f"unknown upload type {type}")

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

    def download_weight(self, dst: IO[bytes]) -> bool:
        if self._client.join_task(self._task_id, self._node_id):
            last_round_id = self._round_id
            try:
                round_id = self._client.get_round_id(self._task_id, self._node_id)
                _logger.info(f"task {self._task_id} round {round_id} start")
                self._round_id = round_id
                self._round_status = RoundStatus.RUNNING
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
                    f"task {self._task_id} round {last_round_id} get weight error {e}",
                    extra={"task_id": self._task_id},
                )
                raise TaskContinue(self._task_id, str(e))
        else:
            raise TaskContinue(self._task_id, f"cannot join task {self._task_id}")

    def upload_state(self, src: IO[bytes]):
        filename = task_state_file(self._task_id, self._round_id)
        with open(filename, mode="wb") as f:
            shutil.copyfileobj(src, f)
        _logger.info(
            f"task {self._task_id} round {self._round_id} upload state",
            extra={"task_id": self._task_id},
        )

    def upload_result(self, src: IO[bytes]):
        try:
            result_arr = load_arr(src)
            uploader = agg.new_uploader(self._alg.name, self._node_id, self._task_id)
            uploader.upload_result(result_arr)
            self._client.upload_result(
                self._task_id, self._node_id, self._round_id, uploader.callback
            )
            _logger.info(
                f"task {self._task_id} upload result of round {self._round_id}",
                extra={"task_id": self._task_id},
            )
            self._round_status = RoundStatus.FINISHED
            member_finish_round(self._task_id, self._node_id, self._round_id)
            _logger.info(
                f"task {self._task_id} finish round {self._round_id}",
                extra={"task_id": self._task_id},
            )
        except Exception as e:
            _logger.error(
                f"task {self._task_id} round {self._round_id} upload state error {e}",
                extra={"task_id": self._task_id},
            )
            raise TaskContinue(self._task_id, str(e))

    def upload_metrics(self, src: IO[bytes]):
        try:
            metrics: Dict[str, float] = json.load(src)
            ordered_keys = sorted(metrics.keys())
            values = np.array([metrics[key] for key in ordered_keys])
            uploader = agg.new_uploader(self._alg.name, self._node_id, self._task_id)
            uploader.upload_result(values)
            self._client.upload_result(
                self._task_id, self._node_id, self._round_id, uploader.callback
            )
            _logger.info(
                f"task {self._task_id} upload metrics of round {self._round_id}",
                extra={"task_id": self._task_id},
            )
        except Exception as e:
            _logger.error(
                f"task {self._task_id} round {self._round_id} upload metrics error {e}",
                extra={"task_id": self._task_id},
            )
            raise TaskContinue(self._task_id, str(e))

    def finish(self):
        try:
            if self._round_status == RoundStatus.RUNNING:
                self._round_status = RoundStatus.FINISHED
                member_finish_round(self._task_id, self._node_id, self._round_id)

            self._client.finish_task(self._task_id, self._node_id)
            _logger.info(
                f"task {self._task_id} finished, total round {self._round_id}",
                extra={"task_id": self._task_id},
            )
        except Exception as e:
            _logger.error(
                f"task {self._task_id} round {self._round_id} finish error {e}",
                extra={"task_id": self._task_id},
            )
            raise TaskContinue(self._task_id, str(e))


# class LocalNode(Node):
#     def __init__(
#         self, data_dir, task_id: int, metadata: TaskMetadata, client: CommuClient
#     ) -> None:
#         self._data_dir = data_dir
#         self._round_id = 0
#         self._round_finished = True
#         self._task_id = task_id
#         self._client = client
#         self._metadata = metadata
#         self._node_id = node.get_node_id()

#     def new_dataloader(
#         self, dataset: str, dataloader: Dict[str, Any], preprocess: Callable
#     ) -> Iterable:
#         return data.new_dataloader(
#             os.path.join(self._data_dir, dataset), dataloader, preprocess
#         )

#     def download_state(self, dst: IO[bytes]) -> bool:
#         filename = task_state_file(self._task_id, self._round_id)
#         if os.path.exists(filename):
#             with open(filename, mode="rb") as f:
#                 shutil.copyfileobj(f, dst)
#             _logger.info(
#                 f"task {self._task_id} round {self._round_id} download state",
#                 extra={"task_id": self._task_id},
#             )
#             return True
#         else:
#             _logger.info(
#                 f"task {self._task_id} round {self._round_id} round does not exist",
#                 extra={"task_id": self._task_id},
#             )
#             return False

#     def upload_state(self, file: IO[bytes]):
#         filename = task_state_file(self._task_id, self._round_id)
#         with open(filename, mode="wb") as f:
#             shutil.copyfileobj(file, f)
#         _logger.info(
#             f"task {self._task_id} round {self._round_id} upload state",
#             extra={"task_id": self._task_id},
#         )

#     def download_weight(self, dst: IO[bytes]) -> bool:
#         try:
#             round_id = self._client.get_round_id(self._task_id, self._node_id)
#             _logger.info(f"task {self._task_id} round {round_id} start")
#             self._round_id = round_id
#             self._round_finished = False
#             member_start_round(self._task_id, self._node_id, round_id)
#             self._client.get_file(
#                 self._task_id, self._node_id, round_id - 1, "weight", dst
#             )
#             _logger.info(
#                 f"task {self._task_id} get weight file of round {self._round_id}",
#                 extra={"task_id": self._task_id},
#             )
#             return True
#         except Exception as e:
#             _logger.error(
#                 f"task {self._task_id} round {self._round_id} error {e}",
#                 extra={"task_id": self._task_id},
#             )
#             return False

#     def upload_result(self, data: IO[bytes]):
#         try:
#             result_arr = utils.load_arr(data)
#             uploader = agg.new_uploader(self._metadata.secure_level, self._node_id, self._task_id)
#             uploader.upload_result(result_arr)
#             self._client.upload_result(
#                 self._task_id, self._node_id, self._round_id, uploader.callback
#             )
#             _logger.info(
#                 f"task {self._task_id} upload result of round {self._round_id}",
#                 extra={"task_id": self._task_id},
#             )
#             self._round_finished = True
#             member_finish_round(self._task_id, self._node_id, self._round_id)
#             _logger.info(
#                 f"task {self._task_id} finish round {self._round_id}",
#                 extra={"task_id": self._task_id},
#             )
#         except Exception as e:
#             _logger.error(
#                 f"task {self._task_id} round {self._round_id} error {e}",
#                 extra={"task_id": self._task_id},
#             )

#     def finish(self):
#         try:
#             last_round_id, status = get_member_round_status(
#                 self._task_id, self._node_id
#             )
#             if status == RoundStatus.RUNNING:
#                 member_finish_round(self._task_id, self._node_id, last_round_id)
#             self._client.finish_task(self._task_id, self._node_id)
#             _logger.info(
#                 f"task {self._task_id} finished, total round {self._round_id}",
#                 extra={"task_id": self._task_id},
#             )
#         except Exception as e:
#             _logger.error(
#                 f"task {self._task_id} round {self._round_id} error {e}",
#                 extra={"task_id": self._task_id},
#             )
