import logging

from . import config


logger = logging.getLogger(__package__)

fmt = '%(asctime)s.%(msecs)03d - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(fmt, datefmt)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(config.log_level)
