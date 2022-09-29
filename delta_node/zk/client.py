from logging import getLogger
from typing import Iterable, List

from delta_node.entity.hlr import Proof
from grpclib.client import Channel

from . import delta_zk_pb2 as pb
from .delta_zk_grpc import ZKPStub

_logger = getLogger(__name__)


class Client(object):
    def __init__(self, ch: Channel) -> None:
        self.stub = ZKPStub(ch)

    async def prove(
        self, weight: Iterable[float], samples: Iterable[Iterable[float]]
    ) -> List[Proof]:
        xy: List[pb.Sample] = []
        for row in samples:
            xy.append(pb.Sample(d=row))
        req = pb.Input(weights=weight, xy=xy)

        res = []
        async with self.stub.prove.open() as stream:
            await stream.send_message(req, end=True)
            async for proof in stream:
                res.append(
                    Proof(
                        index=proof.index,
                        proof=proof.proof,
                        pub_signals=list(proof.publicSignals),
                    )
                )
        return res
