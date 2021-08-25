import logging
import multiprocessing as mp
from logging.handlers import QueueHandler, QueueListener
from typing import Optional

from .. import config
from . import db_handler, file_handler, stream_handler

_queue: Optional[mp.Queue] = None


def set_log_queue(queue: mp.Queue):
    global _queue
    assert _queue is None
    _queue = queue


def get_log_queue() -> mp.Queue:
    assert _queue is not None
    return _queue


def create_log_listener(queue: mp.Queue):
    listener = QueueListener(
        queue,
        stream_handler.handler,
        file_handler.handler,
        db_handler.handler,
    )
    listener.start()
    return listener


def init(queue):
    handler = QueueHandler(queue)
    for name in ["delta_node", "delta"]:
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(config.log_level)
