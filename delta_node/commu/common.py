from dataclasses import dataclass
from enum import IntEnum
from typing import List

from . import commu_pb2

MAX_BUFF_SIZE = 128 * 1024


class Mode(IntEnum):
    SEND = 0
    RECV = 1
    FIN = 2


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


@dataclass
class Data:
    src: str
    dst: str
    type: str
    content: bytes
    name: str = ""


def split_data(
    frame_id: int, data: Data, size: int = MAX_BUFF_SIZE
) -> List[commu_pb2.Message]:
    length = len(data.content)
    results = []
    if length == 0:
        msg = commu_pb2.Message(
            src=data.src,
            dst=data.dst,
            frame_id=frame_id,
            sequence=0,
            type=data.type,
            name=data.name,
            content=data.content,
            eof=True,
        )
        results.append(msg)
    else:
        for i, start in enumerate(range(0, length, size)):
            end = min(length, start + size)
            msg = commu_pb2.Message(
                src=data.src,
                dst=data.dst,
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
