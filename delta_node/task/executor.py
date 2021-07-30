import asyncio
from delta_node.task.location import task_cfg_file, task_weight_file
import aiofiles
import websockets.client
import json
from typing import Union

from .. import node, model
from .task import add_task


async def _recv_file(websocket: websockets.client.WebSocketClientProtocol, filename: str):
    text = await websocket.recv()
    assert text == "start"
    async with aiofiles.open(filename, mode="wb") as f:
        while True:
            data = await websocket.recv()
            if isinstance(data, str):
                raise ValueError("except receive bytes, but got str")
            if len(data) == 0:
                break
            await f.write(data)
    text = await websocket.recv()
    assert text == "end"


class TaskExecutor(object):
    def __init__(self, task_id: int, url: str) -> None:
        self._task_id = task_id
        self._node_id = node.get_node_id()
        self._url = url

    async def run(self):

        loop = asyncio.get_event_loop()

        async with websockets.client.connect(f"{self._url}/{self._task_id}?id={self._node_id}") as websocket:
            metadata_str = await websocket.recv()
            metadata = json.loads(metadata_str)
            name = metadata["name"]
            type = metadata["type"]
            secure_level = metadata["secure_level"]
            algorithm = metadata["algorithm"]
            members = metadata["members"]

            # add task to db
            await loop.run_in_executor(
                None,
                add_task,
                name,
                type,
                secure_level,
                algorithm,
                members,
                self._url,
                self._node_id,
                self._task_id,
                model.TaskStatus.RUNNING,
            )

            stage = await websocket.recv()
            assert stage == "cfg"
            await _recv_file(websocket, task_cfg_file(self._task_id))
            
            while True:
                round_text = await websocket.recv()
                assert isinstance(round_text, str)
                assert round_text.startswith("round")
                round_id = int(round_text.split(":")[-1])
                
                stage = await websocket.recv()
                assert stage == "weight"
                await _recv_file(websocket, task_weight_file(self._task_id, round_id))


