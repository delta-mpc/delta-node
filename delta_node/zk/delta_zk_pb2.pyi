# type: ignore
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Input(_message.Message):
    __slots__ = ["weights", "xy"]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    XY_FIELD_NUMBER: _ClassVar[int]
    weights: _containers.RepeatedScalarFieldContainer[float]
    xy: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, weights: _Optional[_Iterable[float]] = ..., xy: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...

class Proof(_message.Message):
    __slots__ = ["calldata", "error", "index", "proof", "publicSignals"]
    CALLDATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    PUBLICSIGNALS_FIELD_NUMBER: _ClassVar[int]
    calldata: str
    error: str
    index: int
    proof: str
    publicSignals: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, index: _Optional[int] = ..., publicSignals: _Optional[_Iterable[str]] = ..., proof: _Optional[str] = ..., calldata: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ["d"]
    D_FIELD_NUMBER: _ClassVar[int]
    d: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, d: _Optional[_Iterable[float]] = ...) -> None: ...
