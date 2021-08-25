# coding: utf-8
import operator
import random
from functools import reduce
from typing import List, Tuple

from . import op

PRIME = 0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


def _eval_at(coeffs: List[int], x: int, prime: int) -> int:
    value = 0
    for coeff in coeffs[::-1]:
        value *= x
        value += coeff
        value %= prime
    return value


class SecretShare(object):
    def __init__(self, threshold: int, *, prime: int = PRIME):
        self.threshold = threshold
        self.prime = prime

        self.random = random.Random()

    def make_shares(self, value: int, shares: int) -> List[Tuple[int, int]]:
        if self.threshold > shares:
            raise ValueError("threshold should be little equal than shares")

        coeffs = [value] + [self.random.randint(1, self.prime - 1) for _ in range(self.threshold - 1)]
        res = [(x, _eval_at(coeffs, x, self.prime)) for x in range(1, shares + 1)]
        return res

    def resolve_shares(self, shares: List[Tuple[int, int]]) -> int:
        xs, ys = zip(*shares)
        k = len(xs)
        if k < self.threshold:
            raise ValueError("need at least {} shares".format(self.threshold))
        if k != len((set(xs))):
            raise ValueError("shares must be distinct")

        nums = []
        dens = []
        for i in range(k):
            nums.append(reduce(operator.mul, [-xs[j] for j in range(k) if i != j]))
            dens.append(reduce(operator.mul, [xs[i] - xs[j] for j in range(k) if i != j]))

        den: int = reduce(operator.mul, dens)
        num = sum(op.div_mod(nums[i] * den * ys[i] % self.prime, dens[i], self.prime) for i in range(k))
        return op.div_mod(num, den, self.prime)
