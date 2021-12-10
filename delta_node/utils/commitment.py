from hashlib import sha256
from typing import IO, Union


def calc_commitment(content: Union[bytes, IO[bytes]]) -> bytes:
    hash_obj = sha256()
    if isinstance(content, bytes):
        hash_obj.update(content)
    else:
        for data in content:
            hash_obj.update(data)
    return hash_obj.digest()
