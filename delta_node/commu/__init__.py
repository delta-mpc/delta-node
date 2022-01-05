from functools import lru_cache
from typing import Optional

import httpx

from .client import Client

__all__ = ["init", "get_client", "close"]

_client: Optional[httpx.Client] = None
_aclient: Optional[httpx.AsyncClient] = None


async def init():
    global _client, _aclient
    assert _client is None, "commu client has already been initialized"
    assert _aclient is None, "commu aclient has already been initialized"

    _client = httpx.Client()
    _aclient = httpx.AsyncClient()


@lru_cache(maxsize=128, typed=True)
def get_client(url: str):
    assert _client is not None, "commu client has not been initialized"
    assert _aclient is not None, "commu aclient has not been initialized"

    return Client(url, _client, _aclient)


async def close():
    global _client, _aclient

    if _client is not None:
        _client.close()
        _client = None

    if _aclient is not None:
        await _aclient.aclose()
        _aclient = None
