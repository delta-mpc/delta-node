import threading

from ..channel import get_channel
from .client import Client

_local = threading.local()

__all__ = ["get_client"]


def get_client() -> Client:
    if not hasattr(_local, "client"):
        ch = get_channel()
        client = Client(ch)
        _local.client = client
        return client
    else:
        client: Client = _local.client
        return client
