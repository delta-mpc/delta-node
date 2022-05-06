from __future__ import annotations

from os import PathLike
from typing import IO, Dict

from delta.core.task import AggResultType

from .obj import dump_obj, load_obj


def dump_agg_result(file: str | PathLike | IO[bytes], result: Dict[str, AggResultType]):
    dump_obj(file, result)


def load_agg_result(file: str | PathLike | IO[bytes]) -> Dict[str, AggResultType]:
    res = load_obj(file)
    assert isinstance(res, dict)
    return res
