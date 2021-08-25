from typing import Dict, List, Optional

from . import base, simple, secure

_impls = {0: simple, 1: secure}

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
    secure_level: int,
    node_id: str,
    task_id: int,
    timeout: Optional[float] = None,
    **kwargs,
) -> base.Uploader:
    if secure_level not in _impls:
        raise KeyError(f"no such secure level {secure_level}")
    if task_id not in _uploaders:
        impl = _impls[secure_level]
        uploader = impl.Uploader(node_id, task_id, timeout, **kwargs)
        _uploaders[task_id] = uploader
    return _uploaders[task_id]
