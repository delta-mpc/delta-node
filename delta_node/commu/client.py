import logging
import threading
from queue import Queue
from typing import Iterator, Optional

import grpc

from . import commu_pb2, commu_pb2_grpc
from .common import Data, split_data


class CommuClient(object):
    def __init__(self, local_id: str, server_id: str, host: str, port: int) -> None:
        self._id = local_id
        self._server_id = server_id
        self._frame_id = 0

        self._channel = grpc.insecure_channel(f"{host}:{port}")

        self._send_queue = Queue()
        self._recv_queue = Queue()

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._call)

        self._logger = logging.getLogger(__name__)

        self._connected = False
        self._condition = threading.Condition(threading.Lock())

    def connect(self, timeout: Optional[float] = None):
        self._thread.start()
        # put syn msg
        self._send_queue.put(
            Data(src=self._id, dst=self._server_id, type="syn", content=b"")
        )
        with self._condition:
            self._condition.wait_for(lambda: self._connected, timeout)

    def close(self):
        with self._condition:
            if self._connected:
                self._stop_event.set()
                self._thread.join()

    def send(self, data: Data):
        self._send_queue.put(data, block=True)

    def recv(self, timeout: Optional[float] = None) -> Data:
        return self._recv_queue.get(timeout=timeout)

    def _send_iter(self) -> Iterator[commu_pb2.Message]:
        while not self._stop_event.is_set():
            data: Data = self._send_queue.get(block=True)
            frame_id = self._frame_id
            self._frame_id += 1
            for msg in split_data(frame_id, data):
                yield msg
            if data.type == "syn":
                with self._condition:
                    self._connected = True
                    self._condition.notify_all()

    def _call(self):
        stub = commu_pb2_grpc.CommuStub(self._channel)
        src = ""
        dst = ""
        type = ""
        name = ""
        buffer = []
        for msg in stub.call(self._send_iter()):
            # check msg
            if msg.type == "err":
                err = msg.content.decode("utf-8")
                self._logger.error(err)
                return

            if msg.dst != self._id:
                err = f"msg dst should be {self._id}, but got {msg.dst}"
                self._logger.error(err)
                return

            if msg.frame_id != self._frame_id:
                err = f"msg frame id should be {self._frame_id}, but got {msg.frame_id}"
                self._logger.error(err)
                return

            if len(type) == 0:
                type = msg.type
            elif type != msg.type:
                err = f"msg type should not be changed in continuous sequence"
                self._logger.error(err)
                return
            if len(name) == 0:
                name = msg.name
            elif name != msg.name:
                err = f"msg name should not be changed in continuous sequence"
                self._logger.error(err)
                return
            if len(src) == 0:
                src = msg.src
            elif src != msg.src:
                err = f"msg src should not be changed in continuous sequence"
                self._logger.error(err)
                return
            if len(dst) == 0:
                dst = msg.dst
            elif dst != msg.dst:
                err = f"msg dst should not be changed in continuous sequence"
                self._logger.error(err)
                return

            if len(buffer) == msg.sequence:
                buffer.append(msg.content)
            else:
                err = f"msg sequence should be {len(buffer)}, but got {msg.sequence}"
                self._logger.error(err)
                return

            if msg.eof:
                data = Data(
                    src=src, dst=dst, type=type, name=name, content=b"".join(buffer)
                )
                self._recv_queue.put(data)
                src = ""
                dst = ""
                type = ""
                name = ""
                buffer.clear()
                self._frame_id += 1
