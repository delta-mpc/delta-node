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
]

EventType = Literal["task_create", "round_started", "partner_selected", "calculation_started", "aggregation_started", "round_ended"]

@dataclass
class Event:
    type: EventType = field(init=False)


@dataclass
class TaskCreateEvent(Event):
    type = field(init=False, default="task_create")
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
    type = field(init=False, default="partner_selected")


@dataclass
class CalculationStartedEvent(Event, _Addrs, _Round):
    type = field(init=False, default="calculation_started")


@dataclass
class AggregationStartedEvent(Event, _Addrs, _Round):
    type = field(init=False, default="aggregation_started")


@dataclass
class RoundStartedEvent(Event, _Round):
    type = field(init=False, default="round_started")


@dataclass
class RoundEndedEvent(Event, _Round):
    type = field(init=False, default="round_ended")
