import logging

fmt = '%(asctime)s.%(msecs)03d - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(fmt, datefmt)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
