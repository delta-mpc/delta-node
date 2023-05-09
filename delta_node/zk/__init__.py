from contextlib import asynccontextmanager

import grpc
from grpc.aio import Channel

from delta_node import config

from .client import Client

__all__ = ["get_client", "Client"]


def _make_channel(host: str, port: int, *, ssl: bool) -> Channel:
    endpoint = f"{host}:{port}"
    if ssl:
        ch = grpc.aio.secure_channel(
            target=endpoint, credentials=grpc.ssl_channel_credentials()
        )
    else:
        ch = grpc.aio.insecure_channel(target=endpoint)

    return ch


@asynccontextmanager
async def get_client(
    host: str = config.zk_host, port: int = config.zk_port, *, ssl: bool = False
):
    ch = _make_channel(host=host, port=port, ssl=ssl)
    async with ch:
        client = Client(ch)
        yield client
