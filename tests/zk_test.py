import numpy as np
import pytest

from delta_node import zk

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def zk_client():
    async with zk.get_client(host="127.0.0.1", port=3400) as client:
        yield client


async def test_zk(zk_client: zk.Client):
    weight = np.array([0.30321158, -0.10144448, 1.61196386], dtype=np.float64)
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

    proofs = await zk_client.prove(weight.tolist(), data.tolist())
    pub_signals = [
        "21888242871839275222246405745257275088548364400416034299972841686575808495617",
        "29",
        "21888242871839275222246405745257275088548364400416034017709454186575808495617",
        "29",
        "21888242871839275222246405745257275088548364400416034336161954186575808495617",
        "29",
        "4485354118406336729363675711000348342713746016780773923827638902243253344914",
        "6981156750146001390596683852942006945948523736948468087198643842575491393764",
    ]

    assert len(proofs) == 1
    assert proofs[0].index == 0
    assert len(proofs[0].pub_signals) == len(pub_signals)
    assert all(
        proofs[0].pub_signals[i] == pub_signals[i] for i in range(len(pub_signals))
    )
