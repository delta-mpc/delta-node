from logging import getLogger

from delta_node import serialize
from grpclib.client import Channel

from . import datahub_pb2 as pb
from .datahub_grpc import DataHubStub

_logger = getLogger(__name__)


class Client(object):
    def __init__(self, ch: Channel) -> None:
        self.stub = DataHubStub(ch)

    async def register(
        self, address: str, name: str, index: int, commitment: bytes
    ) -> str:
        req = pb.RegisterReq(
            address=address,
            name=name,
            index=index,
            commitment=serialize.bytes_to_hex(commitment, length=32),
        )
        try:
            res = await self.stub.Register(req)
            return res.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_data_commitment(self, address: str, name: str, index: int) -> bytes:
        req = pb.DataCommitmentReq(
            address=address,
            name=name,
            index=index
        )
        try:
            res = await self.stub.GetDataCommitment(req)
            return serialize.hex_to_bytes(res.commitment, length=32)
        except Exception as e:
            _logger.error(e)
            raise
