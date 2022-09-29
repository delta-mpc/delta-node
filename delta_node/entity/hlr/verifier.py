from dataclasses import dataclass
from typing import List

__all__ = ["VerifierState", "Proof"]


@dataclass
class VerifierState:
    unfinished_clients: List[str]
    invalid_clients: List[str]
    valid: bool


@dataclass
class Proof:
    index: int
    proof: str
    pub_signals: List[str]
