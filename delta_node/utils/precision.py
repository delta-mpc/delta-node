import numpy as np
from delta.core.task import AggValueType


def fix_precision(arr: AggValueType, precision: int) -> AggValueType:
    arr = arr.astype(np.float64)
    arr = arr * (10**precision)
    arr = arr.astype(np.int64)
    return arr


def unfix_precision(arr: AggValueType, precision: int) -> AggValueType:
    arr = arr.astype(np.float64)
    arr = arr / (10**precision)
    return arr
