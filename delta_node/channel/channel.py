from enum import IntEnum
from typing import Iterator, Optional, Tuple
from queue import Queue
import socket


class Control(IntEnum):
    INPUT = 0
    OUTPUT = 1
    FINISH = 2



class OuterChannel(object):
    def __init__(self, sock: socket.socket, input_queue: Queue, output_queue: Queue, control_queue: Queue) -> None:
        self._sock = sock
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._control_queue = control_queue
        
    def fileno(self):
        return self._sock.fileno()
    
    def recv(self, timeout: Optional[float] = None):
        self._output_queue.get(timeout=timeout)

    def send(self, msg):
        self._sock.send(b"x")
        self._input_queue.put(msg)
        
    def control_flow(self) -> Iterator[Control]:
        return iter(self._control_queue.get, Control.FINISH)
    
class InnerChannel(object):
    def __init__(self, sock: socket.socket, input_queue: Queue, output_queue: Queue, control_queue: Queue) -> None:
        self._sock = sock
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._control_queue = control_queue
        
    def fileno(self):
        return self._sock.fileno()
    
    def recv(self, timeout: Optional[float] = None):
        self._control_queue.put(Control.INPUT)
        self._sock.settimeout(timeout)
        self._sock.recv(1)
        self._input_queue.get(timeout=timeout)

    def send(self, msg):
        self._control_queue.put(Control.OUTPUT)
        self._output_queue.put(msg)

    def finish(self):
        self._control_queue.put(Control.FINISH)


def new_channel_pair() -> Tuple[InnerChannel, OuterChannel]:
    in_sock, out_sock = socket.socketpair()
    input_queue = Queue()
    output_queue = Queue()
    control_queue = Queue()
    return (
        InnerChannel(in_sock, input_queue, output_queue, control_queue),
        OuterChannel(out_sock, input_queue, output_queue, control_queue)
    )
    