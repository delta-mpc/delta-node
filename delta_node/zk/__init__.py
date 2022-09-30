import threading

from delta_node import config
from grpclib.client import Channel
from grpclib.config import Configuration

from .client import Client

_local = threading.local()

__all__ = ["get_client", "init", "close"]


def init(host: str = config.zk_host, port: int = config.zk_port, *, ssl: bool = False):
    if hasattr(_local, "ch") or hasattr(_local, "client"):
        raise ValueError("chain has been initialized")

    config = Configuration(
        _keepalive_time=60,
        _keepalive_timeout=20,
        _keepalive_permit_without_calls=True,
        _http2_max_pings_without_data=0,
    )
    ch = Channel(host, port, ssl=ssl, config=config)
    _local.ch = ch


def get_client() -> Client:
    if not hasattr(_local, "ch"):
        raise ValueError("zk channel has not been initialized")

    if not hasattr(_local, "client"):
        ch: Channel = _local.ch
        client = Client(ch)
        _local.client = client
        return client
    else:
        client: Client = _local.client
        return client


def close():
    if not hasattr(_local, "ch"):
        raise ValueError("chain channel has not been initialized")

    ch: Channel = _local.ch
    ch.close()
