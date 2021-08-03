import threading
import time
from collections import defaultdict
from typing import Any, Dict, List

import requests

from ... import config, contract

_event_func_map = {
    "Join": "join_task",
    "Task": "create_task",
    "Train": "start_round",
    "PublicKey": "pub_key",
}


def _call_event_func(
    event: str, start: int, page: int, page_size: int = 20
) -> List[Dict[str, Any]]:
    url = config.contract_address + "/event/" + _event_func_map[event]
    data = {"page": page, "page_size": page_size, "start": start}
    resp = requests.get(url, data)
    resp.raise_for_status()
    resp_data = resp.json()
    return resp_data


class EventFilter(contract.EventFilter):
    def __init__(self, interval: float = 5) -> None:
        super().__init__()
        self._event_start = defaultdict(int)
        self._interval = interval
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            for name in _event_func_map:
                start = self._event_start[name]
                events = _call_event_func(name, start, 1, 20)
                if len(events) > 0:
                    for event in events:
                        e = contract.Event(
                            name=event["name"],
                            address=event["address"],
                            url=event["url"],
                            task_id=event["task_id"],
                            epoch=event["epoch"],
                            key=event["key"],
                        )
                        self._event_queue[name].put(e)
                    new_start = events[-1]["event_id"] + 1
                    self._event_start[name] = new_start

            time.sleep(self._interval)

    def terminate(self):
        self._stop_event.set()
