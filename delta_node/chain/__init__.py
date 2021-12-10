import threading

from delta_node import config
from grpclib.client import Channel

from .client import ChainClient

__all__ = ["init", "get_client", "close"]

_local = threading.local()


def init(
    host: str = config.node_host, port: int = config.node_port, *, ssl: bool = False
):
    if hasattr(_local, "ch") or hasattr(_local, "client"):
        raise ValueError("chain has been initialized")

    ch = Channel(host, port, ssl=ssl)
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
