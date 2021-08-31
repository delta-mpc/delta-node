from delta_node.crypto import shamir
import random

if __name__ == "__main__":
    seed = random.randint(1, shamir.PRIME - 1)
    ss = shamir.SecretShare(2)
    shares = ss.make_shares(seed, 2)
    res = ss.resolve_shares(shares)
    assert seed == res
