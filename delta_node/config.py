import os
from typing import Dict

import yaml

_config_path = os.getenv("DELTA_NODE_CONFIG", "config/config.yaml")

with open(_config_path, mode="r", encoding="utf-8") as f:
    _c = yaml.safe_load(f)

_log = _c.get("log")
log_level: str = _log.get("level", "DEBUG")
log_dir: str = _log.get("dir", "logs")

db: str = _c.get("db")

_chain: Dict = _c.get("chain_connector")
chain_host: str = _chain.get("host", "")
chain_port: int = _chain.get("port", 4500)
chain_heartbeat: int = _chain.get("heartbeat", 30)
chain_retry: int = _chain.get("retry", 3)

_node: Dict = _c.get("node")
node_name: str = _node.get("name", "")
node_url: str = _node.get("url", "")

_zk: Dict = _c.get("zk")
zk_host: str = _zk.get("host", "")
zk_port: int = _zk.get("port", 3400)

api_port: int = _c.get("api_port", 6700)

task_dir: str = _c.get("task_dir", "task")

data_dir: str = _c.get("data_dir", "data")

MAX_BUFF_SIZE = 128 * 1024
