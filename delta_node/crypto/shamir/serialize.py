from delta_node import serialize

from .shamir import Share

__all__ = ["share_to_bytes", "bytes_to_share"]

def share_to_bytes(share: Share) -> bytes:
    x, y = share
    x_bytes = serialize.int_to_bytes(x)
    y_bytes = serialize.int_to_bytes(y)
    x_len_bytes = len(x_bytes).to_bytes(1, "big")
    return x_len_bytes + x_bytes + y_bytes


def bytes_to_share(data: bytes) -> Share:
    x_len_bytes = data[:1]
    x_length = int.from_bytes(x_len_bytes, "big")
    
    x_bytes = data[1: 1 + x_length]
    y_bytes = data[1 + x_length:]

    x = serialize.bytes_to_int(x_bytes)
    y = serialize.bytes_to_int(y_bytes)
    return x, y

