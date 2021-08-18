# type: ignore
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import chain_pb2 as chain__pb2


class ChainStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetNodes = channel.unary_unary(
            "/chain.Chain/GetNodes",
            request_serializer=chain__pb2.NodesReq.SerializeToString,
            response_deserializer=chain__pb2.NodesResp.FromString,
        )
        self.RegisterNode = channel.unary_unary(
            "/chain.Chain/RegisterNode",
            request_serializer=chain__pb2.NodeReq.SerializeToString,
            response_deserializer=chain__pb2.NodeResp.FromString,
        )
        self.CreateTask = channel.unary_unary(
            "/chain.Chain/CreateTask",
            request_serializer=chain__pb2.TaskReq.SerializeToString,
            response_deserializer=chain__pb2.TaskResp.FromString,
        )
        self.JoinTask = channel.unary_unary(
            "/chain.Chain/JoinTask",
            request_serializer=chain__pb2.JoinReq.SerializeToString,
            response_deserializer=chain__pb2.JoinResp.FromString,
        )
        self.StartRound = channel.unary_unary(
            "/chain.Chain/StartRound",
            request_serializer=chain__pb2.RoundReq.SerializeToString,
            response_deserializer=chain__pb2.RoundResp.FromString,
        )
        self.PublishPubKey = channel.unary_unary(
            "/chain.Chain/PublishPubKey",
            request_serializer=chain__pb2.KeyReq.SerializeToString,
            response_deserializer=chain__pb2.KeyResp.FromString,
        )
        self.Events = channel.unary_stream(
            "/chain.Chain/Events",
            request_serializer=chain__pb2.EventReq.SerializeToString,
            response_deserializer=chain__pb2.EventResp.FromString,
        )


class ChainServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetNodes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def RegisterNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def CreateTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def JoinTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def StartRound(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def PublishPubKey(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Events(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ChainServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetNodes": grpc.unary_unary_rpc_method_handler(
            servicer.GetNodes,
            request_deserializer=chain__pb2.NodesReq.FromString,
            response_serializer=chain__pb2.NodesResp.SerializeToString,
        ),
        "RegisterNode": grpc.unary_unary_rpc_method_handler(
            servicer.RegisterNode,
            request_deserializer=chain__pb2.NodeReq.FromString,
            response_serializer=chain__pb2.NodeResp.SerializeToString,
        ),
        "CreateTask": grpc.unary_unary_rpc_method_handler(
            servicer.CreateTask,
            request_deserializer=chain__pb2.TaskReq.FromString,
            response_serializer=chain__pb2.TaskResp.SerializeToString,
        ),
        "JoinTask": grpc.unary_unary_rpc_method_handler(
            servicer.JoinTask,
            request_deserializer=chain__pb2.JoinReq.FromString,
            response_serializer=chain__pb2.JoinResp.SerializeToString,
        ),
        "StartRound": grpc.unary_unary_rpc_method_handler(
            servicer.StartRound,
            request_deserializer=chain__pb2.RoundReq.FromString,
            response_serializer=chain__pb2.RoundResp.SerializeToString,
        ),
        "PublishPubKey": grpc.unary_unary_rpc_method_handler(
            servicer.PublishPubKey,
            request_deserializer=chain__pb2.KeyReq.FromString,
            response_serializer=chain__pb2.KeyResp.SerializeToString,
        ),
        "Events": grpc.unary_stream_rpc_method_handler(
            servicer.Events,
            request_deserializer=chain__pb2.EventReq.FromString,
            response_serializer=chain__pb2.EventResp.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "chain.Chain", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class Chain(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetNodes(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chain.Chain/GetNodes",
            chain__pb2.NodesReq.SerializeToString,
            chain__pb2.NodesResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def RegisterNode(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chain.Chain/RegisterNode",
            chain__pb2.NodeReq.SerializeToString,
            chain__pb2.NodeResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def CreateTask(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chain.Chain/CreateTask",
            chain__pb2.TaskReq.SerializeToString,
            chain__pb2.TaskResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def JoinTask(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chain.Chain/JoinTask",
            chain__pb2.JoinReq.SerializeToString,
            chain__pb2.JoinResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def StartRound(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chain.Chain/StartRound",
            chain__pb2.RoundReq.SerializeToString,
            chain__pb2.RoundResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def PublishPubKey(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chain.Chain/PublishPubKey",
            chain__pb2.KeyReq.SerializeToString,
            chain__pb2.KeyResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Events(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/chain.Chain/Events",
            chain__pb2.EventReq.SerializeToString,
            chain__pb2.EventResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
