from queue import Queue
from collections import defaultdict
import threading
import json
from tempfile import TemporaryFile

from typing import Dict, Iterator, List

from ..task.exceptions import TaskNoMemberError
from . import utils


class SimpleAggregator(threading.Thread):
    def __init__(self, task_id: int, member_ids: List[str]) -> None:
        super().__init__()
        self._task_id = task_id
        self._member_ids = member_ids

        self._input_stream_cond = threading.Condition()
        self._input_streams = {}
        self._output_queues = defaultdict(Queue)
        
        self._result_cond = threading.Condition()
        self._result = None

    def set_input_stream(self, member_id: str, stream: Iterator):
        if member_id in self._member_ids:
            with self._input_stream_cond:
                self._input_streams[member_id] = stream
                self._input_stream_cond.notify_all()
        else:
            raise TaskNoMemberError(self._task_id, member_id)

    @property
    def result(self):
        with self._result_cond:
            self._result_cond.wait()
            return self._result
    
    def run(self) -> None:
        with self._input_stream_cond:
            self._input_stream_cond.wait_for(lambda: len(self._member_ids) == len(self._input_streams))

        for member_id, stream in self._input_streams.items():
            init_msg = next(stream)
            assert init_msg.type == "init"
            assert init_msg.task_id == self._task_id
            assert init_msg.member_id == member_id

        pk_dict = {}
        for member_id, stream in self._input_streams.items():
            pk_msg = next(stream)
            assert pk_msg.type == "pk"
            assert pk_msg.task_id == self._task_id
            assert pk_msg.member_id == member_id
            pk: bytes = pk_msg.content
            pk_dict[member_id] = pk.decode("utf-8")
        pk_dict_bytes = json.dumps(pk_dict).encode("utf-8")

        for member_id, q in self._output_queues.items():
            q.put({"type": "pk", "content": pk_dict_bytes})
        
        results = []
        for member_id, stream in self._input_streams.items():
            with TemporaryFile(mode="w+b") as file:
                for msg in stream:
                    assert msg.type == "result"
                    assert msg.task_id == self._task_id
                    assert msg.member_id == member_id
                    if len(msg.content) == 0:
                        break
                    file.write(msg.content)
                arr = utils.load_arr(file)
                results.append(arr)
        result = utils.add_arrs(results)

        with self._result_cond:
            self._result = result
            self._result_cond.notify_all()

        for member_id, q in self._output_queues.items():
            q.put(None)
        

