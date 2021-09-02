from typing import Dict, List, Optional

from . import base, simple, secure

_impls = {"FedAvg": simple, "FaultTolerantFedAvg": secure}

_aggregators: Dict[int, base.Aggregator] = {}

_uploaders: Dict[int, base.Uploader] = {}


def new_aggregator(
    algorithm: str,
    task_id: int,
    timeout: Optional[float] = None,
) -> base.Aggregator:
    if algorithm not in _impls:
        raise KeyError(f"no such algorithm {algorithm}")
    if task_id not in _aggregators:
        impl = _impls[algorithm]
        aggregator = impl.Aggregator(task_id, timeout)
        _aggregators[task_id] = aggregator
    return _aggregators[task_id]


def new_uploader(
    algorithm: str,
    node_id: str,
    task_id: int,
    timeout: Optional[float] = None,
    **kwargs,
) -> base.Uploader:
    if algorithm not in _impls:
        raise KeyError(f"no such algorithm {algorithm}")
    if task_id not in _uploaders:
        impl = _impls[algorithm]
        uploader = impl.Uploader(node_id, task_id, timeout, **kwargs)
        _uploaders[task_id] = uploader
    return _uploaders[task_id]
