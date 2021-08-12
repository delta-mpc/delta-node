from abc import ABC
from typing import List, Optional

import numpy as np

from ..channel import ChannelGroup, InnerChannel


class Aggregator(ABC):
    def __init__(
        self, task_id: int, timeout: Optional[float] = None
    ) -> None:
        self._task_id = task_id
        self._timeout = timeout

    def aggregate(self, member_ids: List[str], group: ChannelGroup) -> np.ndarray:
        ...


class Uploader(ABC):
    def __init__(
        self, node_id: str, task_id: int, timeout: Optional[float] = None
    ) -> None:
        self._node_id = node_id
        self._task_id = task_id
        self._timeout = timeout

        self._result_arr: Optional[np.ndarray] = None

    def upload_result(self, result_arr: np.ndarray):
        self._result_arr = result_arr

    def callback(self, ch: InnerChannel):
        ...
