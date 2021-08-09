import os
from typing import Dict, List

import yaml

_config_path = os.getenv("DELTA_NODE_CONFIG", "config/config.yaml")

with open(_config_path, mode="r", encoding="utf-8") as f:
    _c = yaml.safe_load(f)

_log = _c.get("log")
log_level: str = _log.get("level", "DEBUG")
log_dir: str = _log.get("dir", "logs")

db: str = _c.get("db")

_chain: Dict = _c.get("chain_connector")
chain_address: str = _chain.get("address", None)

_node_address: Dict = _c.get("node_address")
node_host: str = _node_address.get("host", None)
node_port: int = _node_address.get("port", 6800)
node_address = f"{node_host}:{node_port}"

api_port: int = _c.get("api_port", 6700)

task_dir: str = _c.get("task_dir", "task")

data_dir: str = _c.get("data_dir", "data")

MAX_BUFF_SIZE = 128 * 1024