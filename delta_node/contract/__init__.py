import threading
from abc import ABCMeta
from collections import defaultdict
from queue import Queue, Empty
from typing import Dict, List, Optional

from pydantic import BaseModel

from .. import config


__all__ = [
    "register_node",
    "create_task",
    "join_task",
    "start_round",
    "publish_pub_key",
    "Event",
    "EventFilter",
    "new_event_filter",
]


def register_node(url: str) -> str:
    if config.contract_impl == "substrate":
        from .substrate import contract
    elif config.contract_impl == "monkey":
        from .monkey import contract
    else:
        raise ImportError("unknown contract impl")

    return contract.register_node(url)


def create_task(node_id: str, task_name: str) -> int:
    if config.contract_impl == "substrate":
        from .substrate import contract
    elif config.contract_impl == "monkey":
        from .monkey import contract
    else:
        raise ImportError("unknown contract impl")

    return contract.create_task(node_id, task_name)


def join_task(node_id: str, task_id: int) -> bool:
    if config.contract_impl == "substrate":
        from .substrate import contract
    elif config.contract_impl == "monkey":
        from .monkey import contract
    else:
        raise ImportError("unknown contract impl")
    return contract.join_task(node_id, task_id)


def start_round(node_id: str, task_id: int) -> int:
    if config.contract_impl == "substrate":
        from .substrate import contract
    elif config.contract_impl == "monkey":
        from .monkey import contract
    else:
        raise ImportError("unknown contract impl")
    return contract.start_round(node_id, task_id)


def publish_pub_key(node_id: str, task_id: int, round_id: int, pub_key: str):
    if config.contract_impl == "substrate":
        from .substrate import contract
    elif config.contract_impl == "monkey":
        from .monkey import contract
    else:
        raise ImportError("unknown contract impl")
    return contract.publish_pub_key(node_id, task_id, round_id, pub_key)


class Event(BaseModel):
    name: str
    address: str
    url: str
    task_id: int
    epoch: int
    key: str


class EventFilter(threading.Thread, metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self._event_queue: Dict[str, Queue] = defaultdict(Queue)

    def wait_for_event(self, event: str, timeout: Optional[float] = None) -> Optional[Event]:
        queue = self._event_queue[event]
        try:
            return queue.get(block=True, timeout=timeout)
        except Empty:
            return None

    def run(self):
        ...

    def terminate(self):
        ...


def new_event_filter(*args, **kwargs) -> EventFilter:
    if config.contract_impl == "substrate":
        from .substrate import event_filter
    elif config.contract_impl == "monkey":
        from .monkey import event_filter
    else:
        raise ImportError("unknown contract impl")
    return event_filter.EventFilter(*args, **kwargs)
