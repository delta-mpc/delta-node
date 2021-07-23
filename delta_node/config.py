import os
from typing import Dict, List

import yaml

_config_path = os.getenv("HFL_CONFIG", "config_files/hfl_config.yaml")

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

_console: Dict = _c.get("console")
console_host: str = _console.get("host", None)
console_port: int = _console.get("port", None)
console_enabled: bool = bool(_console.get("enabled"))

_server: Dict = _c.get("server")
server_host: str = _server.get("host", None)
server_port: int = _server.get("port", None)
server_task_dir: str = _server.get("task_dir", None)
server_storage_dir: str = _server.get("storage_dir", None)

_client: Dict = _c.get("client")
client_data_paths: List[str] = _client.get("data_paths", None)
