# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: delta-zk.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.const
import grpclib.client
if typing.TYPE_CHECKING:
    import grpclib.server

from . import delta_zk_pb2


class ZKPBase(abc.ABC):

    @abc.abstractmethod
    async def prove(self, stream: 'grpclib.server.Stream[delta_zk_pb2.Input, delta_zk_pb2.Proof]') -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            '/delta.ZKP/prove': grpclib.const.Handler(
                self.prove,
                grpclib.const.Cardinality.UNARY_STREAM,
                delta_zk_pb2.Input,
                delta_zk_pb2.Proof,
            ),
        }


class ZKPStub:

    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.prove = grpclib.client.UnaryStreamMethod(
            channel,
            '/delta.ZKP/prove',
            delta_zk_pb2.Input,
            delta_zk_pb2.Proof,
        )