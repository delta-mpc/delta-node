from __future__ import annotations

import asyncio
import concurrent.futures
import multiprocessing as mp
import os
from functools import partial
from typing import Any, Callable, Dict, Iterable, Iterator, MutableMapping, TypeVar

import cloudpickle as pickle
from typing_extensions import ParamSpec

__all__ = ["run_in_io", "run_in_worker", "MPCache", "map_in_io", "map_in_worker"]

cpu_count = os.cpu_count()

_MANAGER = mp.Manager()

LOG_QUEUE = _MANAGER.Queue()


_P = ParamSpec("_P")
_T = TypeVar("_T")


def map_in_io(
    func: Callable[_P, _T],
    *iterables: Iterable[Any],
    timeout: float | None = None,
    chunksize: int = 1,
) -> Iterator[_T]:
    with concurrent.futures.ThreadPoolExecutor(cpu_count) as pool:
        return pool.map(func, *iterables, timeout=timeout, chunksize=chunksize)


def map_in_worker(
    func: Callable[_P, _T],
    *iterables: Iterable[Any],
    timeout: float | None = None,
    chunksize: int = 1,
) -> Iterator[_T]:
    with concurrent.futures.ThreadPoolExecutor(cpu_count) as pool:
        return pool.map(func, *iterables, timeout=timeout, chunksize=chunksize)


async def run_in_io(
    func: Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    loop = asyncio.get_running_loop()
    partial_func = partial(func, *args, **kwargs)
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        return await loop.run_in_executor(pool, partial_func)


def _mp_func(func_bytes: bytes) -> bytes:
    f = pickle.loads(func_bytes)
    res = f()
    return pickle.dumps(res)


async def run_in_worker(
    func: Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    loop = asyncio.get_running_loop()
    partial_func = partial(func, *args, **kwargs)

    func_bytes = pickle.dumps(partial_func)
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        res_bytes = await loop.run_in_executor(pool, _mp_func, func_bytes)
    res = pickle.loads(res_bytes)
    return res


_KT = TypeVar("_KT", contravariant=True)
_VT = TypeVar("_VT")


class MPCache(MutableMapping[_KT, _VT]):
    def __init__(self) -> None:
        self.cache: Dict[_KT, bytes] = _MANAGER.dict()  # type: ignore

    def __getitem__(self, __k: _KT) -> _VT:
        return pickle.loads(self.cache[__k])

    def __setitem__(self, __k: _KT, __v: _VT) -> None:
        self.cache[__k] = pickle.dumps(__v)

    def __delitem__(self, __v: _KT) -> None:
        del self.cache[__v]

    def __iter__(self) -> Iterator[_KT]:
        return iter(self.cache)

    def __len__(self) -> int:
        return len(self.cache)
