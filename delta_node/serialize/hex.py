from typing import Optional

__all__ = [
    "int_to_bytes",
    "bytes_to_int",
    "bytes_to_hex",
    "hex_to_bytes"
]


def bytes_to_hex(src: bytes, with0x: bool = True, length: Optional[int] = None) -> str:
    """
    convert bytes to hex string
    
    src: source bytes
    with0x: whether to output hex string starts with '0x'
    length: output hex string byte length (len(output) / 2)
    """
    if length is not None:
        assert len(src) <= length, f"input bytes length is too long ({len(src)} > {length})"
    res = src.hex()
    if length is not None:
        res = res.zfill(length * 2)
    if with0x:
        res = "0x" + res
    return res


def hex_to_bytes(src: str, length: Optional[int] = None) -> bytes:
    """
    convert hex string to bytes

    src: source hex string
    length: output bytes length
    """
    if src.startswith("0x"):
        src = src[2:]
    if length is not None:
        assert len(src) <= length * 2, f"input hex string length is too long ({len(src)} > {length * 2})"
        src = src.zfill(length * 2)
    return bytes.fromhex(src)


def int_to_bytes(x: int) -> bytes:
    length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, "big")


def bytes_to_int(bs: bytes) -> int:
    return int.from_bytes(bs, "big")
