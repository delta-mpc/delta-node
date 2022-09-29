import threading

from delta_node import config
from grpclib.client import Channel
from grpclib.config import Configuration

__all__ = ["init", "get_channel", "close"]

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
    _local.ch = ch


def get_channel() -> Channel:
    if not hasattr(_local, "ch"):
        raise ValueError("chain channel has not been initialized")

    ch: Channel = _local.ch
    return ch


def close():
    if not hasattr(_local, "ch"):
        raise ValueError("chain channel has not been initialized")

    ch: Channel = _local.ch
    ch.close()
