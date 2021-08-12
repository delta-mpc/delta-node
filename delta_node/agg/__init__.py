from typing import Dict, List, Optional

from . import base, simple

_impls = {0: simple}

_aggregators: Dict[int, base.Aggregator] = {}

_uploaders: Dict[int, base.Uploader] = {}


def new_aggregator(
    secure_level: int,
    task_id: int,
    timeout: Optional[float] = None,
) -> base.Aggregator:
    if secure_level not in _impls:
        raise KeyError(f"no such secure level {secure_level}")
    if task_id not in _aggregators:
        impl = _impls[secure_level]
        aggregator = impl.Aggregator(task_id, timeout)
        _aggregators[task_id] = aggregator
    return _aggregators[task_id]


def new_uploader(
    secure_level: int, task_id: int, node_id: str, timeout: Optional[float] = None
) -> base.Uploader:
    if secure_level not in _impls:
        raise KeyError(f"no such secure level {secure_level}")
    if task_id not in _uploaders:
        impl = _impls[secure_level]
        uploader = impl.Uploader(node_id, task_id, timeout)
        _uploaders[task_id] = uploader
    return _uploaders[task_id]
