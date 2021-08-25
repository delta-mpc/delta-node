import os
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes



def encrypt(key: bytes, data: bytes) -> bytes:
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    encryptor = cipher.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    ct = nonce + ct
    return b64encode(ct)


def decrypt(key: bytes, data: bytes) -> bytes:
    raw = b64decode(data)
    nonce, ct = raw[:16], raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    decryptor = cipher.decryptor()
    plain_text = decryptor.update(ct) + decryptor.finalize()
    return plain_text
