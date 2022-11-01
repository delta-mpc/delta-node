import numpy as np
from delta.core.task import AggValueType


def fix_precision(arr: AggValueType, precision: int) -> AggValueType:
    _arr = arr.astype(np.float64)
    _arr = _arr * (10**precision)
    _arr = _arr.astype(np.int64)
    return _arr


def unfix_precision(arr: AggValueType, precision: int) -> AggValueType:
    _arr = arr.astype(np.float64)
    _arr = _arr / (10**precision)
    return _arr
