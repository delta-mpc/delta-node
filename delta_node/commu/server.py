from typing import Generator

import grpc
from sqlalchemy.orm import session
from . import commu_pb2, commu_pb2_grpc
from .. import task, config


def file_resp_generator(filename: str) -> Generator[commu_pb2.FileResp, None, None]:
    with open(filename, mode="rb") as f:
        while True:
            content = f.read(config.MAX_BUFF_SIZE)
            if len(content) == 0:
                break
            resp = commu_pb2.FileResp(filename=filename, content=content)
            yield resp



class Servicer(commu_pb2_grpc.CommuServicer):
    def GetMetadata(self, request, context):
        task_id = request.task_id
        member_id = request.member_id
        try:
            manager = task.get_task_manager(task_id=task_id)
            manager.join(member_id)
            metadata = manager.task_metadata
            resp = commu_pb2.MetadataResp(
                name=metadata.name,
                type=metadata.type,
                secure_level=metadata.secure_level,
                algorithm=metadata.algorithm,
                members=metadata.members
            )
            return resp
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    def GetFile(self, request, context):
        task_id = request.task_id
        member_id = request.member_id
        file_type = request.type

        try:
            manager = task.get_task_manager(task_id)
            if manager.has_joined_member(member_id):
                if file_type == "cfg":
                    filename = task.task_cfg_file(task_id)
                    yield from file_resp_generator(filename)
                elif file_type == "weight":
                    round_id = manager.start_new_round(member_id)
                    filename = task.task_weight_file(task_id, round_id)
                    yield from file_resp_generator(filename)
            else:
                raise task.MemberNotJoinedError(task_id, member_id)
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    def UploadResult(self, request_iterator, context):
        init_msg = next(request_iterator)
        task_id = init_msg.task_id
        member_id = init_msg.member_id
        assert init_msg.type == "init"

        try:
            manager = task.TaskManager(task_id)
            if manager.has_joined_member(member_id):
                pk_msg = next(request_iterator)
                assert pk_msg.type == "pk"
                pk = pk_msg.content
        except task.TaskError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))