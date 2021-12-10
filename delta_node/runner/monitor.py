import asyncio
import logging
from collections import defaultdict
from typing import Awaitable, Callable, Dict, List

from delta_node import chain, entity, registry

_logger = logging.getLogger(__name__)


EventCallback = Callable[[entity.Event], Awaitable[None]]


class Monitor(object):
    def __init__(self) -> None:
        self.callbacks: Dict[entity.EventType, List[EventCallback]] = defaultdict(list)

    async def start(self):
        node_address = await registry.get_node_address()
        async for event in chain.get_client().subscribe(node_address):
            callbacks = self.callbacks[event.type]
            for callback in callbacks:
                fut = asyncio.create_task(callback(event))

                def _done_callback(fut: asyncio.Task):
                    exc = fut.exception()
                    if exc is not None:
                        _logger.error(
                            f"event {event.type} callback {callback.__name__} error"
                        )
                        _logger.exception(exc)

                fut.add_done_callback(_done_callback)

    def register(self, event: entity.EventType, callback: EventCallback):
        self.callbacks[event].append(callback)
