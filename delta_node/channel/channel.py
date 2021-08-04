import logging
import socket
from enum import IntEnum
from queue import Queue
from typing import Iterator, Optional, Tuple

from .msg import Message

_logger = logging.getLogger(__name__)


class Control(IntEnum):
    INPUT = 0
    OUTPUT = 1
    FINISH = 2


class OuterChannel(object):
    def __init__(
        self,
        sock: socket.socket,
        input_queue: Queue,
        output_queue: Queue,
        control_queue: Queue,
    ) -> None:
        self._sock = sock
        self._input_queue = input_queue  # type: Queue[Message]
        self._output_queue = output_queue  # type: Queue[Message]
        self._control_queue = control_queue  # type: Queue[Control]

    def fileno(self):
        return self._sock.fileno()

    def recv(self, timeout: Optional[float] = None) -> Message:
        return self._output_queue.get(timeout=timeout)

    def send(self, msg: Message):
        self._sock.send(b"x")
        self._input_queue.put(msg)

    def control_flow(self) -> Iterator[Control]:
        return iter(self._control_queue.get, Control.FINISH)


class InnerChannel(object):
    def __init__(
        self,
        sock: socket.socket,
        input_queue: Queue,
        output_queue: Queue,
        control_queue: Queue,
    ) -> None:
        self._sock = sock
        self._input_queue = input_queue  # type: Queue[Message]
        self._output_queue = output_queue  # type: Queue[Message]
        self._control_queue = control_queue  # type: Queue[Control]

    def fileno(self):
        return self._sock.fileno()

    def ready_to_read(self):
        self._control_queue.put(Control.INPUT)

    def _recv(self, timeout: Optional[float] = None) -> Message:
        res = self._input_queue.get(timeout=timeout)
        self._sock.recv(1)
        return res

    def recv(self, timeout: Optional[float] = None) -> Message:
        self.ready_to_read()
        return self._recv(timeout)

    def ready_to_write(self):
        self._control_queue.put(Control.OUTPUT)

    def _send(self, msg: Message):
        self._output_queue.put(msg)

    def send(self, msg: Message):
        self.ready_to_write()
        self._send(msg)

    def close(self):
        self._control_queue.put(Control.FINISH)
        self._sock.close()


def new_channel_pair() -> Tuple[InnerChannel, OuterChannel]:
    in_sock, out_sock = socket.socketpair()
    in_sock.setblocking(False)
    out_sock.setblocking(False)
    input_queue = Queue()
    output_queue = Queue()
    control_queue = Queue()
    return (
        InnerChannel(in_sock, input_queue, output_queue, control_queue),
        OuterChannel(out_sock, input_queue, output_queue, control_queue),
    )
