import os
from .. import config


def task_cfg_file(task_id: int):
    return os.path.join(config.server_storage_dir, "cfg", str(task_id) + ".cfg")


def task_weight_file(task_id: int):
    return os.path.join(config.server_storage_dir, "weight", str(task_id) + ".weight")
