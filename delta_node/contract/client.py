from typing import Iterable, List
import grpc

from . import chain_pb2, chain_pb2_grpc
from .utils import Event, Node


class ChainClient(object):
    def __init__(self, address: str) -> None:
        self._channel = grpc.insecure_channel(address)
        self._stub = chain_pb2_grpc.ChainStub(self._channel)

    def get_nodes(self, page: int = 1, page_size: int = 20) -> List[Node]:
        req = chain_pb2.NodesReq(page=page, page_size=page_size)
        resp = self._stub.GetNodes(req)
        nodes = [Node(id=node.id, url=node.url) for node in resp.nodes]
        return nodes

    def register_node(self, url: str) -> str:
        req = chain_pb2.NodeReq(url=url)
        resp = self._stub.RegisterNode(req)
        return resp.node_id

    def create_task(self, node_id: str, task_name: str) -> int:
        req = chain_pb2.TaskReq(node_id=node_id, name=task_name)
        resp = self._stub.CreateTask(req)
        return resp.task_id

    def join_task(self, node_id: str, task_id: int) -> bool:
        req = chain_pb2.JoinReq(node_id=node_id, task_id=task_id)
        resp = self._stub.JoinTask(req)
        return resp.success

    def start_round(self, node_id: str, task_id: int) -> int:
        req = chain_pb2.RoundReq(node_id=node_id, task_id=task_id)
        resp = self._stub.StartRound(req)
        return resp.round_id

    def publish_pub_key(
        self, node_id: str, task_id: int, round_id: int, pub_key: str
    ) -> bool:
        req = chain_pb2.KeyReq(
            node_id=node_id, task_id=task_id, round_id=round_id, key=pub_key
        )
        resp = self._stub.PublishPubKey(req)
        return resp.success

    def events(self, node_id: str) -> Iterable[Event]:
        req = chain_pb2.EventReq(node_id=node_id)
        for e in self._stub.Events(req):
            event = Event(
                name=e.name,
                address=e.address,
                url=e.url,
                task_id=e.task_id,
                epoch=e.epoch,
                key=e.key,
            )
            yield event
