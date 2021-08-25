from typing import Tuple


def extend_gcd(a: int, b: int) -> Tuple[int, int, int]:
    last_r, r = a, b
    last_x, x = 1, 0
    last_y, y = 0, 1
    while r != 0:
        quot = last_r // r
        last_r, r = r, last_r - quot * r
        last_x, x = x, last_x - quot * x
        last_y, y = y, last_y - quot * y
    return last_r, last_x, last_y


def inverse_mod(k: int, p: int) -> int:
    if k == 0:
        raise ZeroDivisionError

    gcd, x, y = extend_gcd(k, p)

    assert gcd == 1
    assert k * x % p == 1

    return x % p


def div_mod(a: int, b: int, p: int) -> int:
    return a * inverse_mod(b, p) % p
