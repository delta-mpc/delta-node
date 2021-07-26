import logging
from collections import defaultdict
from concurrent import futures
from queue import Queue, Empty
from typing import Dict, List, Optional, Set
from threading import Condition, Lock
from functools import wraps
import time

import grpc

from . import commu_pb2_grpc
from .common import Data, Mode, err_msg, split_data


def check_client(f):
    @wraps(f)
    def impl(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            key = e.args[0]
            raise RuntimeError(f"client {key} is not active now")

    return impl


class CommuServer(commu_pb2_grpc.CommuServicer):
    def __init__(
        self, local_id: str, host: str, port: int, max_workers: int = 4
    ) -> None:
        super().__init__()
        self._id = local_id
        self._active_clients: Set[str] = set()
        self._send_queues: Dict[str, Queue] = {}
        self._recv_queues: Dict[str, Queue] = {}
        self._client_actions: Dict[str, Queue] = {}

        self._logger = logging.getLogger(__name__)

        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self._server.add_insecure_port(f"{host}:{port}")

        self._client_condition = Condition(Lock())

    def call(self, request_iterator, context):
        remote_id = ""
        frame_id = 0
        try:
            while True:
                if len(remote_id) == 0:
                    msg = next(request_iterator)
                    remote_id = msg.src
                    if msg.type != "syn":
                        err = "first msg should be syn type"
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id, err)
                        return
                    if not msg.eof:
                        err = "syn eof should be true"
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id, err)
                        return
                    if msg.frame_id != frame_id:
                        err = f"syn frame_id should be 0, but got {msg.frame_id}"
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id, err)
                        return
                    frame_id += 1
                    with self._client_condition:
                        self._active_clients.add(remote_id)
                        self._send_queues[remote_id] = Queue()
                        self._recv_queues[remote_id] = Queue()
                        self._client_actions[remote_id] = Queue()
                        self._client_condition.notify_all()
                    self._logger.debug(frame_id)
                    continue

                mode = self._client_actions[remote_id].get(block=True)
                if mode == Mode.RECV:
                    eof = False
                    buffer = []
                    src = ""
                    dst = ""
                    type = ""
                    name = ""
                    while not eof:
                        msg = next(request_iterator)
                        if msg.type == "err":
                            err = msg.content.decode("utf-8")
                            self._logger.error(err)
                            return

                        if msg.frame_id != frame_id:
                            err = f"msg frame id should be {frame_id}, but got {msg.frame_id}"
                            self._logger.error(err)
                            yield err_msg(self._id, remote_id, frame_id, err)
                            return
                        # check sequence consistence
                        if len(type) == 0:
                            type = msg.type
                        elif type != msg.type:
                            err = (
                                f"msg type should not be changed in continuous sequence"
                            )
                            self._logger.error(err)
                            yield err_msg(self._id, remote_id, frame_id + 1, err)
                            return
                        if len(name) == 0:
                            name = msg.name
                        elif name != msg.name:
                            err = (
                                f"msg name should not be changed in continuous sequence"
                            )
                            self._logger.error(err)
                            yield err_msg(self._id, remote_id, frame_id + 1, err)
                            return
                        if len(src) == 0:
                            src = msg.src
                        elif src != msg.src:
                            err = (
                                f"msg src should not be changed in continuous sequence"
                            )
                            self._logger.error(err)
                            yield err_msg(self._id, remote_id, frame_id + 1, err)
                            return
                        if len(dst) == 0:
                            dst = msg.dst
                        elif dst != msg.dst:
                            err = (
                                f"msg dst should not be changed in continuous sequence"
                            )
                            self._logger.error(err)
                            yield err_msg(self._id, remote_id, frame_id + 1, err)
                            return

                        if len(buffer) == msg.sequence:
                            buffer.append(msg.content)
                        else:
                            err = f"msg sequence should be {len(buffer)}, but got {msg.sequence}"
                            self._logger.error(err)
                            yield err_msg(self._id, remote_id, frame_id + 1, err)
                            return
                        eof = msg.eof

                    data = Data(
                        src=src, dst=dst, type=type, name=name, content=b"".join(buffer)
                    )
                    self._recv_queues[remote_id].put(data)
                    frame_id += 1
                    self._logger.debug(frame_id)

                elif mode == Mode.SEND:
                    data = self._send_queues[remote_id].get()
                    self._logger.debug(data)
                    for msg in split_data(frame_id, data):
                        yield msg
                    frame_id += 1
                    self._logger.debug(frame_id)
                elif mode == Mode.FIN:
                    return
        finally:
            if len(remote_id) > 0 and remote_id in self._active_clients:
                self._active_clients.remove(remote_id)
                self._send_queues.pop(remote_id)
                self._recv_queues.pop(remote_id)
                self._client_actions.pop(remote_id)

    def wait_for_connection(self, target: str, timeout: Optional[float] = None):
        with self._client_condition:
            self._client_condition.wait_for(
                lambda: target in self._active_clients, timeout
            )

    @check_client
    def send(self, target: str, data: Data):
        self._client_actions[target].put(Mode.SEND)
        self._send_queues[target].put(data)

    @check_client
    def recv(self, target: str, timeout: Optional[float] = None) -> Data:
        self._client_actions[target].put(Mode.RECV)
        return self._recv_queues[target].get(timeout=timeout)

    @check_client
    def close(self, target: str):
        self._client_actions[target].put(Mode.FIN)

    @check_client
    def close_all(self):
        for client in self._client_actions:
            self._client_actions[client].put(Mode.FIN)

    @check_client
    def broadcast(self, messages: Dict[str, Data]):
        for client, msg in messages.items():
            self._send_queues[client].put(msg)

    @check_client
    def gather(
        self, clients: List[str], timeout: Optional[float] = None
    ) -> Dict[str, Data]:
        result = {}
        end = 0
        if timeout is not None:
            end = time.time() + timeout
        while (end == 0 or time.time() < end) and len(result) < len(clients):
            for client in clients:
                q: Queue = self._recv_queues[client]
                try:
                    data = q.get_nowait()
                    result[client] = data
                except Empty:
                    continue
        return result

    def start(self):
        commu_pb2_grpc.add_CommuServicer_to_server(self, self._server)
        self._server.start()

    def stop(self):
        self._server.stop(grace=True)

    @property
    def client(self) -> List[str]:
        return list(self._active_clients)
