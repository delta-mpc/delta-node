import logging
import time
import threading
from selectors import EVENT_READ, DefaultSelector
from tempfile import TemporaryFile
from typing import IO, Dict, List, Optional

from .. import config
from .channel import InnerChannel
from .msg import Message


_logger = logging.getLogger(__name__)

class ChannelGroup(object):
    def __init__(self) -> None:
        self._channels: Dict[str, InnerChannel] = {}
        self._channel_cond = threading.Condition()

        self._selector = DefaultSelector()

    def register(self, member_id: str, ch: InnerChannel):
        with self._channel_cond:
            self._channels[member_id] = ch
            self._channel_cond.notify(1)
            self._selector.register(ch, EVENT_READ, data=member_id)

    def wait(self, member_ids: List[str], timeout: Optional[float] = None) -> List[str]:
        with self._channel_cond:
            self._channel_cond.wait_for(lambda: len(self._channels) == len(member_ids), timeout=timeout)
        return list(self._channels.keys())

    def close(self):
        self._selector.close()
        for ch in self._channels.values():
            ch.close()
        self._channels.clear()

    def recv_msg(self, member_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        if member_id in self._channels:
            ch = self._channels[member_id]
            return ch.recv(timeout=timeout)

    def recv_msgs(self, member_ids: List[str], timeout: Optional[float] = None) -> Dict[str, Message]:
        for member_id in member_ids:
            ch = self._channels[member_id]
            ch.ready_to_read()

        result = {}
        remaining = timeout
        while len(result) < len(member_ids) and (remaining is None or remaining > 0):
            start = time.time()
            events = self._selector.select(remaining)
            end = time.time()
            if remaining is not None:
                remaining -= end - start
            for key, _ in events:
                member_id = key.data
                ch = self._channels[member_id]
                msg = ch._recv()
                result[member_id] = msg
        return result

    def send_msg(self, member_id: str, msg: Message):
        if member_id in self._channels:
            ch = self._channels[member_id]
            ch.send(msg)

    def send_msgs(self, messages: Dict[str, Message]):
        for member_id, msg in messages.items():
            ch = self._channels[member_id]
            ch.send(msg)

    def recv_file(self, member_id: str, timeout: Optional[float] = None) -> Optional[IO[bytes]]:
        if member_id in self._channels:
            file = TemporaryFile()

            remaining = timeout
            while True:
                start = time.time()
                chunk = self.recv_msg(member_id, remaining)
                end = time.time()
                if remaining is not None:
                    remaining -= end - start
                assert chunk is not None
                assert chunk.type == "file"
                if len(chunk.content) == 0:
                    break
                file.write(chunk.content)
            file.seek(0)
            return file

    def recv_files(self, member_ids: List[str], timeout: Optional[float] = None) -> Dict[str, IO[bytes]]:
        _logger.info("recv files")
        temp_files: Dict[str, IO[bytes]] = {}

        unfinished = member_ids.copy()
        remaining = timeout
        while len(unfinished) > 0:
            start = time.time()
            data = self.recv_msgs(unfinished, remaining)
            _logger.info(f"recv data from {data.keys()}")
            end = time.time()
            if remaining is not None:
                remaining -= end - start
            for member_id, chunk in data.items():
                assert chunk.type == "file"
                if len(chunk.content) == 0:
                    unfinished.remove(member_id)
                else:
                    if member_id not in temp_files:
                        temp_files[member_id] = TemporaryFile(mode="w+b")
                    file = temp_files[member_id]
                    file.write(chunk.content)
        _logger.info("recv files complete")

        for member_id in unfinished:
            temp_files.pop(member_id)

        for file in temp_files.values():
            file.seek(0)
        return temp_files

    def send_file(self, member_id: str, file: IO[bytes]):
        if member_id in self._channels:
            while True:
                chunk = file.read(config.MAX_BUFF_SIZE)
                self.send_msg(member_id, Message(type="file", content=chunk))
                if len(chunk) == 0:
                    break

    def send_files(self, files: Dict[str, IO[bytes]]):
        finished = set()
        while len(finished) < len(files):
            for member_id, file in files.items():
                if member_id in finished:
                    break
                chunk = file.read(config.MAX_BUFF_SIZE)
                self.send_msg(member_id, Message(type="file", content=chunk))
                if len(chunk) == 0:
                    finished.add(member_id)
                    break
