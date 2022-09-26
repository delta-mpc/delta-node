from dataclasses import dataclass
from typing import List

__all__ = ["VerifierState"]


@dataclass
class VerifierState:
    unfinished_clients: List[str]
    invalid_clients: List[str]
    valid: bool
