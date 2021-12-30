from dataclasses import dataclass, field
from typing import List, Literal

__all__ = [
    "EventType",
    "Event",
    "TaskCreateEvent",
    "PartnerSelectedEvent",
    "CalculationStartedEvent",
    "AggregationStartedEvent",
    "RoundStartedEvent",
    "RoundEndedEvent",
    "TaskFinishEvent"
]

EventType = Literal[
    "task_created",
    "round_started",
    "partner_selected",
    "calculation_started",
    "aggregation_started",
    "round_ended",
    "task_finish"
]


@dataclass
class Event:
    type: EventType = field(init=False)
    task_id: str


@dataclass
class TaskCreateEvent(Event):
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
class PartnerSelectedEvent(Event, _Addrs, _Round):
    type: EventType = field(init=False, default="partner_selected")


@dataclass
class CalculationStartedEvent(Event, _Addrs, _Round):
    type: EventType = field(init=False, default="calculation_started")


@dataclass
class AggregationStartedEvent(Event, _Addrs, _Round):
    type: EventType = field(init=False, default="aggregation_started")


@dataclass
class RoundStartedEvent(Event, _Round):
    type: EventType = field(init=False, default="round_started")


@dataclass
class RoundEndedEvent(Event, _Round):
    type: EventType = field(init=False, default="round_ended")


@dataclass
class TaskFinishEvent(Event):
    type: EventType = field(init=False, default="task_finish")
