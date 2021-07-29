import logging

from ... import contract
from . import mpc_pb2
from .channel import stub

logger = logging.getLogger(__name__)


class EventFilter(contract.EventFilter):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        req = mpc_pb2.EventRequest()

        for e in stub.event(req):
            event = contract.Event(
                name=e.name,
                address=e.address,
                url=e.url,
                task_id=e.taskId,
                epoch=e.epoch,
                key=e.key,
            )
            if event.name in self._event_queue:
                self._event_queue[event.name].put(event)

    def terminate(self):
        raise KeyboardInterrupt