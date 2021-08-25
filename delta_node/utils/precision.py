import numpy as np


def fix_precision(arr: np.ndarray, precision: int) -> np.ndarray:
    arr = np.around(arr, precision) * (10 ** precision)
    arr = arr.astype(np.int64)
    return arr


def unfix_precision(arr: np.ndarray, precision: int) -> np.ndarray:
    arr = arr.astype(np.float64)
    arr = arr / (10 ** precision)
    return arr
