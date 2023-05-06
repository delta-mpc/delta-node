import threading

from delta_node import config
import grpc
from grpc.aio import Channel

from .client import Client

_local = threading.local()

__all__ = ["get_client", "init", "close"]


async def init(host: str = config.zk_host, port: int = config.zk_port, *, ssl: bool = False):
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


async def close():
    if not hasattr(_local, "ch"):
        raise ValueError("chain channel has not been initialized")

    ch: Channel = _local.ch
    await ch.close()
