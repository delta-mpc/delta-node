import logging
import os
from logging.handlers import RotatingFileHandler

from . import config


def init():
    logger = logging.getLogger(__package__)

    fmt = "%(asctime)s.%(msecs)03d - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt, datefmt)

    std_handler = logging.StreamHandler()
    std_handler.setFormatter(formatter)
    logger.addHandler(std_handler)

    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir, exist_ok=True)

    log_filename = os.path.join(config.log_dir, "log.txt")
    file_handler = RotatingFileHandler(
        log_filename,
        encoding="utf-8",
        delay=True,
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
    )
    logger.addHandler(file_handler)

    logger.setLevel(config.log_level)
