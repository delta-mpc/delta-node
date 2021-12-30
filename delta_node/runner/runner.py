from abc import ABC, abstractmethod
from typing import Callable

from delta_node import entity


class TaskRunner(ABC):
    @abstractmethod
    async def dispatch(self, event: entity.Event):
        pass
    
    @abstractmethod
    async def finish(self):
        pass
