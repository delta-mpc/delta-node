from delta_node.crypto import shamir
import random


def random_bytes(length: int) -> bytes:
    return bytes(random.getrandbits(8) for _ in range(length))


def test_shamir():
    value = random_bytes(32)

    ss = shamir.SecretShare(3)

    shares = ss.make_shares(value, 5)
    assert len(shares) == 5

    assert ss.resolve_shares(shares) == value
    assert ss.resolve_shares(random.sample(shares, 4)) == value
    assert ss.resolve_shares(random.sample(shares, 3)) == value
