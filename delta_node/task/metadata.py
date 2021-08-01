from dataclasses import dataclass
from typing import List


@dataclass
class TaskMetadata(object):
    name: str
    type: str
    secure_level: int
    algorithm: str
    members: List[str]
