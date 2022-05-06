from __future__ import annotations

import os

import pandas as pd
from delta_node import config

from .file import load_file


def load_dataframe(dataset: str) -> pd.DataFrame:
    filename = os.path.join(config.data_dir, dataset)
    if not os.path.isfile(filename):
        raise ValueError("DataFrame dataset should be a file")
    res = load_file(filename)
    if isinstance(res, pd.DataFrame):
        return res
    else:
        raise ValueError(f"{filename} is not a dataframe")
