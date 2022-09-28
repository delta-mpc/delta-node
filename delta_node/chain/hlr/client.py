from logging import getLogger
from typing import List, Tuple

from delta_node import serialize
from delta_node.entity import TaskStatus
from delta_node.entity.hlr import (RoundStatus, RunnerTask, SecretShareData,
                                   TaskRound, VerifierState)
from grpclib.client import Channel

from . import hlr_pb2 as pb
from .hlr_grpc import HLRStub

_logger = getLogger(__name__)


class Client(object):
    def __init__(self, ch: Channel) -> None:
        self.stub = HLRStub(ch)

    async def create_task(
        self,
        address: str,
        dataset: str,
        commitment: bytes,
        enable_verify: bool,
        tolerance: int,
    ) -> Tuple[str, str]:
        hex_commitment = serialize.bytes_to_hex(commitment, length=32)
        req = pb.CreateTaskReq(
            address=address,
            dataset=dataset,
            commitment=hex_commitment,
            enable_verify=enable_verify,
            tolerance=tolerance,
        )
        try:
            resp = await self.stub.CreateTask(req)
            return resp.tx_hash, resp.task_id
        except Exception as e:
            _logger.error(e)
            raise

    async def finish_task(self, address: str, task_id: str) -> str:
        req = pb.FinishTaskReq(address=address, task_id=task_id)
        try:
            resp = await self.stub.FinishTask(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_task(self, task_id: str) -> RunnerTask:
        req = pb.TaskReq(task_id=task_id)
        try:
            resp = await self.stub.GetTask(req)
            status = TaskStatus.FINISHED if resp.finished else TaskStatus.RUNNING
            res = RunnerTask(
                creator=resp.address,
                task_id=resp.task_id,
                dataset=resp.dataset,
                commitment=serialize.hex_to_bytes(resp.commitment),
                url=resp.url,
                type=resp.task_type,
                status=status,
                enable_verify=resp.enable_verify,
                tolerance=resp.tolerance,
            )
            return res
        except Exception as e:
            _logger.error(e)
            raise

    async def start_round(
        self, address: str, task_id: str, round: int, weight_commitment: bytes
    ) -> str:
        req = pb.StartRoundReq(
            address=address,
            task_id=task_id,
            round=round,
            weight_commitment=serialize.bytes_to_hex(weight_commitment, length=32),
        )
        try:
            resp = await self.stub.StartRound(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def join_round(
        self, address: str, task_id: str, round: int, pk1: bytes, pk2: bytes
    ) -> str:
        hex_pk1 = serialize.bytes_to_hex(pk1)
        hex_pk2 = serialize.bytes_to_hex(pk2)
        req = pb.JoinRoundReq(
            address=address, task_id=task_id, round=round, pk1=hex_pk1, pk2=hex_pk2
        )
        try:
            resp = await self.stub.JoinRound(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_task_round(self, task_id: str, round: int) -> TaskRound:
        req = pb.TaskRoundReq(task_id=task_id, round=round)
        try:
            weight_commitment = await self.get_weight_commitment(task_id, round)
            resp = await self.stub.GetTaskRound(req)
            return TaskRound(
                task_id=task_id,
                round=round,
                status=RoundStatus(resp.status),
                joined_clients=list(resp.joined_clients),
                finished_clients=list(resp.finished_clients),
                weight_commitment=weight_commitment,
            )
        except Exception as e:
            _logger.error(e)
            raise

    async def get_weight_commitment(self, task_id: str, round: int) -> bytes:
        req = pb.WeightCommitmentReq(task_id=task_id, round=round)
        try:
            resp = await self.stub.GetWeightCommitment(req)
            return serialize.hex_to_bytes(resp.commitment, 32)
        except Exception as e:
            _logger.error(e)
            raise

    async def select_candidates(
        self, address: str, task_id: str, round: int, clients: List[str]
    ) -> str:
        req = pb.CandidatesReq(
            address=address, task_id=task_id, round=round, clients=clients
        )
        try:
            resp = await self.stub.SelectCandidates(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_seed_commitment(
        self,
        address: str,
        task_id: str,
        round: int,
        receivers: List[str],
        commitments: List[bytes],
    ) -> str:
        hex_commitments = [
            serialize.bytes_to_hex(commitment, length=32) for commitment in commitments
        ]
        req = pb.ShareCommitment(
            address=address,
            task_id=task_id,
            round=round,
            receivers=receivers,
            commitments=hex_commitments,
        )
        try:
            resp = await self.stub.UploadSeedCommitment(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_secret_key_commitment(
        self,
        address: str,
        task_id: str,
        round: int,
        receivers: List[str],
        commitments: List[bytes],
    ) -> str:
        hex_commitments = [
            serialize.bytes_to_hex(commitment, length=32) for commitment in commitments
        ]
        req = pb.ShareCommitment(
            address=address,
            task_id=task_id,
            round=round,
            receivers=receivers,
            commitments=hex_commitments,
        )
        try:
            resp = await self.stub.UploadSecretKeyCommitment(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_client_public_keys(
        self, task_id: str, round: int, clients: List[str]
    ) -> List[Tuple[bytes, bytes]]:
        req = pb.PublicKeyReq(task_id=task_id, round=round, clients=clients)
        try:
            resp = await self.stub.GetClientPublickKeys(req)
            res = [
                (serialize.hex_to_bytes(keys.pk1), serialize.hex_to_bytes(keys.pk2))
                for keys in resp.keys
            ]
            return res
        except Exception as e:
            _logger.error(e)
            raise

    async def start_calculation(
        self, address: str, task_id: str, round: int, clients: List[str]
    ) -> str:
        req = pb.CalculationReq(
            address=address, task_id=task_id, round=round, clients=clients
        )
        try:
            resp = await self.stub.StartCalculation(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_result_commitment(
        self, address: str, task_id: str, round: int, commitment: bytes
    ) -> str:
        hex_commitment = serialize.bytes_to_hex(commitment, length=32)
        req = pb.ResultCommitment(
            address=address, task_id=task_id, round=round, commitment=hex_commitment
        )
        try:
            resp = await self.stub.UploadResultCommitment(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_result_commitment(
        self, task_id: str, round: int, client: str
    ) -> bytes:
        req = pb.ResultCommitmentReq(task_id=task_id, round=round, client=client)
        try:
            resp = await self.stub.GetResultCommitment(req)
            return serialize.hex_to_bytes(resp.commitment)
        except Exception as e:
            _logger.error(e)
            raise

    async def start_aggregation(
        self, address: str, task_id: str, round: int, clients: List[str]
    ) -> str:
        req = pb.AggregationReq(
            address=address, task_id=task_id, round=round, clients=clients
        )
        try:
            resp = await self.stub.StartAggregation(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_seed(
        self,
        address: str,
        task_id: str,
        round: int,
        senders: List[str],
        shares: List[bytes],
    ) -> str:
        hex_shares = [serialize.bytes_to_hex(share) for share in shares]
        req = pb.Share(
            address=address,
            task_id=task_id,
            round=round,
            senders=senders,
            shares=hex_shares,
        )
        try:
            resp = await self.stub.UploadSeed(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_secret_key(
        self,
        address: str,
        task_id: str,
        round: int,
        senders: List[str],
        shares: List[bytes],
    ) -> str:
        hex_shares = [serialize.bytes_to_hex(share) for share in shares]
        req = pb.Share(
            address=address,
            task_id=task_id,
            round=round,
            senders=senders,
            shares=hex_shares,
        )
        try:
            resp = await self.stub.UploadSecretKey(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_secret_share_datas(
        self, task_id: str, round: int, senders: List[str], receiver: str
    ) -> List[SecretShareData]:
        req = pb.SecretShareReq(
            task_id=task_id, round=round, senders=senders, receiver=receiver
        )
        try:
            resp = await self.stub.GetSecretShareDatas(req)
            res = [
                SecretShareData(
                    sender=sender,
                    receiver=receiver,
                    seed=serialize.hex_to_bytes(share.seed),
                    seed_commitment=serialize.hex_to_bytes(share.seed_commitment),
                    secret_key=serialize.hex_to_bytes(share.secret_key),
                    secret_key_commitment=serialize.hex_to_bytes(
                        share.secret_key_commitment
                    ),
                )
                for sender, share in zip(senders, resp.shares)
            ]
            return res
        except Exception as e:
            _logger.error(e)
            raise

    async def end_round(self, address: str, task_id: str, round: int) -> str:
        req = pb.EndRoundReq(address=address, task_id=task_id, round=round)
        try:
            resp = await self.stub.EndRound(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def verify(
        self,
        address: str,
        task_id: str,
        weight_size: int,
        proof: str,
        pub_signals: List[str],
        block_index: int,
        samples: int,
    ) -> Tuple[str, bool]:
        req = pb.VerifyReq(
            address=address,
            task_id=task_id,
            weight_size=weight_size,
            proof=proof,
            pub_signals=pub_signals,
            block_index=block_index,
            samples=samples,
        )
        try:
            resp = await self.stub.Verify(req)
            return resp.tx_hash, resp.valid
        except Exception as e:
            _logger.error(e)
            raise

    async def get_verifier_state(self, task_id: str) -> VerifierState:
        req = pb.TaskReq(task_id=task_id)
        try:
            resp = await self.stub.GetVerifierState(req)
            return VerifierState(
                unfinished_clients=list(resp.unfinished_clients),
                invalid_clients=list(resp.invalid_clients),
                valid=resp.valid
            )
        except Exception as e:
            _logger.error(e)
            raise

    async def confirm_verification(self, address: str, task_id: str) -> str:
        req = pb.ConfirmReq(
            address=address,
            task_id=task_id
        )
        try:
            resp = await self.stub.ConfirmVerification(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

