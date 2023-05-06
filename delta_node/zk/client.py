from typing import Iterable, List

from grpc.aio import Channel

from delta_node.entity.hlr import Proof

from . import delta_zk_pb2 as pb
from .delta_zk_pb2_grpc import ZKPStub


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
        stream = self.stub.prove(req)
        async for proof in stream:
            res.append(
                Proof(
                    index=proof.index,
                    proof=proof.proof,
                    pub_signals=list(proof.publicSignals),
                )
            )
        return res
