import numpy as np
from typing import IO, List

def load_arr(file: IO[bytes]) -> np.ndarray:
    arr = np.load(file)
    if isinstance(arr, np.ndarray):
        return arr
    else:
        return arr["arr_0"]


def add_arrs(arrs: List[np.ndarray]) -> np.ndarray:
    return np.sum(arrs, axis=0)  # type: ignore

