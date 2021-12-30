# coding: utf-8
import operator
import random
from functools import reduce
from typing import List, Tuple

from delta_node import serialize

from . import op


__all__ = ["Share", "PRIME", "SecretShare"]

Share = Tuple[int, int]

PRIME = 0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


def _eval_at(coeffs: List[int], x: int, prime: int) -> int:
    value = 0
    for coeff in coeffs[::-1]:
        value *= x
        value += coeff
        value %= prime
    return value


def _share_to_bytes(share: Share) -> bytes:
    x, y = share
    x_bytes = serialize.int_to_bytes(x)
    y_bytes = serialize.int_to_bytes(y)
    x_len_bytes = len(x_bytes).to_bytes(1, "big")
    return x_len_bytes + x_bytes + y_bytes


def _bytes_to_share(data: bytes) -> Share:
    x_len_bytes = data[:1]
    x_length = int.from_bytes(x_len_bytes, "big")

    x_bytes = data[1 : 1 + x_length]
    y_bytes = data[1 + x_length :]

    x = serialize.bytes_to_int(x_bytes)
    y = serialize.bytes_to_int(y_bytes)
    return x, y


class SecretShare(object):
    def __init__(self, threshold: int, *, prime: int = PRIME):
        self.threshold = threshold
        self.prime = prime

        self.random = random.Random()

    def make_shares(self, value: bytes, shares: int) -> List[bytes]:
        if self.threshold > shares:
            raise ValueError("threshold should be little equal than shares")

        coeffs = [serialize.bytes_to_int(value)] + [
            self.random.randint(1, self.prime - 1) for _ in range(self.threshold - 1)
        ]
        res = [
            _share_to_bytes((x, _eval_at(coeffs, x, self.prime)))
            for x in range(1, shares + 1)
        ]
        return res

    def resolve_shares(self, shares: List[bytes]) -> bytes:
        share_tups = [_bytes_to_share(share) for share in shares]
        xs, ys = zip(*share_tups)
        k = len(xs)
        if k < self.threshold:
            raise ValueError("need at least {} shares".format(self.threshold))
        if k != len((set(xs))):
            raise ValueError("shares must be distinct")

        nums = []
        dens = []
        for i in range(k):
            nums.append(reduce(operator.mul, [-xs[j] for j in range(k) if i != j]))
            dens.append(
                reduce(operator.mul, [xs[i] - xs[j] for j in range(k) if i != j])
            )

        den: int = reduce(operator.mul, dens)
        num = sum(
            op.div_mod(nums[i] * den * ys[i] % self.prime, dens[i], self.prime)
            for i in range(k)
        )
        return serialize.int_to_bytes(op.div_mod(num, den, self.prime))
