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

class ConfirmReq(_message.Message):
    __slots__ = ["address", "task_id"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    task_id: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...

class CreateTaskReq(_message.Message):
    __slots__ = ["address", "commitment", "dataset", "enable_verify", "tolerance"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    ENABLE_VERIFY_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    dataset: str
    enable_verify: bool
    tolerance: int
    def __init__(self, address: _Optional[str] = ..., dataset: _Optional[str] = ..., commitment: _Optional[str] = ..., enable_verify: bool = ..., tolerance: _Optional[int] = ...) -> None: ...

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
    __slots__ = ["address", "round", "task_id", "weight_commitment"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    address: str
    round: int
    task_id: str
    weight_commitment: str
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., round: _Optional[int] = ..., weight_commitment: _Optional[str] = ...) -> None: ...

class TaskReq(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class TaskResp(_message.Message):
    __slots__ = ["address", "commitment", "dataset", "enable_verify", "finished", "task_id", "task_type", "tolerance", "url"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    ENABLE_VERIFY_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    address: str
    commitment: str
    dataset: str
    enable_verify: bool
    finished: bool
    task_id: str
    task_type: str
    tolerance: int
    url: str
    def __init__(self, address: _Optional[str] = ..., url: _Optional[str] = ..., task_id: _Optional[str] = ..., dataset: _Optional[str] = ..., commitment: _Optional[str] = ..., task_type: _Optional[str] = ..., finished: bool = ..., enable_verify: bool = ..., tolerance: _Optional[int] = ...) -> None: ...

class TaskRoundReq(_message.Message):
    __slots__ = ["round", "task_id"]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class TaskRoundResp(_message.Message):
    __slots__ = ["finished_clients", "joined_clients", "round", "status"]
    FINISHED_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    JOINED_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    finished_clients: _containers.RepeatedScalarFieldContainer[str]
    joined_clients: _containers.RepeatedScalarFieldContainer[str]
    round: int
    status: RoundStatus
    def __init__(self, round: _Optional[int] = ..., status: _Optional[_Union[RoundStatus, str]] = ..., joined_clients: _Optional[_Iterable[str]] = ..., finished_clients: _Optional[_Iterable[str]] = ...) -> None: ...

class VerifyReq(_message.Message):
    __slots__ = ["address", "block_index", "proof", "pub_signals", "samples", "task_id", "weight_size"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BLOCK_INDEX_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    PUB_SIGNALS_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_SIZE_FIELD_NUMBER: _ClassVar[int]
    address: str
    block_index: int
    proof: str
    pub_signals: _containers.RepeatedScalarFieldContainer[str]
    samples: int
    task_id: str
    weight_size: int
    def __init__(self, address: _Optional[str] = ..., task_id: _Optional[str] = ..., weight_size: _Optional[int] = ..., proof: _Optional[str] = ..., pub_signals: _Optional[_Iterable[str]] = ..., block_index: _Optional[int] = ..., samples: _Optional[int] = ...) -> None: ...

class VerifyResp(_message.Message):
    __slots__ = ["tx_hash", "valid"]
    TX_HASH_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    tx_hash: str
    valid: bool
    def __init__(self, tx_hash: _Optional[str] = ..., valid: bool = ...) -> None: ...

class VerifyState(_message.Message):
    __slots__ = ["invalid_clients", "unfinished_clients", "valid"]
    INVALID_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    UNFINISHED_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    invalid_clients: _containers.RepeatedScalarFieldContainer[str]
    unfinished_clients: _containers.RepeatedScalarFieldContainer[str]
    valid: bool
    def __init__(self, unfinished_clients: _Optional[_Iterable[str]] = ..., invalid_clients: _Optional[_Iterable[str]] = ..., valid: bool = ...) -> None: ...

class WeightCommitmentReq(_message.Message):
    __slots__ = ["round", "task_id"]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    round: int
    task_id: str
    def __init__(self, task_id: _Optional[str] = ..., round: _Optional[int] = ...) -> None: ...

class WeightCommitmentResp(_message.Message):
    __slots__ = ["commitment"]
    COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    commitment: str
    def __init__(self, commitment: _Optional[str] = ...) -> None: ...

class RoundStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
