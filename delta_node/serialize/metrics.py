import json

import os
from os import PathLike
from typing import IO, Dict, Union


def dump_metrics(file: Union[str, PathLike, IO[str]], metrics: Dict[str, float]):
    if isinstance(file, str):
        with open(file, mode="w") as f:
            json.dump(metrics, f)
    elif isinstance(file, PathLike):
        filename = os.fspath(file)
        with open(filename, mode="w") as f:
            json.dump(metrics, f)
    else:
        json.dump(metrics, file)


def load_metrics(file: Union[str, PathLike, IO[str]]) -> Dict[str, float]:
    if isinstance(file, str):
        with open(file, mode="r") as f:
            return json.load(f)
    elif isinstance(file, PathLike):
        filename = os.fspath(file)
        with open(filename, mode="r") as f:
            return json.load(f)
    else:
        return json.load(file)
