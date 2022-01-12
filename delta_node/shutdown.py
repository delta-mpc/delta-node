from typing import Any, Callable, List

_shutdown_handlers: List[Callable[[], None]] = []


__all__ = ["add_handler", "shutdown_handler"]


def add_handler(handler: Callable[[], None]):
    _shutdown_handlers.append(handler)


def shutdown_handler(*_: Any):
    for cb in _shutdown_handlers:
        cb()
