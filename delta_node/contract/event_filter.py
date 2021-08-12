import threading
from collections import defaultdict
from queue import Empty, Queue
from typing import Dict, Optional

from .client import ChainClient
from .utils import Event


class EventFilter(threading.Thread):
    def __init__(self, node_id: str, client: ChainClient) -> None:
        super().__init__(daemon=True)
        
        self._event_queue: Dict[str, Queue] = defaultdict(Queue)
        self._node_id = node_id
        self._client = client

    def wait_for_event(
        self, event: str, timeout: Optional[float] = None
    ) -> Optional[Event]:
        queue = self._event_queue[event]
        try:
            return queue.get(block=True, timeout=timeout)
        except Empty:
            return None

    def run(self):
        for event in self._client.events(self._node_id):
            name = event.name
            self._event_queue[name].put(event)

    def terminate(self):
        raise KeyboardInterrupt
