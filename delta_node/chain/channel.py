from typing import Dict, Optional, Type
from types import TracebackType

from collections import defaultdict
from grpclib.client import Channel


class ChannelWrapper(object):
    _channels: Dict[str, Channel] = {}
    _channel_ref_count: Dict[str, int] = defaultdict(int)

    def __init__(self, host: str, port: int, *, ssl: bool = False) -> None:
        if ssl:
            self.key = f"https://{host}:{port}"
        else:
            self.key = f"http://{host}:{port}"

        if self.key not in self._channels:
            self._channels[self.key] = Channel(host=host, port=port, ssl=ssl)
            self._channel_ref_count[self.key] += 1

    @property
    def channel(self) -> Channel:
        return self._channels[self.key]

    def close(self):
        self.channel.close()
        self._channel_ref_count[self.key] -= 1
        if self._channel_ref_count[self.key] == 0:
            del self._channels[self.key]

    async def __aenter__(self) -> "ChannelWrapper":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()
