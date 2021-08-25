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


def make_mask(seed: Union[int, bytes, str], shape: Sequence[int]) -> np.ndarray:
    state = random.Random(seed)
    size = reduce(mul, shape)

    mask = np.array(
        [state.randint(0, 2 ** 63 - 1) for _ in range(size)], dtype=np.int64
    )
    mask.resize(shape)

    return mask
