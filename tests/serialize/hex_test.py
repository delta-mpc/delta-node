from delta_node import serialize

def test_hex_to_str():
    src = bytes([255])
    assert serialize.bytes_to_hex(src) == "0xff"
    assert serialize.bytes_to_hex(src, with0x=False) == "ff"
    assert serialize.bytes_to_hex(src, length=2) == "0x00ff"