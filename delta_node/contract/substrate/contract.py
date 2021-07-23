from . import mpc_pb2
from typing import Optional

from .channel import stub
from ... import serialize

from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

__all__ = [
    "register_node",
    "create_task",
    "join_task",
    "start_round",
    "publish_pub_key",
]


class NoneRespError(Exception):
    def __init__(self):
        pass


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(NoneRespError),
)
def register_node(url: str) -> str:
    req = mpc_pb2.RegisterNodeRequest(url=url)
    e: Optional[mpc_pb2.EventResponse] = None
    for event in stub.registerNode(req):
        e = event
        break
    if e is None:
        raise NoneRespError
    return e.address  # type: ignore


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(NoneRespError),
)
def create_task(node_id: str, task_name: str) -> int:
    req = mpc_pb2.RegisterTaskRequest()
    e: Optional[mpc_pb2.EventResponse] = None
    for event in stub.registerTask(req):
        e = event
        break
    if e is None:
        raise NoneRespError
    return e.taskId  # type: ignore


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(NoneRespError),
)
def join_task(node_id: str, task_id: int) -> bool:
    req = mpc_pb2.JoinTaskRequest(task_id=task_id)
    e: Optional[mpc_pb2.EventResponse] = None
    for event in stub.joinTask(req):
        e = event
        break
    if e is None:
        raise NoneRespError
    return e.taskId == task_id  # type: ignore


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(NoneRespError),
)
def start_round(node_id: str, task_id: int) -> int:
    req = mpc_pb2.TrainRequest(task_id=task_id)
    e: Optional[mpc_pb2.EventResponse] = None
    for event in stub.train(req):
        e = event
        break
    if e is None:
        raise NoneRespError
    return e.epoch  # type: ignore


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(NoneRespError),
)
def publish_pub_key(node_id: str, task_id: int, round_id: int, pub_key: str):
    req = mpc_pb2.KeyRequest(
        task_id=task_id, epoch=round_id, key=serialize.hex_str_to_bytes(pub_key)
    )
    e: Optional[mpc_pb2.EventResponse] = None
    for event in stub.key(req):
        e = event
        break
    if e is None:
        raise NoneRespError
    return e.taskId == task_id and e.epoch == round_id and e.key == pub_key  # type: ignore
