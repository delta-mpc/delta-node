# type: ignore
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import commu_pb2 as commu__pb2


class CommuStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetMetadata = channel.unary_unary(
                '/commu.Commu/GetMetadata',
                request_serializer=commu__pb2.TaskReq.SerializeToString,
                response_deserializer=commu__pb2.MetadataResp.FromString,
                )
        self.JoinTask = channel.unary_unary(
                '/commu.Commu/JoinTask',
                request_serializer=commu__pb2.TaskReq.SerializeToString,
                response_deserializer=commu__pb2.StatusResp.FromString,
                )
        self.FinishTask = channel.unary_unary(
                '/commu.Commu/FinishTask',
                request_serializer=commu__pb2.TaskReq.SerializeToString,
                response_deserializer=commu__pb2.StatusResp.FromString,
                )
        self.GetRound = channel.unary_unary(
                '/commu.Commu/GetRound',
                request_serializer=commu__pb2.TaskReq.SerializeToString,
                response_deserializer=commu__pb2.RoundResp.FromString,
                )
        self.GetFile = channel.unary_stream(
                '/commu.Commu/GetFile',
                request_serializer=commu__pb2.FileReq.SerializeToString,
                response_deserializer=commu__pb2.FileResp.FromString,
                )
        self.UploadResult = channel.stream_stream(
                '/commu.Commu/UploadResult',
                request_serializer=commu__pb2.ResultReq.SerializeToString,
                response_deserializer=commu__pb2.ResultResp.FromString,
                )


class CommuServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetMetadata(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def JoinTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FinishTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetRound(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadResult(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CommuServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetMetadata': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMetadata,
                    request_deserializer=commu__pb2.TaskReq.FromString,
                    response_serializer=commu__pb2.MetadataResp.SerializeToString,
            ),
            'JoinTask': grpc.unary_unary_rpc_method_handler(
                    servicer.JoinTask,
                    request_deserializer=commu__pb2.TaskReq.FromString,
                    response_serializer=commu__pb2.StatusResp.SerializeToString,
            ),
            'FinishTask': grpc.unary_unary_rpc_method_handler(
                    servicer.FinishTask,
                    request_deserializer=commu__pb2.TaskReq.FromString,
                    response_serializer=commu__pb2.StatusResp.SerializeToString,
            ),
            'GetRound': grpc.unary_unary_rpc_method_handler(
                    servicer.GetRound,
                    request_deserializer=commu__pb2.TaskReq.FromString,
                    response_serializer=commu__pb2.RoundResp.SerializeToString,
            ),
            'GetFile': grpc.unary_stream_rpc_method_handler(
                    servicer.GetFile,
                    request_deserializer=commu__pb2.FileReq.FromString,
                    response_serializer=commu__pb2.FileResp.SerializeToString,
            ),
            'UploadResult': grpc.stream_stream_rpc_method_handler(
                    servicer.UploadResult,
                    request_deserializer=commu__pb2.ResultReq.FromString,
                    response_serializer=commu__pb2.ResultResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'commu.Commu', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Commu(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetMetadata(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/commu.Commu/GetMetadata',
            commu__pb2.TaskReq.SerializeToString,
            commu__pb2.MetadataResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def JoinTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/commu.Commu/JoinTask',
            commu__pb2.TaskReq.SerializeToString,
            commu__pb2.StatusResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def FinishTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/commu.Commu/FinishTask',
            commu__pb2.TaskReq.SerializeToString,
            commu__pb2.StatusResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetRound(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/commu.Commu/GetRound',
            commu__pb2.TaskReq.SerializeToString,
            commu__pb2.RoundResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/commu.Commu/GetFile',
            commu__pb2.FileReq.SerializeToString,
            commu__pb2.FileResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UploadResult(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/commu.Commu/UploadResult',
            commu__pb2.ResultReq.SerializeToString,
            commu__pb2.ResultResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
