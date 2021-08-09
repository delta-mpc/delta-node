import logging
from concurrent import futures
from queue import Queue
from typing import IO, Callable

import grpc

from .. import channel
from ..model import TaskMetadata
from . import commu_pb2, commu_pb2_grpc

_logger = logging.getLogger(__name__)


class CommuClient(object):
    def __init__(self, address: str) -> None:
        self._channel = grpc.insecure_channel(address)
        self._stub = commu_pb2_grpc.CommuStub(self._channel)

    def get_metadata(self, task_id: int, member_id: str) -> TaskMetadata:
        req = commu_pb2.TaskReq(task_id=task_id, member_id=member_id)
        resp = self._stub.GetMetadata(req)
        metadata = TaskMetadata(
            name=resp.name,
            type=resp.type,
            secure_level=resp.secure_level,
            algorithm=resp.algorithm,
            members=resp.members,
        )
        return metadata

    def join_task(self, task_id: int, member_id: str) -> bool:
        req = commu_pb2.TaskReq(task_id=task_id, member_id=member_id)
        try:
            resp = self._stub.JoinTask(req)
            success = resp.success
            return success
        except grpc.RpcError as e:
            _logger.error(e)
            return False

    def finish_task(self, task_id: int, member_id: str) -> bool:
        req = commu_pb2.TaskReq(task_id=task_id, member_id=member_id)
        try:
            resp = self._stub.FinishTask(req)
            success = resp.success
            return success
        except grpc.RpcError as e:
            _logger.error(e)
            return False

    def get_round_id(self, task_id: int, member_id: str) -> int:
        req = commu_pb2.TaskReq(task_id=task_id, member_id=member_id)
        resp = self._stub.GetRound(req)
        round_id = resp.round_id
        return round_id

    def get_file(
        self, task_id: int, member_id: str, round_id: int, file_type: str, dst: IO[bytes]
    ):
        req = commu_pb2.FileReq(
            task_id=task_id, member_id=member_id, round_id=round_id, type=file_type
        )
        for resp in self._stub.GetFile(req):
            content = resp.content
            if len(content) == 0:
                break
            dst.write(content)

    def upload_result(
        self,
        task_id: int,
        member_id: str,
        round_id: int,
        callback: Callable[[channel.InnerChannel], None],
    ):
        in_ch, out_ch = channel.new_channel_pair()

        q = Queue()
        init_msg = commu_pb2.ResultReq(
            task_id=task_id,
            member_id=member_id,
            round_id=round_id,
            type="init",
            content=b"",
        )
        q.put(init_msg)
        req_iter = iter(q.get, None)
        resp_iter = self._stub.UploadResult(req_iter)
        _logger.info(f"task {task_id} member {member_id} upload result")

        with futures.ThreadPoolExecutor(1) as pool:
            fut = pool.submit(callback, in_ch)

            for opt in out_ch.control_flow():
                if opt == channel.Control.INPUT:
                    resp = next(resp_iter)
                    msg = channel.Message(type=resp.type, content=resp.content)
                    out_ch.send(msg)
                elif opt == channel.Control.OUTPUT:
                    msg = out_ch.recv()
                    req = commu_pb2.ResultReq(
                        task_id=task_id,
                        member_id=member_id,
                        round_id=round_id,
                        type=msg.type,
                        content=msg.content,
                    )
                    q.put(req)
            q.put(None)
            fut.result()
        # wait for server finish
        for _ in resp_iter:
            pass
