from .event_filter import EventFilter
from .client import ChainClient
from .event import Event
from .. import config, node


__all__ = [
    "register_node",
    "create_task",
    "join_task",
    "start_round",
    "publish_pub_key",
    "Event",
    "EventFilter",
    "new_event_filter",
]

_client = ChainClient(config.chain_address)


def register_node(url: str) -> str:
    return _client.register_node(url)


def create_task(node_id: str, task_name: str) -> int:
    return _client.create_task(node_id, task_name)


def join_task(node_id: str, task_id: int) -> bool:
    return _client.join_task(node_id, task_id)


def start_round(node_id: str, task_id: int) -> int:
    return _client.start_round(node_id, task_id)


def publish_pub_key(node_id: str, task_id: int, round_id: int, pub_key: str):
    return _client.publish_pub_key(node_id, task_id, round_id, pub_key)


def new_event_filter() -> EventFilter:
    node_id = node.get_node_id()
    return EventFilter(node_id, _client)
