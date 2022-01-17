import logging
import os
from logging import LogRecord
from logging.handlers import RotatingFileHandler
from typing import List

from .. import config


def create_handlers() -> List[logging.Handler]:
    datefmt = "%Y-%m-%d %H:%M:%S"
    common_fmt = "%(asctime)s.%(msecs)03d - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    tx_fmt = common_fmt + " tx hash: %(tx_hash)s"

    common_formatter = logging.Formatter(common_fmt, datefmt)
    tx_formatter = logging.Formatter(tx_fmt, datefmt)

    class CommonFilter(logging.Filter):
        def filter(self, record: LogRecord) -> bool:
            tx_hash = getattr(record, "tx_hash", None)
            return tx_hash is None

    class TxFilter(logging.Filter):
        def filter(self, record: LogRecord) -> bool:
            tx_hash = getattr(record, "tx_hash", None)
            return tx_hash is not None

    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir, exist_ok=True)
    log_filename = os.path.join(config.log_dir, "log.txt")

    common_handler = RotatingFileHandler(
        log_filename,
        encoding="utf-8",
        delay=True,
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
    )
    common_handler.setFormatter(common_formatter)
    common_handler.addFilter(CommonFilter())

    tx_handler = RotatingFileHandler(
        log_filename,
        encoding="utf-8",
        delay=True,
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
    )
    tx_handler.setFormatter(tx_formatter)
    tx_handler.addFilter(TxFilter())

    return [common_handler, tx_handler]
