# type: ignore
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AggregationStartedEvent(_message.Message):
    __slots__ = ["addrs", "round", "task_id"]
    ADDRS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    addrs: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., addrs: _Optional[_Iterable[str]] = ...) -> None: ...

class CalculationStartedEvent(_message.Message):
    __slots__ = ["addrs", "round", "task_id"]
    ADDRS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    addrs: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., addrs: _Optional[_Iterable[str]] = ...) -> None: ...

class DataRegisteredEvent(_message.Message):
    __slots__ = ["commitment", "index", "name", "owner"]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    commitment: str
    index: int
    name: str
    owner: str
    def __init__(self, owner: _Optional[str] = ..., name: _Optional[str] = ..., index: _Optional[int] = ..., commitment: _Optional[str] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ["aggregation_started", "calculation_started", "data_registered", "heartbeat", "partner_selected", "round_ended", "round_started", "task_created", "task_finished", "task_member_verified", "task_verification_confirmed"]
    AGGREGATION_STARTED_FIELD_NUMBER: _ClassVar[int]
    CALCULATION_STARTED_FIELD_NUMBER: _ClassVar[int]
    DATA_REGISTERED_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    PARTNER_SELECTED_FIELD_NUMBER: _ClassVar[int]
    ROUND_ENDED_FIELD_NUMBER: _ClassVar[int]
    ROUND_STARTED_FIELD_NUMBER: _ClassVar[int]
    TASK_CREATED_FIELD_NUMBER: _ClassVar[int]
    TASK_FINISHED_FIELD_NUMBER: _ClassVar[int]
    TASK_MEMBER_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    TASK_VERIFICATION_CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    aggregation_started: AggregationStartedEvent
    calculation_started: CalculationStartedEvent
    data_registered: DataRegisteredEvent
    heartbeat: HeartBeatEvent
    partner_selected: PartnerSelectedEvent
    round_ended: RoundEndedEvent
    round_started: RoundStartedEvent
    task_created: TaskCreateEvent
    task_finished: TaskFinishEvent
    task_member_verified: TaskMemberVerifiedEvent
    task_verification_confirmed: TaskVerificationConfirmedEvent
    def __init__(self, task_created: _Optional[_Union[TaskCreateEvent, _Mapping]] = ..., round_started: _Optional[_Union[RoundStartedEvent, _Mapping]] = ..., partner_selected: _Optional[_Union[PartnerSelectedEvent, _Mapping]] = ..., calculation_started: _Optional[_Union[CalculationStartedEvent, _Mapping]] = ..., aggregation_started: _Optional[_Union[AggregationStartedEvent, _Mapping]] = ..., round_ended: _Optional[_Union[RoundEndedEvent, _Mapping]] = ..., task_finished: _Optional[_Union[TaskFinishEvent, _Mapping]] = ..., heartbeat: _Optional[_Union[HeartBeatEvent, _Mapping]] = ..., task_member_verified: _Optional[_Union[TaskMemberVerifiedEvent, _Mapping]] = ..., task_verification_confirmed: _Optional[_Union[TaskVerificationConfirmedEvent, _Mapping]] = ..., data_registered: _Optional[_Union[DataRegisteredEvent, _Mapping]] = ...) -> None: ...

class EventReq(_message.Message):
    __slots__ = ["address", "timeout"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    address: str
    timeout: int
    def __init__(self, address: _Optional[str] = ..., timeout: _Optional[int] = ...) -> None: ...

class HeartBeatEvent(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PartnerSelectedEvent(_message.Message):
    __slots__ = ["addrs", "round", "task_id"]
    ADDRS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    addrs: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., addrs: _Optional[_Iterable[str]] = ...) -> None: ...

class RoundEndedEvent(_message.Message):
    __slots__ = ["round", "task_id"]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class RoundStartedEvent(_message.Message):
    __slots__ = ["round", "task_id"]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class TaskCreateEvent(_message.Message):
    __slots__ = ["address", "commitment", "dataset", "enable_verify", "task_id", "task_type", "tolerance", "url"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    ENABLE_VERIFY_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    dataset: str
    enable_verify: bool
    task_id: str
    task_type: str
    tolerance: int
    url: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., dataset: _Optional[str] = ..., url: _Optional[str] = ..., commitment: _Optional[str] = ..., task_type: _Optional[str] = ..., enable_verify: bool = ..., tolerance: _Optional[int] = ...) -> None: ...

class TaskFinishEvent(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class TaskMemberVerifiedEvent(_message.Message):
    __slots__ = ["address", "task_id", "verified"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    address: str
    task_id: str
    verified: bool
    def __init__(self, task_id: _Optional[str] = ..., address: _Optional[str] = ..., verified: bool = ...) -> None: ...

class TaskVerificationConfirmedEvent(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...
