from __future__ import annotations

import math
from functools import partial
from typing import Iterable, List, Union

import gmpy2
from delta_node.serialize import int_to_bytes
from gmpy2 import mpz  # type: ignore

from . import constant

__all__ = ["calc_weight_commitment", "calc_data_commitment"]

BigInt = Union[int, str, mpz]


def mimc7_hash(x: BigInt, key: BigInt) -> mpz:
    r = mpz(x)
    k = mpz(key)
    cts = constant.cts()
    q = mpz(constant.q())
    for i in range(len(cts)):
        t = (r + k + mpz(cts[i])) % q
        r = gmpy2.powmod(t, 7, q)  # type: ignore
    res = r + k
    return res


def mimc7_hash_arr(xs: List[BigInt], key: BigInt) -> mpz:
    r = mpz(key)
    arr = [mpz(x) for x in xs]
    q = mpz(constant.q())
    for x in arr:
        r = (r + x + mimc7_hash(x, r)) % q
    return r


def _float2mpz(x: float, precision: int = 8) -> mpz:
    q = mpz(constant.q())

    a = mpz(int(x * (10**precision)))
    b = q - a
    return min(a, b)


def merkle_mimc7_hash_arr(xs: List[BigInt], key: BigInt, min_size: int = 2) -> mpz:
    length = len(xs)
    assert length % 2 == 0, "merkle mimc7 hash input array length should be even"
    if length == min_size:
        return mimc7_hash_arr(xs, key)
    else:
        left = merkle_mimc7_hash_arr(xs[: length // 2], key, min_size)
        right = merkle_mimc7_hash_arr(xs[length // 2 :], key, min_size)
        return mimc7_hash_arr([left, right], key)


def calc_weight_commitment(weight: Iterable[float]) -> bytes:
    w = list(map(partial(_float2mpz, precision=8), weight))
    return int_to_bytes(int(mimc7_hash_arr(w, 2)))


def calc_data_commitment(data: Iterable[Iterable[float]]) -> List[bytes]:
    # convert to mpz
    precision1 = 8
    precision2 = 21

    p_data = []
    for row in data:
        row = list(row)
        x = row[:-1]
        y = row[-1]
        p_row = [_float2mpz(v, precision1) for v in x] + [_float2mpz(y, precision2)]
        p_data.append(p_row)

    # pad p_data
    rows = len(p_data)
    cols = len(p_data[0])
    block_size = constant.data_block_size()
    pad_length = math.ceil(rows / block_size) * block_size - rows
    pad_data = [[mpz()] * cols] * pad_length
    p_data += pad_data

    # mimc7 each row of p_data
    hash_data = [mimc7_hash_arr(row, 2) for row in p_data]

    # calc merkle mimc7 hash
    res = []
    for start in range(0, len(hash_data), block_size):
        h = merkle_mimc7_hash_arr(hash_data[start : start + block_size], 2)
        res.append(int_to_bytes(int(h)))
    return res
