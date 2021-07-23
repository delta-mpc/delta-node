from collections import defaultdict
import logging

from pydantic import BaseModel

from . import mpc_pb2
from .channel import stub

logger = logging.getLogger(__name__)

__all__ = ["register_event_filter", "start_listen_event", "Event"]

_event_filters = defaultdict(list)


class Event(BaseModel):
    name: str
    address: str
    url: str
    task_id: int
    epoch: int
    key: str


def register_event_filter(event: str, func):
    _event_filters[event].append(func)


def start_listen_event(interval: int = 5):
    req = mpc_pb2.EventRequest()
    for e in stub.event(req):
        event = Event(
            name=e.name,
            address=e.address,
            url=e.url,
            task_id=e.taskId,
            epoch=e.epoch,
            key=e.key,
        )
        print(str(event))
        for event_name in _event_filters:
            if event.name == event_name:
                for func in _event_filters[event_name]:
                    try:
                        func(event)
                    except Exception as e:
                        logger.exception(e)
