from delta_node.utils.mimc7 import calc_data_commitment, calc_weight_commitment, mimc7_hash
from delta_node.serialize import bytes_to_hex
import numpy as np

def test_mimc7():
    x = 1
    k = 0
    h = mimc7_hash(x, k)
    assert h.digits(10) == "17600997160967632941734844553571167148709325093482377638261037629495019706198"


def test_weight_commitment():
    weight = [0.30321158, -0.10144448, 1.61196386]
    cmmt = calc_weight_commitment(weight)
    assert bytes_to_hex(cmmt, length=32) == "0x09ea9ed6d70cd296187459b9256c3f290565ccedc317f96f539bc46df73cda92"


def test_data_commitment():
    x = np.array(
        [
            [2.66, 20.0, 0.0],
            [2.89, 22.0, 0.0],
            [3.28, 24.0, 0.0],
            [2.92, 12.0, 0.0],
            [4.0, 21.0, 0.0],
            [2.86, 17.0, 0.0],
            [2.76, 17.0, 0.0],
            [2.87, 21.0, 0.0],
            [3.03, 25.0, 0.0],
            [3.92, 29.0, 0.0],
            [2.63, 20.0, 0.0],
            [3.32, 23.0, 0.0],
            [3.57, 23.0, 0.0],
            [3.26, 25.0, 0.0],
            [3.53, 26.0, 0.0],
            [2.74, 19.0, 0.0],
            [2.75, 25.0, 0.0],
            [2.83, 19.0, 0.0],
            [3.12, 23.0, 1.0],
            [3.16, 25.0, 1.0],
            [2.06, 22.0, 1.0],
            [3.62, 28.0, 1.0],
            [2.89, 14.0, 1.0],
            [3.51, 26.0, 1.0],
            [3.54, 24.0, 1.0],
            [2.83, 27.0, 1.0],
            [3.39, 17.0, 1.0],
            [2.67, 24.0, 1.0],
            [3.65, 21.0, 1.0],
            [4.0, 23.0, 1.0],
            [3.1, 21.0, 1.0],
            [2.39, 19.0, 1.0],
        ],
        dtype=np.float64,
    )
    y = np.array(
        [
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            1,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            1,
            0,
            1,
        ],
        dtype=np.uint8,
    )
    data = np.hstack([x, y[:, None]])

    res = calc_data_commitment(data)
    
    assert len(res) == 1
    assert bytes_to_hex(res[0], length=32) == "0x0f6f31d790c79863387ddcbe761748b5dc72837e62035cc85e8eb136d727e8e4"