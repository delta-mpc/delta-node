import logging
from typing import AsyncGenerator, List, Tuple

from delta_node import entity, serialize, entity
from grpclib.client import Channel

from . import chain_pb2
from .chain_grpc import ChainStub

_logger = logging.getLogger(__name__)


class ChainClient(object):
    def __init__(self, ch: Channel) -> None:
        self.stub = ChainStub(ch)

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

    async def get_node_info(self, address: str) -> entity.Node:
        req = chain_pb2.NodeInfoReq(address=address)
        try:
            resp = await self.stub.GetNodeInfo(req)
            return entity.Node(url=resp.url, name=resp.name, address=address)
        except Exception as e:
            _logger.error(e)
            raise

    async def create_task(
        self, address: str, dataset: str, commitment: bytes, task_type: str
    ) -> str:
        hex_commitment = serialize.bytes_to_hex(commitment, max_length=32)
        req = chain_pb2.CreateTaskReq(
            address=address,
            dataset=dataset,
            commitment=hex_commitment,
            task_type=task_type,
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

    async def get_task_round(self, task_id: str, round: int) -> entity.TaskRound:
        req = chain_pb2.TaskRoundReq(task_id=task_id, round=round)
        try:
            resp = await self.stub.GetTaskRound(req)
            return entity.TaskRound(
                task_id=task_id,
                round=round,
                status=entity.RoundStatus(resp.status),
                clients=list(resp.clients),
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
        self,
        address: str,
        task_id: str,
        round: int,
        receivers: List[str],
        commitments: List[bytes],
    ):
        hex_commitments = [
            serialize.bytes_to_hex(commitment, max_length=32)
            for commitment in commitments
        ]
        req = chain_pb2.ShareCommitment(
            address=address,
            task_id=task_id,
            round=round,
            receivers=receivers,
            commitments=hex_commitments,
        )
        try:
            await self.stub.UploadSeedCommitment(req)
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
    ):
        hex_commitments = [
            serialize.bytes_to_hex(commitment, max_length=32)
            for commitment in commitments
        ]
        req = chain_pb2.ShareCommitment(
            address=address,
            task_id=task_id,
            round=round,
            receivers=receivers,
            commitments=hex_commitments,
        )
        try:
            await self.stub.UploadSecretKeyCommitment(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_client_public_keys(
        self, task_id: str, round: int, clients: List[str]
    ) -> List[Tuple[bytes, bytes]]:
        req = chain_pb2.PublicKeyReq(task_id=task_id, round=round, clients=clients)
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
        self,
        address: str,
        task_id: str,
        round: int,
        senders: List[str],
        shares: List[bytes],
    ):
        hex_shares = [serialize.bytes_to_hex(share) for share in shares]
        req = chain_pb2.Share(
            address=address,
            task_id=task_id,
            round=round,
            senders=senders,
            shares=hex_shares,
        )
        try:
            await self.stub.UploadSeed(req)
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
    ):
        hex_shares = [serialize.bytes_to_hex(share) for share in shares]
        req = chain_pb2.Share(
            address=address,
            task_id=task_id,
            round=round,
            senders=senders,
            shares=hex_shares,
        )
        try:
            await self.stub.UploadSecretKey(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_secret_share_datas(
        self, task_id: str, round: int, senders: List[str], receiver: str
    ) -> List[entity.SecretShareData]:
        req = chain_pb2.SecretShareReq(
            task_id=task_id, round=round, senders=senders, receiver=receiver
        )
        try:
            resp = await self.stub.GetSecretShareDatas(req)
            res = [
                entity.SecretShareData(
                    seed=serialize.hex_to_bytes(share.seed),
                    seed_commitment=serialize.hex_to_bytes(share.seed_commitment),
                    secret_key=serialize.hex_to_bytes(share.secret_key),
                    secret_key_commitment=serialize.hex_to_bytes(
                        share.secret_key_commitment
                    ),
                )
                for share in resp.shares
            ]
            return res
        except Exception as e:
            _logger.error(e)
            raise

    async def end_round(self, address: str, task_id: str, round: int):
        req = chain_pb2.EndRoundReq(address=address, task_id=task_id, round=round)
        try:
            await self.stub.EndRound(req)
        except Exception as e:
            _logger.error(e)
            raise

    async def subscribe(self, address: str) -> AsyncGenerator[entity.Event, None]:
        req = chain_pb2.EventReq(address=address)
        try:
            async with self.stub.Subscribe.open() as stream:
                await stream.send_message(req, end=True)
                async for event in stream:
                    event_type = event.WhichOneof("event")
                    if event_type == "task_create":
                        yield entity.TaskCreateEvent(
                            address=event.task_create.address,
                            task_id=event.task_create.task_id,
                            dataset=event.task_create.dataset,
                            url=event.task_create.url,
                            commitment=serialize.hex_to_bytes(
                                event.task_create.commitment
                            ),
                            task_type=event.task_create.task_type,
                        )
                    elif event_type == "round_started":
                        yield entity.RoundStartedEvent(
                            task_id=event.round_started.task_id,
                            round=event.round_started.round,
                        )
                    elif event_type == "partner_selected":
                        yield entity.PartnerSelectedEvent(
                            task_id=event.partner_selected.task_id,
                            round=event.partner_selected.round,
                            addrs=list(event.partner_selected.addrs),
                        )
                    elif event_type == "calculation_started":
                        yield entity.CalculationStartedEvent(
                            task_id=event.calculation_started.task_id,
                            round=event.calculation_started.round,
                            addrs=list(event.calculation_started.addrs),
                        )
                    elif event_type == "aggregation_started":
                        yield entity.AggregationStartedEvent(
                            task_id=event.aggregation_started.task_id,
                            round=event.aggregation_started.round,
                            addrs=list(event.aggregation_started.addrs),
                        )
                    else:
                        yield entity.RoundEndedEvent(
                            task_id=event.round_ended.task_id,
                            round=event.round_ended.round,
                        )
        except Exception as e:
            _logger.error(e)
            raise
