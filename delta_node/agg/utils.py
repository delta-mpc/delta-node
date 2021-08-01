import numpy as np
from typing import IO, List

from numpy.lib.arraysetops import isin

def load_arr(file: IO[bytes]) -> np.ndarray:
    arr = np.load(file)
    if isinstance(arr, np.ndarray):
        return arr
    elif isinstance(arr, dict):
        return arr["arr_0"]
    else:
        raise ValueError("unsupport file")


def add_arrs(arrs: List[np.ndarray]) -> np.ndarray:
    return np.sum(arrs, axis=0)  # type: ignore
