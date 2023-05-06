# type: ignore
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import datahub_pb2 as datahub__pb2
from ..transaction import transaction_pb2 as transaction__pb2


class DataHubStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/datahub.DataHub/Register',
                request_serializer=datahub__pb2.RegisterReq.SerializeToString,
                response_deserializer=transaction__pb2.Transaction.FromString,
                )
        self.GetDataCommitment = channel.unary_unary(
                '/datahub.DataHub/GetDataCommitment',
                request_serializer=datahub__pb2.DataCommitmentReq.SerializeToString,
                response_deserializer=datahub__pb2.DataCommitmentResp.FromString,
                )


class DataHubServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetDataCommitment(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DataHubServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=datahub__pb2.RegisterReq.FromString,
                    response_serializer=transaction__pb2.Transaction.SerializeToString,
            ),
            'GetDataCommitment': grpc.unary_unary_rpc_method_handler(
                    servicer.GetDataCommitment,
                    request_deserializer=datahub__pb2.DataCommitmentReq.FromString,
                    response_serializer=datahub__pb2.DataCommitmentResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'datahub.DataHub', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class DataHub(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/datahub.DataHub/Register',
            datahub__pb2.RegisterReq.SerializeToString,
            transaction__pb2.Transaction.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetDataCommitment(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/datahub.DataHub/GetDataCommitment',
            datahub__pb2.DataCommitmentReq.SerializeToString,
            datahub__pb2.DataCommitmentResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
