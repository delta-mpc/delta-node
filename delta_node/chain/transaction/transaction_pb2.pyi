from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_message.Message):
    __slots__ = ["tx_hash"]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    tx_hash: str
    def __init__(self, tx_hash: _Optional[str] = ...) -> None: ...
