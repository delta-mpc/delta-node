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
