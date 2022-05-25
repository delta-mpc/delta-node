from abc import ABC, abstractmethod

from delta.core.task import ClientContext
from delta_node import entity


class Manager(ABC):
    def __init__(self, task_id: str, ctx: ClientContext) -> None:
        self.task_id = task_id
        self.ctx = ctx

    @abstractmethod
    async def init(self):
        ...

    @abstractmethod
    async def run(self):
        ...

    @abstractmethod
    async def finish(self, success: bool):
        ...

