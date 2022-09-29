"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _RoundStatus:
    ValueType = typing.NewType('ValueType', builtins.int)
    V: typing_extensions.TypeAlias = ValueType
class _RoundStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_RoundStatus.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    STARTED: _RoundStatus.ValueType  # 0
    RUNNING: _RoundStatus.ValueType  # 1
    CALCULATING: _RoundStatus.ValueType  # 2
    AGGREGATING: _RoundStatus.ValueType  # 3
    FINISHED: _RoundStatus.ValueType  # 4
class RoundStatus(_RoundStatus, metaclass=_RoundStatusEnumTypeWrapper):
    pass

STARTED: RoundStatus.ValueType  # 0
RUNNING: RoundStatus.ValueType  # 1
CALCULATING: RoundStatus.ValueType  # 2
AGGREGATING: RoundStatus.ValueType  # 3
FINISHED: RoundStatus.ValueType  # 4
global___RoundStatus = RoundStatus


class CreateTaskReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    DATASET_FIELD_NUMBER: builtins.int
    COMMITMENT_FIELD_NUMBER: builtins.int
    TASK_TYPE_FIELD_NUMBER: builtins.int
    address: typing.Text
    dataset: typing.Text
    commitment: typing.Text
    task_type: typing.Text
    def __init__(self,
        *,
        address: typing.Text = ...,
        dataset: typing.Text = ...,
        commitment: typing.Text = ...,
        task_type: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","commitment",b"commitment","dataset",b"dataset","task_type",b"task_type"]) -> None: ...
global___CreateTaskReq = CreateTaskReq

class CreateTaskResp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TX_HASH_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    tx_hash: typing.Text
    task_id: typing.Text
    def __init__(self,
        *,
        tx_hash: typing.Text = ...,
        task_id: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["task_id",b"task_id","tx_hash",b"tx_hash"]) -> None: ...
global___CreateTaskResp = CreateTaskResp

class FinishTaskReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","task_id",b"task_id"]) -> None: ...
global___FinishTaskReq = FinishTaskReq

class TaskReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    task_id: typing.Text
    def __init__(self,
        *,
        task_id: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["task_id",b"task_id"]) -> None: ...
global___TaskReq = TaskReq

class TaskResp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    URL_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    DATASET_FIELD_NUMBER: builtins.int
    COMMITMENT_FIELD_NUMBER: builtins.int
    TASK_TYPE_FIELD_NUMBER: builtins.int
    FINISHED_FIELD_NUMBER: builtins.int
    address: typing.Text
    url: typing.Text
    task_id: typing.Text
    dataset: typing.Text
    commitment: typing.Text
    task_type: typing.Text
    finished: builtins.bool
    def __init__(self,
        *,
        address: typing.Text = ...,
        url: typing.Text = ...,
        task_id: typing.Text = ...,
        dataset: typing.Text = ...,
        commitment: typing.Text = ...,
        task_type: typing.Text = ...,
        finished: builtins.bool = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","commitment",b"commitment","dataset",b"dataset","finished",b"finished","task_id",b"task_id","task_type",b"task_type","url",b"url"]) -> None: ...
global___TaskResp = TaskResp

class StartRoundReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","round",b"round","task_id",b"task_id"]) -> None: ...
global___StartRoundReq = StartRoundReq

class JoinRoundReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    PK1_FIELD_NUMBER: builtins.int
    PK2_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    pk1: typing.Text
    pk2: typing.Text
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        pk1: typing.Text = ...,
        pk2: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","pk1",b"pk1","pk2",b"pk2","round",b"round","task_id",b"task_id"]) -> None: ...
global___JoinRoundReq = JoinRoundReq

class TaskRoundReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    task_id: typing.Text
    round: builtins.int
    def __init__(self,
        *,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["round",b"round","task_id",b"task_id"]) -> None: ...
global___TaskRoundReq = TaskRoundReq

class TaskRoundResp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ROUND_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    CLIENTS_FIELD_NUMBER: builtins.int
    round: builtins.int
    status: global___RoundStatus.ValueType
    @property
    def clients(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        round: builtins.int = ...,
        status: global___RoundStatus.ValueType = ...,
        clients: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["clients",b"clients","round",b"round","status",b"status"]) -> None: ...
global___TaskRoundResp = TaskRoundResp

class CandidatesReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    CLIENTS_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    @property
    def clients(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        clients: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","clients",b"clients","round",b"round","task_id",b"task_id"]) -> None: ...
global___CandidatesReq = CandidatesReq

class ShareCommitment(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    RECEIVERS_FIELD_NUMBER: builtins.int
    COMMITMENTS_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    @property
    def receivers(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    @property
    def commitments(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        receivers: typing.Optional[typing.Iterable[typing.Text]] = ...,
        commitments: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","commitments",b"commitments","receivers",b"receivers","round",b"round","task_id",b"task_id"]) -> None: ...
global___ShareCommitment = ShareCommitment

class PublicKeyReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    CLIENTS_FIELD_NUMBER: builtins.int
    task_id: typing.Text
    round: builtins.int
    @property
    def clients(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        clients: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["clients",b"clients","round",b"round","task_id",b"task_id"]) -> None: ...
global___PublicKeyReq = PublicKeyReq

class PublicKeys(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    PK1_FIELD_NUMBER: builtins.int
    PK2_FIELD_NUMBER: builtins.int
    pk1: typing.Text
    pk2: typing.Text
    def __init__(self,
        *,
        pk1: typing.Text = ...,
        pk2: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["pk1",b"pk1","pk2",b"pk2"]) -> None: ...
global___PublicKeys = PublicKeys

class PublicKeyResp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    KEYS_FIELD_NUMBER: builtins.int
    @property
    def keys(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___PublicKeys]: ...
    def __init__(self,
        *,
        keys: typing.Optional[typing.Iterable[global___PublicKeys]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["keys",b"keys"]) -> None: ...
global___PublicKeyResp = PublicKeyResp

class CalculationReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    CLIENTS_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    @property
    def clients(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        clients: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","clients",b"clients","round",b"round","task_id",b"task_id"]) -> None: ...
global___CalculationReq = CalculationReq

class ResultCommitment(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    COMMITMENT_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    commitment: typing.Text
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        commitment: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","commitment",b"commitment","round",b"round","task_id",b"task_id"]) -> None: ...
global___ResultCommitment = ResultCommitment

class ResultCommitmentReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    CLIENT_FIELD_NUMBER: builtins.int
    task_id: typing.Text
    round: builtins.int
    client: typing.Text
    def __init__(self,
        *,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        client: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["client",b"client","round",b"round","task_id",b"task_id"]) -> None: ...
global___ResultCommitmentReq = ResultCommitmentReq

class ResultCommitmentResp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    COMMITMENT_FIELD_NUMBER: builtins.int
    commitment: typing.Text
    def __init__(self,
        *,
        commitment: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["commitment",b"commitment"]) -> None: ...
global___ResultCommitmentResp = ResultCommitmentResp

class AggregationReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    CLIENTS_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    @property
    def clients(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        clients: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","clients",b"clients","round",b"round","task_id",b"task_id"]) -> None: ...
global___AggregationReq = AggregationReq

class Share(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    SENDERS_FIELD_NUMBER: builtins.int
    SHARES_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    @property
    def senders(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    @property
    def shares(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        senders: typing.Optional[typing.Iterable[typing.Text]] = ...,
        shares: typing.Optional[typing.Iterable[typing.Text]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","round",b"round","senders",b"senders","shares",b"shares","task_id",b"task_id"]) -> None: ...
global___Share = Share

class SecretShareReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    SENDERS_FIELD_NUMBER: builtins.int
    RECEIVER_FIELD_NUMBER: builtins.int
    task_id: typing.Text
    round: builtins.int
    @property
    def senders(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]: ...
    receiver: typing.Text
    def __init__(self,
        *,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        senders: typing.Optional[typing.Iterable[typing.Text]] = ...,
        receiver: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["receiver",b"receiver","round",b"round","senders",b"senders","task_id",b"task_id"]) -> None: ...
global___SecretShareReq = SecretShareReq

class SecretShareData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    SEED_FIELD_NUMBER: builtins.int
    SEED_COMMITMENT_FIELD_NUMBER: builtins.int
    SECRET_KEY_FIELD_NUMBER: builtins.int
    SECRET_KEY_COMMITMENT_FIELD_NUMBER: builtins.int
    seed: typing.Text
    seed_commitment: typing.Text
    secret_key: typing.Text
    secret_key_commitment: typing.Text
    def __init__(self,
        *,
        seed: typing.Optional[typing.Text] = ...,
        seed_commitment: typing.Optional[typing.Text] = ...,
        secret_key: typing.Optional[typing.Text] = ...,
        secret_key_commitment: typing.Optional[typing.Text] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_secret_key",b"_secret_key","_secret_key_commitment",b"_secret_key_commitment","_seed",b"_seed","_seed_commitment",b"_seed_commitment","secret_key",b"secret_key","secret_key_commitment",b"secret_key_commitment","seed",b"seed","seed_commitment",b"seed_commitment"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_secret_key",b"_secret_key","_secret_key_commitment",b"_secret_key_commitment","_seed",b"_seed","_seed_commitment",b"_seed_commitment","secret_key",b"secret_key","secret_key_commitment",b"secret_key_commitment","seed",b"seed","seed_commitment",b"seed_commitment"]) -> None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_secret_key",b"_secret_key"]) -> typing.Optional[typing_extensions.Literal["secret_key"]]: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_secret_key_commitment",b"_secret_key_commitment"]) -> typing.Optional[typing_extensions.Literal["secret_key_commitment"]]: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_seed",b"_seed"]) -> typing.Optional[typing_extensions.Literal["seed"]]: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_seed_commitment",b"_seed_commitment"]) -> typing.Optional[typing_extensions.Literal["seed_commitment"]]: ...
global___SecretShareData = SecretShareData

class SecretShareResp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    SHARES_FIELD_NUMBER: builtins.int
    @property
    def shares(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___SecretShareData]: ...
    def __init__(self,
        *,
        shares: typing.Optional[typing.Iterable[global___SecretShareData]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["shares",b"shares"]) -> None: ...
global___SecretShareResp = SecretShareResp

class EndRoundReq(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ADDRESS_FIELD_NUMBER: builtins.int
    TASK_ID_FIELD_NUMBER: builtins.int
    ROUND_FIELD_NUMBER: builtins.int
    address: typing.Text
    task_id: typing.Text
    round: builtins.int
    def __init__(self,
        *,
        address: typing.Text = ...,
        task_id: typing.Text = ...,
        round: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["address",b"address","round",b"round","task_id",b"task_id"]) -> None: ...
global___EndRoundReq = EndRoundReq
