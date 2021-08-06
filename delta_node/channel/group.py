import logging
import time
import threading
from selectors import EVENT_READ, DefaultSelector
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

    def recv_msg(self, member_id: str, timeout: Optional[float] = None) -> Message:
        assert member_id in self._channels
        ch = self._channels[member_id]
        return ch.recv(timeout=timeout)

    def recv_msgs(self, member_ids: List[str], timeout: Optional[float] = None) -> Dict[str, Message]:
        assert all(member_id in self._channels for member_id in member_ids)
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
        assert member_id in self._channels
        ch = self._channels[member_id]
        ch.send(msg)

    def send_msgs(self, messages: Dict[str, Message]):
        assert all(member_id in self._channels for member_id in messages)
        for member_id, msg in messages.items():
            ch = self._channels[member_id]
            ch.send(msg)

    def recv_file(self, member_id: str, dst: IO[bytes], timeout: Optional[float] = None) -> bool:
        assert member_id in self._channels
        ch = self._channels[member_id]
        return ch.recv_file(dst, timeout)

    def recv_files(self, dst_files: Dict[str, IO[bytes]], timeout: Optional[float] = None) -> Dict[str, bool]:
        assert all(member_id in self._channels for member_id in dst_files)

        finish_map = {member_id: False for member_id in dst_files}
        unfinished = list(dst_files.keys())
        remaining = timeout
        while len(unfinished) > 0 and (remaining is None or remaining > 0):
            start = time.time()
            data = self.recv_msgs(unfinished, remaining)
            end = time.time()
            if remaining is not None:
                remaining -= end - start
            for member_id, chunk in data.items():
                assert chunk.type == "file"
                if len(chunk.content) == 0:
                    finish_map[member_id] = True
                    unfinished.remove(member_id)
                else:
                    file = dst_files[member_id]
                    file.write(chunk.content)
        return finish_map

    def send_file(self, member_id: str, file: IO[bytes]):
        assert member_id in self._channels
        ch = self._channels[member_id]
        ch.send_file(file)

    def send_files(self, files: Dict[str, IO[bytes]]):
        assert all(member_id in self._channels for member_id in files)
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
