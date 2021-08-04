import logging
from concurrent import futures
from typing import Generator, Optional

import grpc

from .. import config, task
from ..channel import Control, Message
from . import commu_pb2, commu_pb2_grpc


_logger = logging.getLogger(__name__)

def file_resp_generator(filename: str) -> Generator[commu_pb2.FileResp, None, None]:
    with open(filename, mode="rb") as f:
        while True:
            content = f.read(config.MAX_BUFF_SIZE)
            if len(content) == 0:
                yield commu_pb2.FileResp(filename=filename, content=b"")
                break
            resp = commu_pb2.FileResp(filename=filename, content=content)
            yield resp


class Servicer(commu_pb2_grpc.CommuServicer):
    def GetMetadata(self, request, context):
        task_id = request.task_id
        member_id = request.member_id
        try:
            manager = task.get_task_manager(task_id=task_id)
            metadata = manager.get_metadata(member_id)
            resp = commu_pb2.MetadataResp(
                name=metadata.name,
                type=metadata.type,
                secure_level=metadata.secure_level,
                algorithm=metadata.algorithm,
                members=metadata.members,
            )
            return resp
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def JoinTask(self, request, context):
        task_id = request.task_id
        member_id = request.member_id
        try:
            manager = task.get_task_manager(task_id=task_id)
            manager.join(member_id)
            resp = commu_pb2.JoinResp(success=True)
            return resp
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def GetRound(self, request, context):
        task_id = request.task_id
        member_id = request.member_id
        try:
            manager = task.get_task_manager(task_id=task_id)
            round_id = manager.get_round_id(member_id=member_id)
            resp = commu_pb2.RoundResp(round_id=round_id)
            return resp
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def GetFile(self, request, context):
        task_id = request.task_id
        member_id = request.member_id
        file_type = request.type
        round_id = request.round_id

        try:
            manager = task.get_task_manager(task_id)
            filename = manager.get_file(member_id, round_id, file_type)
            yield from file_resp_generator(filename)
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))


    def UploadResult(self, request_iterator, context):
        init_msg = next(request_iterator)
        task_id = init_msg.task_id
        member_id = init_msg.member_id
        assert init_msg.type == "init"
        _logger.info(f"task {task_id} member {member_id} upload result")

        try:
            manager = task.get_task_manager(task_id)
            if manager.has_joined_member(member_id):
                with manager.aggregate(member_id) as ch:
                    for opt in ch.control_flow():
                        if opt == Control.INPUT:
                            req = next(request_iterator)
                            msg = Message(req.type, req.content)
                            ch.send(msg)
                        elif opt == Control.OUTPUT:
                            msg = ch.recv()
                            yield commu_pb2.ResultResp(
                                type=msg.type, content=msg.content
                            )
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))


class CommuServer(object):
    def __init__(self, address: str) -> None:
        self._server = grpc.server(futures.ThreadPoolExecutor())
        self._server.add_insecure_port(address)
        commu_pb2_grpc.add_CommuServicer_to_server(Servicer(), self._server)

    def start(self):
        self._server.start()

    def wait_for_termination(self, timeout: Optional[float] = None):
        self._server.wait_for_termination(timeout=timeout)

    def stop(self):
        self._server.stop(True)
