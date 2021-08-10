from dataclasses import dataclass


@dataclass
class Event(object):
    name: str
    address: str
    url: str
    task_id: int
    epoch: int
    key: str
