from delta_node.model import task
from .. import config
import os.path

__all__ = ["task_cfg_file", "task_weight_file"]

def task_cfg_file(task_id: int):
    return os.path.join(config.server_storage_dir, "cfg", str(task_id) + ".cfg")


def task_weight_file(task_id: int):
    return os.path.join(config.server_storage_dir, "weight", str(task_id) + ".weight")
