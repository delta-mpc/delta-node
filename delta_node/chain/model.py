from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class NodeInfo(object):
    url: str
    name: str


class RoundStatus(Enum):
    STARTED = 0
    RUNNING = 1
    CALCULATING = 2
    AGGREGATING = 3
    FINISHED = 4


@dataclass
class TaskRound(object):
    round: int
    status: RoundStatus
    clients: List[str]


@dataclass
class PublicKeyPair(object):
    pk1: bytes
    pk2: bytes


@dataclass
class SecretShareData(object):
    seed: Optional[bytes]
    seed_commitment: Optional[bytes]
    secret_key: Optional[bytes]
    secret_key_commitment: Optional[bytes]

@dataclass
class Event(object):
    pass


@dataclass
class TaskCreateEvent(Event):
    address: str
    task_id: str
    dataset: str
    url: str
    commitment: bytes


@dataclass
class _Round(object):
    task_id: str
    round: int


@dataclass
class _Addrs(object):
    addrs: List[str]


@dataclass
class PartnerSelectedEvent(Event, _Addrs, _Round):
    pass


@dataclass
class CalculationStartedEvent(Event, _Addrs, _Round):
    pass


@dataclass
class AggregationStartedEvent(Event, _Addrs, _Round):
    pass


@dataclass
class RoundStartedEvent(Event, _Round):
    pass

@dataclass
class RoundEndedEvent(Event, _Round):
    pass
