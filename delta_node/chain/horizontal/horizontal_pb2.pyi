# type: ignore
from ..transaction import transaction_pb2 as _transaction_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

AGGREGATING: RoundStatus
CALCULATING: RoundStatus
DESCRIPTOR: _descriptor.FileDescriptor
FINISHED: RoundStatus
RUNNING: RoundStatus
STARTED: RoundStatus

class AggregationReq(_message.Message):
    __slots__ = ["address", "clients", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    clients: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., clients: _Optional[_Iterable[str]] = ...) -> None: ...

class CalculationReq(_message.Message):
    __slots__ = ["address", "clients", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    clients: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., clients: _Optional[_Iterable[str]] = ...) -> None: ...

class CandidatesReq(_message.Message):
    __slots__ = ["address", "clients", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    clients: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., clients: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateTaskReq(_message.Message):
    __slots__ = ["address", "commitment", "dataset", "task_type"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    dataset: str
    task_type: str
    def __init__(self, address: _Optional[str] = ..., dataset: _Optional[str] = ..., commitment: _Optional[str] = ..., task_type: _Optional[str] = ...) -> None: ...

class CreateTaskResp(_message.Message):
    __slots__ = ["task_id", "tx_hash"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    tx_hash: str
    def __init__(self, tx_hash: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...

class EndRoundReq(_message.Message):
    __slots__ = ["address", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class FinishTaskReq(_message.Message):
    __slots__ = ["address", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...

class JoinRoundReq(_message.Message):
    __slots__ = ["address", "pk1", "pk2", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PK1_FIELD_NUMBER: _ClassVar[int]
    PK2_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    pk1: str
    pk2: str
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., pk1: _Optional[str] = ..., pk2: _Optional[str] = ...) -> None: ...

class PublicKeyReq(_message.Message):
    __slots__ = ["clients", "round", "task_id"]
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    clients: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., clients: _Optional[_Iterable[str]] = ...) -> None: ...

class PublicKeyResp(_message.Message):
    __slots__ = ["keys"]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[PublicKeys]
    def __init__(self, keys: _Optional[_Iterable[_Union[PublicKeys, _Mapping]]] = ...) -> None: ...

class PublicKeys(_message.Message):
    __slots__ = ["pk1", "pk2"]
    PK1_FIELD_NUMBER: _ClassVar[int]
    PK2_FIELD_NUMBER: _ClassVar[int]
    pk1: str
    pk2: str
    def __init__(self, pk1: _Optional[str] = ..., pk2: _Optional[str] = ...) -> None: ...

class ResultCommitment(_message.Message):
    __slots__ = ["address", "commitment", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., commitment: _Optional[str] = ...) -> None: ...

class ResultCommitmentReq(_message.Message):
    __slots__ = ["client", "round", "task_id"]
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    client: str
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., client: _Optional[str] = ...) -> None: ...

class ResultCommitmentResp(_message.Message):
    __slots__ = ["commitment"]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    commitment: str
    def __init__(self, commitment: _Optional[str] = ...) -> None: ...

class SecretShareData(_message.Message):
    __slots__ = ["secret_key", "secret_key_commitment", "seed", "seed_commitment"]
    SECRET_KEY_COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    SEED_COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    secret_key: str
    secret_key_commitment: str
    seed: str
    seed_commitment: str
    def __init__(self, seed: _Optional[str] = ..., seed_commitment: _Optional[str] = ..., secret_key: _Optional[str] = ..., secret_key_commitment: _Optional[str] = ...) -> None: ...

class SecretShareReq(_message.Message):
    __slots__ = ["receiver", "round", "senders", "task_id"]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    SENDERS_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    receiver: str
    round: int
    senders: _containers.RepeatedScalarFieldContainer[str]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ..., senders: _Optional[_Iterable[str]] = ..., receiver: _Optional[str] = ...) -> None: ...

class SecretShareResp(_message.Message):
    __slots__ = ["shares"]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    shares: _containers.RepeatedCompositeFieldContainer[SecretShareData]
    def __init__(self, shares: _Optional[_Iterable[_Union[SecretShareData, _Mapping]]] = ...) -> None: ...

class Share(_message.Message):
    __slots__ = ["address", "round", "senders", "shares", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    SENDERS_FIELD_NUMBER: _ClassVar[int]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    round: int
    senders: _containers.RepeatedScalarFieldContainer[str]
    shares: _containers.RepeatedScalarFieldContainer[str]
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., senders: _Optional[_Iterable[str]] = ..., shares: _Optional[_Iterable[str]] = ...) -> None: ...

class ShareCommitment(_message.Message):
    __slots__ = ["address", "commitments", "receivers", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENTS_FIELD_NUMBER: _ClassVar[int]
    RECEIVERS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitments: _containers.RepeatedScalarFieldContainer[str]
    receivers: _containers.RepeatedScalarFieldContainer[str]
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., receivers: _Optional[_Iterable[str]] = ..., commitments: _Optional[_Iterable[str]] = ...) -> None: ...

class StartRoundReq(_message.Message):
    __slots__ = ["address", "round", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    round: int
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class TaskReq(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class TaskResp(_message.Message):
    __slots__ = ["address", "commitment", "dataset", "finished", "task_id", "task_type", "url"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    dataset: str
    finished: bool
    task_id: str
    task_type: str
    url: str
    def __init__(self, address: _Optional[str] = ..., url: _Optional[str] = ..., task_id: _Optional[str] = ..., dataset: _Optional[str] = ..., commitment: _Optional[str] = ..., task_type: _Optional[str] = ..., finished: bool = ...) -> None: ...

class TaskRoundReq(_message.Message):
    __slots__ = ["round", "task_id"]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class TaskRoundResp(_message.Message):
    __slots__ = ["clients", "round", "status"]
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    clients: _containers.RepeatedScalarFieldContainer[str]
    round: int
    status: RoundStatus
    def __init__(self, round: _Optional[int] = ..., status: _Optional[_Union[RoundStatus, str]] = ..., clients: _Optional[_Iterable[str]] = ...) -> None: ...

class RoundStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
