from base64 import b64encode, b64decode


def key_to_str(key: bytes) -> str:
    return b64encode(key).decode("utf-8")


def str_to_key(key_str: str) -> bytes:
    return b64decode(key_str.encode("utf-8"))
