import logging
from typing import List

from delta_node import serialize
from grpclib.client import Channel
from numpy import add

from . import chain_pb2
from .chain_grpc import ChainStub
from .model import (NodeInfo, PublicKeyPair, RoundStatus, SecretShareData,
                    TaskRound)

_logger = logging.getLogger(__name__)


class ChainClient(object):
    def __init__(self, host: str, port: int) -> None:
        self.channel = Channel(host=host, port=port)
        self.stub = ChainStub(self.channel)

    async def join(self, url: str, name: str) -> str:
        req = chain_pb2.JoinReq(url=url, name=name)
        try:
            resp = await self.stub.Join(req)
            return resp.address
        except Exception as e:
            _logger.error(e)
            raise

    async def update_name(self, address: str, name: str):
        req = chain_pb2.UpdateNameReq(address=address, name=name)
        try:
            await self.stub.UpdateName(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def updaet_url(self, address: str, url: str):
        req = chain_pb2.UpdateUrlReq(address=address, url=url)
        try:
            await self.stub.UpdateUrl(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def leave(self, address: str):
        req = chain_pb2.LeaveReq(address=address)
        try:
            await self.stub.Leave(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_node_info(self, address: str) -> NodeInfo:
        req = chain_pb2.NodeInfoReq(address=address)
        try:
            resp = await self.stub.GetNodeInfo(req)
            return NodeInfo(url=resp.url, name=resp.name)
        except Exception as e:
            _logger.error(e)
            raise

    async def create_task(self, address: str, dataset: str, commitment: bytes) -> str:
        hex_commitment = serialize.bytes_to_hex(commitment, max_length=32)
        req = chain_pb2.CreateTaskReq(
            address=address, dataset=dataset, commitment=hex_commitment
        )
        try:
            resp = await self.stub.CreateTask(req)
            return resp.task_id
        except Exception as e:
            _logger.error(e)
            raise

    async def start_round(self, address: str, task_id: str, round: int):
        req = chain_pb2.StartRoundReq(address=address, task_id=task_id, round=round)
        try:
            await self.stub.StartRound(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def join_round(
        self, address: str, task_id: str, round: int, pk1: bytes, pk2: bytes
    ):
        hex_pk1 = serialize.bytes_to_hex(pk1)
        hex_pk2 = serialize.bytes_to_hex(pk2)
        req = chain_pb2.JoinRoundReq(
            address=address, task_id=task_id, round=round, pk1=hex_pk1, pk2=hex_pk2
        )
        try:
            await self.stub.JoinRound(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_task_round(self, task_id: str, round: int) -> TaskRound:
        req = chain_pb2.TaskRoundReq(task_id=task_id, round=round)
        try:
            resp = await self.stub.GetTaskRound(req)
            return TaskRound(
                round=round, status=RoundStatus(resp.status), clients=list(resp.clients)
            )
        except Exception as e:
            _logger.error(e)
            raise

    async def select_candidates(
        self, address: str, task_id: str, round: int, clients: List[str]
    ):
        req = chain_pb2.CandidatesReq(
            address=address, task_id=task_id, round=round, clients=clients
        )
        try:
            await self.stub.SelectCandidates(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_seed_commitment(
        self, address: str, task_id: str, round: int, receiver: str, commitment: bytes
    ):
        hex_commitment = serialize.bytes_to_hex(commitment, max_length=32)
        req = chain_pb2.ShareCommitment(
            address=address,
            task_id=task_id,
            round=round,
            receiver=receiver,
            commitment=hex_commitment,
        )
        try:
            await self.stub.UploadSeedCommitment(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_secret_key_commitment(
        self, address: str, task_id: str, round: int, receiver: str, commitment: bytes
    ):
        hex_commitment = serialize.bytes_to_hex(commitment, max_length=32)
        req = chain_pb2.ShareCommitment(
            address=address,
            task_id=task_id,
            round=round,
            receiver=receiver,
            commitment=hex_commitment,
        )
        try:
            await self.stub.UploadSecretKeyCommitment(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_client_public_keys(
        self, task_id: str, round: int, client: str
    ) -> PublicKeyPair:
        req = chain_pb2.PublicKeyReq(task_id=task_id, round=round, client=client)
        try:
            resp = await self.stub.GetClientPublickKeys(req)
            pk1 = serialize.hex_to_bytes(resp.pk1)
            pk2 = serialize.hex_to_bytes(resp.pk2)
            return PublicKeyPair(pk1, pk2)
        except Exception as e:
            _logger.error(e)
            raise

    async def start_calculation(
        self, address: str, task_id: str, round: int, clients: List[str]
    ):
        req = chain_pb2.CalculationReq(
            address=address, task_id=task_id, round=round, clients=clients
        )
        try:
            await self.stub.StartCalculation(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_result_commitment(
        self, address: str, task_id: str, round: int, commitment: bytes
    ):
        hex_commitment = serialize.bytes_to_hex(commitment, max_length=32)
        req = chain_pb2.ResultCommitment(
            address=address, task_id=task_id, round=round, commitment=hex_commitment
        )
        try:
            await self.stub.UploadResultCommitment(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_result_commitment(
        self, task_id: str, round: int, client: str
    ) -> bytes:
        req = chain_pb2.ResultCommitmentReq(task_id=task_id, round=round, client=client)
        try:
            resp = await self.stub.GetResultCommitment(req)
            return serialize.hex_to_bytes(resp.commitment)
        except Exception as e:
            _logger.error(e)
            raise

    async def start_aggregation(
        self, address: str, task_id: str, round: int, clients: List[str]
    ):
        req = chain_pb2.AggregationReq(
            address=address, task_id=task_id, round=round, clients=clients
        )
        try:
            await self.stub.StartAggregation(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_seed(
        self, address: str, task_id: str, round: int, sender: str, share: bytes
    ):
        hex_share = serialize.bytes_to_hex(share)
        req = chain_pb2.Share(
            address=address,
            task_id=task_id,
            round=round,
            sender=sender,
            share=hex_share,
        )
        try:
            await self.stub.UploadSeed(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def upload_secret_key(
        self, address: str, task_id: str, round: int, sender: str, share: bytes
    ):
        hex_share = serialize.bytes_to_hex(share)
        req = chain_pb2.Share(
            address=address,
            task_id=task_id,
            round=round,
            sender=sender,
            share=hex_share,
        )
        try:
            await self.stub.UploadSecretKey(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_secret_share_data(
        self, task_id: str, round: int, sender: str, receiver: str
    ) -> SecretShareData:
        req = chain_pb2.SecretShareReq(
            task_id=task_id, round=round, sender=sender, receiver=receiver
        )
        try:
            resp = await self.stub.GetSecretShareData(req)
            res = SecretShareData(
                seed=serialize.hex_to_bytes(resp.seed),
                seed_commitment=serialize.hex_to_bytes(resp.seed_commitment),
                secret_key=serialize.hex_to_bytes(resp.secret_key),
                secret_key_commitment=serialize.hex_to_bytes(
                    resp.secret_key_commitment
                ),
            )
            return res
        except Exception as e:
            _logger.error(e)
            raise
