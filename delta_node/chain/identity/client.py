from logging import getLogger
from typing import List, Tuple

from delta_node.entity.identity import Node
from grpc.aio import Channel

from . import identity_pb2 as pb
from .identity_pb2_grpc import IdentityStub

_logger = getLogger(__name__)


class Client(object):
    def __init__(self, ch: Channel) -> None:
        self.stub = IdentityStub(ch)

    async def join(self, url: str, name: str) -> Tuple[str, str]:
        req = pb.JoinReq(url=url, name=name)
        try:
            resp = await self.stub.Join(req)
            return resp.tx_hash, resp.address
        except Exception as e:
            _logger.error(e)
            raise

    async def update_name(self, address: str, name: str) -> str:
        req = pb.UpdateNameReq(address=address, name=name)
        try:
            resp = await self.stub.UpdateName(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def update_url(self, address: str, url: str) -> str:
        req = pb.UpdateUrlReq(address=address, url=url)
        try:
            resp = await self.stub.UpdateUrl(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def leave(self, address: str) -> str:
        req = pb.LeaveReq(address=address)
        try:
            resp = await self.stub.Leave(req)
            return resp.tx_hash
        except Exception as e:
            _logger.error(e)
            raise

    async def get_node_info(self, address: str) -> Node:
        req = pb.NodeInfoReq(address=address)
        try:
            resp = await self.stub.GetNodeInfo(req)
            return Node(url=resp.url, name=resp.name, address=address)
        except Exception as e:
            _logger.error(e)
            raise

    async def get_nodes(self, page: int, page_size: int) -> Tuple[List[Node], int]:
        req = pb.NodeInfosReq(page=page, page_size=page_size)
        try:
            resp = await self.stub.GetNodes(req)
            nodes = [
                Node(address=node.address, url=node.url, name=node.name)
                for node in resp.nodes
            ]
            return nodes, resp.total_count
        except Exception as e:
            _logger.error(e)
            raise
