# type: ignore
from ..transaction import transaction_pb2 as _transaction_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JoinReq(_message.Message):
    __slots__ = ["name", "url"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    def __init__(self, url: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class JoinResp(_message.Message):
    __slots__ = ["address", "tx_hash"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    address: str
    tx_hash: str
    def __init__(self, tx_hash: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class LeaveReq(_message.Message):
    __slots__ = ["address"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class NodeInfo(_message.Message):
    __slots__ = ["address", "name", "url"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    address: str
    name: str
    url: str
    def __init__(self, url: _Optional[str] = ..., name: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class NodeInfoReq(_message.Message):
    __slots__ = ["address"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class NodeInfos(_message.Message):
    __slots__ = ["nodes", "total_count"]
    NODES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[NodeInfo]
    total_count: int
    def __init__(self, nodes: _Optional[_Iterable[_Union[NodeInfo, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class NodeInfosReq(_message.Message):
    __slots__ = ["page", "page_size"]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class UpdateNameReq(_message.Message):
    __slots__ = ["address", "name"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    address: str
    name: str
    def __init__(self, address: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class UpdateUrlReq(_message.Message):
    __slots__ = ["address", "url"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    address: str
    url: str
    def __init__(self, address: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...
