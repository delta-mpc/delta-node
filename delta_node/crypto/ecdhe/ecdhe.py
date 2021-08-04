from typing import Tuple
import time

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from ... import serialize


__all__ = ["generate_key_pair", "generate_shared_key"]

def generate_key_pair(curve: ec.EllipticCurve) -> Tuple[bytes, bytes]:
    priv_key = ec.generate_private_key(curve)
    pub_key = priv_key.public_key()

    sk = priv_key.private_numbers().private_value
    sk_bytes = serialize.int_to_bytes(sk)
    pk_bytes = pub_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint)
    return sk_bytes, pk_bytes


def generate_shared_key(sk_bytes: bytes, pk_bytes: bytes, curve: ec.EllipticCurve) -> bytes:
    pub_key = ec.EllipticCurvePublicKey.from_encoded_point(curve, pk_bytes)
    sk = serialize.bytes_to_int(sk_bytes)
    priv_key = ec.derive_private_key(sk, curve)

    shared_key = priv_key.exchange(ec.ECDH(), pub_key)

    digest = hashes.Hash(hashes.SHA256())
    digest.update(shared_key)
    return digest.finalize()
