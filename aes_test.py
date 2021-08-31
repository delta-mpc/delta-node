from delta_node.crypto import aes, ecdhe


if __name__ == "__main__":
    curve = ecdhe.CURVES["secp256r1"]
    sk1, pk1 = ecdhe.generate_key_pair(curve)
    sk2, pk2 = ecdhe.generate_key_pair(curve)

    ck1 = ecdhe.generate_shared_key(sk1, pk2, curve)
    ck2 = ecdhe.generate_shared_key(sk2, pk1, curve)
    assert ck1 == ck2

    msg = b"hello world"
    ct = aes.encrypt(ck1, msg)
    pt = aes.decrypt(ck2, ct)
    print(pt)
    assert msg == pt
