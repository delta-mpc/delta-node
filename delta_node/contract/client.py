import logging
from typing import Iterable, List
import grpc

from . import chain_pb2, chain_pb2_grpc
from .utils import Event, Node


_logger = logging.getLogger(__name__)


class ChainClient(object):
    def __init__(self, address: str) -> None:
        self._channel = grpc.insecure_channel(address)
        self._stub = chain_pb2_grpc.ChainStub(self._channel)

        self._subscribe_futures = {}

    def get_nodes(self, page: int = 1, page_size: int = 20) -> List[Node]:
        req = chain_pb2.NodesReq(page=page, page_size=page_size)
        try:
            resp = self._stub.GetNodes(req)
            nodes = [Node(id=node.id, url=node.url) for node in resp.nodes]
            return nodes
        except grpc.RpcError as e:
            _logger.error(e)
            raise

    def register_node(self, url: str) -> str:
        req = chain_pb2.NodeReq(url=url)
        try:
            resp = self._stub.RegisterNode(req)
            return resp.node_id
        except grpc.RpcError as e:
            _logger.error(e)
            raise
        
    def create_task(self, node_id: str, task_name: str) -> int:
        req = chain_pb2.TaskReq(node_id=node_id, name=task_name)
        try:
            resp = self._stub.CreateTask(req)
            return resp.task_id
        except grpc.RpcError as e:
            _logger.error(e)
            raise

    def join_task(self, node_id: str, task_id: int) -> bool:
        req = chain_pb2.JoinReq(node_id=node_id, task_id=task_id)
        try:
            resp = self._stub.JoinTask(req)
            return resp.success
        except grpc.RpcError as e:
            _logger.error(e)
            raise

    def start_round(self, node_id: str, task_id: int) -> int:
        req = chain_pb2.RoundReq(node_id=node_id, task_id=task_id)
        try:
            resp = self._stub.StartRound(req)
            return resp.round_id
        except grpc.RpcError as e:
            _logger.error(e)
            raise

    def publish_pub_key(
        self, node_id: str, task_id: int, round_id: int, pub_key: str
    ) -> bool:
        req = chain_pb2.KeyReq(
            node_id=node_id, task_id=task_id, round_id=round_id, key=pub_key
        )
        try:
            resp = self._stub.PublishPubKey(req)
            return resp.success
        except grpc.RpcError as e:
            _logger.error(e)
            raise

    def subscribe(self, node_id: str) -> Iterable[Event]:
        req = chain_pb2.EventReq(node_id=node_id)
        fut = self._stub.Events(req)
        self._subscribe_futures[node_id] = fut
        try:
            for e in fut:
                event = Event(
                    name=e.name,
                    address=e.address,
                    url=e.url,
                    task_id=e.task_id,
                    epoch=e.epoch,
                    key=e.key,
                )
                yield event
        except grpc.RpcError as e:
            _logger.error(e)

    def unsubscribe(self, node_id: str):
        _logger.info("unsubsribe events")
        fut = self._subscribe_futures[node_id]
        fut.cancel()
