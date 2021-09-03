import json
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from ..channel import ChannelGroup, InnerChannel


class Algorithm(ABC):
    def __init__(self, task_id: int, timeout: Optional[float] = None) -> None:
        self._task_id = task_id
        self._timeout = timeout

    @abstractmethod
    def aggregate(self, member_ids: List[str], group: ChannelGroup) -> np.ndarray:
        ...

    @abstractmethod
    def upload(self, node_id: str, result: np.ndarray, ch: InnerChannel):
        ...

    @abstractmethod
    def update(self, weight: np.ndarray, result: np.ndarray) -> np.ndarray:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def _upload_callback(
        self, node_id: str, result: np.ndarray
    ) -> Callable[[InnerChannel], None]:
        def callback(ch: InnerChannel):
            return self.upload(node_id, result, ch)

        return callback

    def aggregate_result(
        self, member_ids: List[str], group: ChannelGroup, extra_msg: bytes
    ) -> np.ndarray:
        return self.aggregate(member_ids, group)

    def aggregate_metrics(
        self, member_ids: List[str], group: ChannelGroup, extra_msg: bytes
    ) -> Dict[str, float]:
        keys: List[str] = json.loads(extra_msg)
        values_arr = self.aggregate(member_ids, group)
        values = values_arr.tolist()
        res = {k: v for k, v in zip(keys, values)}
        return res

    def upload_result(
        self, node_id: str, result: np.ndarray
    ) -> Tuple[bytes, Callable[[InnerChannel], None]]:
        extra_msg = b""
        callback = self._upload_callback(node_id, result)

        return extra_msg, callback

    def upload_metrics(
        self, node_id: str, metrics: Dict[str, float]
    ) -> Tuple[bytes, Callable[[InnerChannel], None]]:
        keys = sorted(metrics.keys())
        extra_msg = json.dumps(keys).encode("utf-8")

        values_arr = np.array([metrics[k] for k in keys])
        callback = self._upload_callback(node_id, values_arr)

        return extra_msg, callback
