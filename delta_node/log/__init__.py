import logging
import multiprocessing as mp
from logging.handlers import QueueHandler, QueueListener
from typing import Optional

from delta_node import config, pool
from . import db_handler, file_handler, stream_handler


def create_log_listener():
    listener = QueueListener(
        pool.LOG_QUEUE,
        stream_handler.handler,
        file_handler.handler,
        db_handler.handler,
    )
    return listener


def init():
    handler = QueueHandler(pool.LOG_QUEUE)
    for name in ["delta_node", "delta"]:
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(config.log_level)
