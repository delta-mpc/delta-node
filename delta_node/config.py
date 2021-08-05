import os
from typing import Dict, List

import yaml

_config_path = os.getenv("DELTA_NODE_CONFIG", "config_files/config.yaml")

with open(_config_path, mode="r", encoding="utf-8") as f:
    _c = yaml.safe_load(f)

_log = _c.get("log")
log_level: str = _log.get("level", "DEBUG")
log_enable_db: bool = _log.get("enable_db")

db: str = _c.get("db")

_contract: Dict = _c.get("contract")
contract_address: str = _contract.get("address", None)
contract_impl: str = _contract.get("impl", None)

url: str = _c.get("url")

_server: Dict = _c.get("server")
server_host: str = _server.get("host", None)
server_port: int = _server.get("port", None)

storage_dir: str = _c.get("storage_dir", None)

data_dir: str = _c.get("data_dir", None)

MAX_BUFF_SIZE = 128 * 1024