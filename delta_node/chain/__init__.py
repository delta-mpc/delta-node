import threading

from delta_node import config
from grpclib.client import Channel
from grpclib.config import Configuration

from .client import ChainClient

__all__ = ["init", "get_client", "close"]

_local = threading.local()


def init(
    host: str = config.chain_host, port: int = config.chain_port, *, ssl: bool = False
):
    if hasattr(_local, "ch") or hasattr(_local, "client"):
        raise ValueError("chain has been initialized")

    config = Configuration(
        _keepalive_time=10,
        _keepalive_timeout=5,
        _keepalive_permit_without_calls=True,
        _http2_max_pings_without_data=0,
    )
    ch = Channel(host, port, ssl=ssl, config=config)
    client = ChainClient(ch)
    _local.ch = ch
    _local.client = client


def get_client() -> ChainClient:
    if not hasattr(_local, "client"):
        raise ValueError("chain has not been initialized")

    client: ChainClient = _local.client
    return client


def close():
    if (not hasattr(_local, "client")) or (not hasattr(_local, "ch")):
        raise ValueError("chain has not been initialized")

    ch: Channel = _local.ch
    ch.close()
    delattr(_local, "ch")
    delattr(_local, "client")
