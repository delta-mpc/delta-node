from dataclasses import dataclass
from typing import List


@dataclass
class Event(object):
    name: str
    address: str
    url: str
    task_id: int
    epoch: int
    key: str


@dataclass
class Node(object):
    id: str
    url: str
    name: str


@dataclass
class NodesResp(object):
    nodes: List[Node]
    total_pages: int
