from __future__ import annotations

import logging
import asyncio
from typing import Dict
from collections import defaultdict

from delta_node import entity

_logger = logging.getLogger(__name__)

class EventBox(object):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        
        self.lock = asyncio.Lock()
        self.conditions: Dict[entity.EventType, asyncio.Condition] = defaultdict(asyncio.Condition)
        self.bucket: Dict[entity.EventType, entity.TaskEvent] = {}

    async def get_condition(self, event_type: entity.EventType):
        async with self.lock:
            return self.conditions[event_type]

    async def remove_condition(self, event_type: entity.EventType):
        async with self.lock:
            self.conditions.pop(event_type)

    async def recv_event(self, event: entity.TaskEvent):
        if event.task_id == self.task_id:
            _logger.debug(f"event box {self.task_id} recv event {event.type}")
            condition = await self.get_condition(event.type)
            async with condition:
                self.bucket[event.type] = event
                condition.notify(1)

    async def wait_for_event(self, event_type: entity.EventType, timeout: float | None = None) -> entity.TaskEvent:
        _logger.debug(f"event box {self.task_id} wait for event {event_type}")
        condition = await self.get_condition(event_type)

        async def wait():
            async with condition:
                await condition.wait_for(lambda: event_type in self.bucket)
            
        await asyncio.wait_for(wait(), timeout=timeout)
        await self.remove_condition(event_type)

        return self.bucket.pop(event_type)
