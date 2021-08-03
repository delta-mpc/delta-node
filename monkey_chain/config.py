import os
from typing import Dict

import yaml

_config_path = os.getenv("MONKEY_CHAIN_CONFIG", "config_files/monkey_chain_config.yaml")

with open(_config_path, mode="r", encoding="utf-8") as f:
    c = yaml.safe_load(f)

_log = c.get("log")
log_level = _log.get("level", "DEBUG")

db: str = c.get("db", "sqlite://")

_server: Dict = c.get("server", dict())
host: str = _server.get("host", "0.0.0.0")
port: int = _server.get("port", 32301)

