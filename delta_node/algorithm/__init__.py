from typing import Dict, Optional

from ..exceptions import TaskErrorWithMsg
from .base import Algorithm
from .fault_tolerant_fedavg import FaultTolerantFedAvg
from .fedavg import FedAvg

__all__ = ["new_algorithm"]

_cache: Dict[int, Algorithm] = {}


def new_algorithm(
    name: str, task_id: int, timeout: Optional[float] = None
) -> Algorithm:
    if task_id not in _cache:
        if name == "FedAvg":
            alg = FedAvg(task_id, timeout)
        elif name == "FaultTolerantFedAvg":
            alg = FaultTolerantFedAvg(task_id, timeout)
        else:
            raise TaskErrorWithMsg(task_id, f"unknown task algorithm {name}")
        _cache[task_id] = alg
    return _cache[task_id]
