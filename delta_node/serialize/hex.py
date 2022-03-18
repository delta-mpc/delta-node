from typing import Optional

__all__ = [
    "int_to_bytes",
    "bytes_to_int",
    "bytes_to_hex",
    "hex_to_bytes"
]


def bytes_to_hex(src: bytes, with0x: bool = True, max_length: Optional[int] = None) -> str:
    if max_length is not None:
        assert len(src) <= max_length, f"input bytes length is too long ({len(src)} > {max_length})"
    res = src.hex()
    if max_length is not None:
        res = res.zfill(max_length)
    if with0x:
        res = "0x" + res
    return res


def hex_to_bytes(src: str, length: Optional[int] = None) -> bytes:
    if src.startswith("0x"):
        src = src[2:]
    if length is not None:
        src = src.lstrip("0")
        assert len(src) <= length, f"input length is too long ({len(src)} > {length})"
        if len(src) < length:
            src = src.zfill(length)
    return bytes.fromhex(src)


def int_to_bytes(x: int) -> bytes:
    length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, "big")


def bytes_to_int(bs: bytes) -> int:
    return int.from_bytes(bs, "big")
