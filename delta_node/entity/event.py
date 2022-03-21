import string
from dataclasses import dataclass, field
from typing import List, Literal

__all__ = [
    "EventType",
    "Event",
    "TaskEvent",
    "TaskCreateEvent",
    "PartnerSelectedEvent",
    "CalculationStartedEvent",
    "AggregationStartedEvent",
    "RoundStartedEvent",
    "RoundEndedEvent",
    "TaskFinishEvent",
    "HeartbeatEvent",
]

EventType = Literal[
    "task_created",
    "round_started",
    "partner_selected",
    "calculation_started",
    "aggregation_started",
    "round_ended",
    "task_finish",
    "heartbeat",
]


@dataclass
class Event:
    type: EventType = field(init=False)


@dataclass
class TaskEvent(Event):
    task_id: str


@dataclass
class TaskCreateEvent(TaskEvent):
    type: EventType = field(init=False, default="task_created")
    address: str
    task_id: str
    dataset: str
    url: str
    commitment: bytes
    task_type: str


@dataclass
class _Round(object):
    task_id: str
    round: int


@dataclass
class _Addrs(object):
    addrs: List[str]


@dataclass
class PartnerSelectedEvent(TaskEvent, _Addrs, _Round):
    type: EventType = field(init=False, default="partner_selected")


@dataclass
class CalculationStartedEvent(TaskEvent, _Addrs, _Round):
    type: EventType = field(init=False, default="calculation_started")


@dataclass
class AggregationStartedEvent(TaskEvent, _Addrs, _Round):
    type: EventType = field(init=False, default="aggregation_started")


@dataclass
class RoundStartedEvent(TaskEvent, _Round):
    type: EventType = field(init=False, default="round_started")


@dataclass
class RoundEndedEvent(TaskEvent, _Round):
    type: EventType = field(init=False, default="round_ended")


@dataclass
class TaskFinishEvent(TaskEvent):
    type: EventType = field(init=False, default="task_finish")


@dataclass
class HeartbeatEvent(Event):
    type: EventType = field(init=False, default="heartbeat")
