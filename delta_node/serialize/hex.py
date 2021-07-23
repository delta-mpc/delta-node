__all__ = [
    "int_to_hex_str",
    "hex_str_to_bytes",
    "hex_str_to_int",
    "int_to_bytes",
    "bytes_to_int",
]


def int_to_hex_str(x: int) -> str:
    bs = int_to_bytes(x)
    return bs.hex()


def hex_str_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)


def hex_str_to_int(hex_str: str) -> int:
    return int(hex_str, 16)


def int_to_bytes(x: int) -> bytes:
    length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, "big")


def bytes_to_int(bs: bytes) -> int:
    return int.from_bytes(bs, "big")
