import logging
from collections import defaultdict
from enum import IntEnum
from queue import Queue
from typing import Dict
from dataclasses import dataclass
import grpc
from concurrent import futures
import commu_pb2
import commu_pb2_grpc


class Mode(IntEnum):
    SEND = 0
    RECV = 1


def err_msg(src: str, dst: str, frame_id: int, err: str):
    return commu_pb2.Message(
        src=src,
        dst=dst,
        frame_id=frame_id,
        sequence=0,
        type="err",
        content=err.encode("utf-8"),
        eof=True,
    )


def fin_msg(src: str, dst: str, frame_id: int):
    return commu_pb2.Message(
        src=src,
        dst=dst,
        frame_id=frame_id,
        sequence=0,
        type="fin",
        content=b"",
        eof=True,
    )


@dataclass
class Data:
    type: str
    name: str
    content: bytes


def split_msg(src: str, dst: str, frame_id: int, data: Data, size: int):
    length = len(data.content)
    results = []
    for i, start in enumerate(range(0, length, size)):
        end = min(length, start + size)
        msg = commu_pb2.Message(
            src=src,
            dst=dst,
            frame_id=frame_id,
            sequence=i,
            type=data.type,
            name=data.name,
            content=data.content[start:end],
            eof=False,
        )
        results.append(msg)
    results[-1].eof = True
    return results


class CommuServer(commu_pb2_grpc.CommuServicer):
    def __init__(self, id: str) -> None:
        super().__init__()
        self._id = id
        self._send_queues: Dict[str, Queue] = defaultdict(Queue)
        self._recv_queues: Dict[str, Queue] = defaultdict(Queue)
        self._client_actions: Dict[str, Queue] = defaultdict(Queue)
        self._max_buff_size = 128 * 1024
        self._logger = logging.getLogger(__name__)

    def call(self, request_iterator, context):
        remote_id = ""
        frame_id = 0

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
                continue

            mode = self._client_actions[remote_id].get(block=True)
            if mode == Mode.RECV:
                eof = False
                buffer = []
                type = ""
                name = ""
                while not eof:
                    msg = next(request_iterator)
                    if msg.type == "err":
                        err = msg.content.decode("utf-8")
                        self._logger.error(err)
                        return

                    if msg.frame_id != frame_id:
                        err = (
                            f"msg frame id should be {frame_id}, but got {msg.frame_id}"
                        )
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id, err)
                        return

                    if msg.type == "fin":
                        msg = fin_msg(self._id, remote_id, frame_id + 1)
                        self._logger.info("remote close")
                        yield msg
                        return

                    if len(type) == 0:
                        type = msg.type
                    elif type != msg.type:
                        err = f"msg type should not be changed in continuous sequence"
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id + 1, err)
                        return
                    if len(name) == 0:
                        name = msg.name
                    elif name != msg.name:
                        err = f"msg name should not be changed in continuous sequence"
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id + 1, err)
                        return

                    if len(buffer) == msg.sequence:
                        buffer.append(msg.content)
                    else:
                        err = f"msg sequence should be continuous"
                        self._logger.error(err)
                        yield err_msg(self._id, remote_id, frame_id + 1, err)
                        return
                    eof = msg.eof

                data = Data(type=type, name=name, content=b"".join(buffer))
                self._recv_queues[remote_id].put(data, block=True)
                frame_id += 1

            elif mode == Mode.SEND:
                data = self._send_queues[remote_id].get()
                if data.type == "fin":
                    msg = fin_msg(self._id, remote_id, frame_id)
                    self._logger.info("self close")
                    yield msg
                    return
                if len(data.content) > self._max_buff_size:
                    msgs = split_msg(
                        self._id, remote_id, frame_id, data, self._max_buff_size
                    )
                    for msg in msgs:
                        yield msg

                else:
                    msg = commu_pb2.Message(
                        src=self._id,
                        dst=remote_id,
                        frame_id=frame_id,
                        sequence=0,
                        type=data.type,
                        name=data.name,
                        content=data.content,
                        eof=True,
                    )
                    yield msg
                frame_id += 1

    def send(self, client: str, data: Data):
        self._client_actions[client].put(Mode.SEND)
        self._send_queues[client].put(data)

    def recv(self, client: str) -> Data:
        self._client_actions[client].put(Mode.RECV)
        return self._recv_queues[client].get()

    def close(self, client: str):
        fin_data = Data(type="fin", name="", content=b"")
        self.send(client, fin_data)


def main():
    server = grpc.server(futures.ThreadPoolExecutor(4))
    commu_server = CommuServer("1")
    commu_pb2_grpc.add_CommuServicer_to_server(commu_server, server)
    server.add_insecure_port("[::]:38080")
    server.start()

    data = commu_server.recv("2")
    print(data)
    resp = Data(
        type=data.type,
        name=data.name,
        content=f"hello 2, recv your content {data.content.decode('utf-8')}".encode(
            "utf-8"
        ),
    )
    commu_server.send("2", resp)
    data = commu_server.recv("2")
    print(data)
    commu_server.close("2")


if __name__ == "__main__":
    logging.basicConfig()
    main()
