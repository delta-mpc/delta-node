# type: ignore
from ..transaction import transaction_pb2 as _transaction_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DataCommitmentReq(_message.Message):
    __slots__ = ["address", "index", "name"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    address: str
    index: int
    name: str
    def __init__(self, address: _Optional[str] = ..., name: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...

class DataCommitmentResp(_message.Message):
    __slots__ = ["commitment"]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    commitment: str
    def __init__(self, commitment: _Optional[str] = ...) -> None: ...

class RegisterReq(_message.Message):
    __slots__ = ["address", "commitment", "index", "name"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    index: int
    name: str
    def __init__(self, address: _Optional[str] = ..., name: _Optional[str] = ..., index: _Optional[int] = ..., commitment: _Optional[str] = ...) -> None: ...
