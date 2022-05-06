from __future__ import annotations

import os
from os import PathLike
from typing import IO, Any

import cloudpickle as pickle


def dump_obj(file: str | PathLike | IO[bytes], obj: Any):
    if isinstance(file, str):
        with open(file, mode="wb") as f:
            pickle.dump(obj, f)
    elif isinstance(file, PathLike):
        filename = os.fspath(file)
        with open(filename, mode="wb") as f:
            pickle.dump(obj, f)
    else:
        return pickle.dump(obj, file)


def load_obj(file: str | PathLike | IO[bytes]) -> Any:
    if isinstance(file, PathLike):
        filename = os.fspath(file)
        with open(filename, mode="rb") as f:
            res = pickle.load(f)
    elif isinstance(file, str):
        with open(file, mode="rb") as f:
            res = pickle.load(f)
    else:
        res = pickle.load(file)
    return res
