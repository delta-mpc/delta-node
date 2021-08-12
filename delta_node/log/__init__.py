import logging
import multiprocessing as mp
from logging.handlers import QueueHandler, QueueListener

from .. import config
from . import db_handler, file_handler, stream_handler



def main_init(queue: mp.Queue):
    listener = QueueListener(
        queue,
        stream_handler.handler,
        file_handler.handler,
        db_handler.handler,
    )

    handler = QueueHandler(queue)
    logger = logging.getLogger("delta_node")
    logger.addHandler(handler)
    logger.setLevel(config.log_level)
    listener.start()
    return listener


def worker_init(queue):
    handler = QueueHandler(queue)
    logger = logging.getLogger("delta_node")
    logger.addHandler(handler)
    logger.setLevel(config.log_level)
