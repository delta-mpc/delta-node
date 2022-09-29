from typing import List, Sequence
from delta_node import utils
from delta_node.crypto import ecdhe
import numpy as np
import os


def test_precision():
    precision = 8

    arr = np.random.random(10)
    arr_ = utils.unfix_precision(utils.fix_precision(arr, precision), precision)
    assert np.allclose(arr, arr_)


def test_mask():
    seed = os.urandom(32)
    mask = utils.make_mask(seed, (10,))
    mask_ = utils.make_mask(seed, (10,))
    assert np.array_equal(mask, mask_)


def generate_masked_arr(
    index: int,
    arr: np.ndarray,
    seed: bytes,
    sk: bytes,
    pks: Sequence[bytes],
    curve: ecdhe.EllipticCurve,
) -> np.ndarray:
    seed_mask = utils.make_mask(seed, arr.shape)

    sk_mask = np.zeros_like(arr, dtype=np.int64)
    for i, pk in enumerate(pks):
        if i != index:
            key = ecdhe.generate_shared_key(sk, pk, curve)
            mask = utils.make_mask(key, arr.shape)
            if index < i:
                sk_mask -= mask
            else:
                sk_mask += mask

    return utils.fix_precision(arr, 8) + seed_mask + sk_mask  # type:ignore


def test_calc():
    curve = ecdhe.CURVES["secp256k1"]
    seeds = [os.urandom(32) for _ in range(3)]
    sks, pks = zip(*[ecdhe.generate_key_pair(curve) for _ in range(3)])
    arrs = [np.random.random(10) for _ in range(3)]
    target = np.mean(arrs, 0)

    masked_arrs = [
        generate_masked_arr(i, arrs[i], seeds[i], sks[i], pks, curve) for i in range(3)
    ]
    masked_arr = np.sum(masked_arrs, 0)
    for seed in seeds:
        masked_arr -= utils.make_mask(seed, masked_arr.shape)
    
    unmask_arr = utils.unfix_precision(masked_arr, 8)
    target_ = unmask_arr / 3
    assert np.allclose(target, target_)
