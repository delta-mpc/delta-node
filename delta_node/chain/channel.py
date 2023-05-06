import threading

from delta_node import config

import grpc
from grpc.aio import Channel

__all__ = ["init", "get_channel", "close"]

_local = threading.local()


async def init(
    host: str = config.chain_host, port: int = config.chain_port, *, ssl: bool = False
):
    if hasattr(_local, "ch") or hasattr(_local, "client"):
        raise ValueError("chain has been initialized")

    endpoint = f"{host}:{port}"
    if ssl:
        ch = grpc.aio.secure_channel(
            target=endpoint, credentials=grpc.ssl_channel_credentials()
        )
    else:
        ch = grpc.aio.insecure_channel(target=endpoint)

    await ch.channel_ready()

    _local.ch = ch


def get_channel() -> Channel:
    if not hasattr(_local, "ch"):
        raise ValueError("chain channel has not been initialized")

    ch: Channel = _local.ch
    return ch


async def close():
    if not hasattr(_local, "ch"):
        raise ValueError("chain channel has not been initialized")

    ch: Channel = _local.ch
    await ch.close()
