import random
from functools import reduce
from operator import mul
from typing import IO, Sequence, Union

import numpy as np


def load_arr(file: IO[bytes]) -> np.ndarray:
    arr = np.load(file)
    if isinstance(arr, np.ndarray):
        return arr
    return arr["arr_0"]


def dump_arr(f: IO[bytes], arr: np.ndarray):
    np.savez_compressed(f, arr)


def make_mask(seed: Union[int, bytes], shape: Sequence[int]) -> np.ndarray:
    if isinstance(seed, int):
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng(list(seed))

    mask = rng.integers(0, 2 ** 47 - 1, size=shape, dtype=np.int64)

    return mask
