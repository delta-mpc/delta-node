from delta_node.channel.channel import new_channel_pair
import threading
from typing import Dict, List

from .. import channel
from .metadata import TaskMetadata
from .exceptions import TaskNoMemberError


class Aggregator(threading.Thread):
    def __init__(self, task_id: int, metadata: TaskMetadata) -> None:
        super().__init__()
        self._task_id = task_id
        self._member_ids = metadata.members
        self._secure_level = metadata.secure_level
        self._algorithm = metadata.algorithm
        
        self._channel_cond = threading.Condition()
        self._channels: Dict[str, channel.InnerChannel] = {}

    def connect(self, member_id: str):
        if member_id not in self._member_ids:
            raise TaskNoMemberError(self._task_id, member_id)
        with self._channel_cond:
            in_channel, out_channel = new_channel_pair()
            self._channels[member_id] = in_channel
            self._channel_cond.notify(1)
            return out_channel
    
    