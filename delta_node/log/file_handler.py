import os
import logging
from logging.handlers import RotatingFileHandler

from .. import config

if not os.path.exists(config.log_dir):
    os.makedirs(config.log_dir, exist_ok=True)

fmt = '%(asctime)s.%(msecs)03d - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(fmt, datefmt)

log_filename = os.path.join(config.log_dir, "log.txt")
handler = RotatingFileHandler(
    log_filename,
    encoding="utf-8",
    delay=True,
    maxBytes=50 * 1024 * 1024,
    backupCount=5,
)
handler.setFormatter(formatter)
