import os

from .. import config


def task_cfg_file(task_id: int) -> str:
    dirname = os.path.join(config.task_dir, "task", str(task_id))
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return os.path.join(dirname, "task.cfg")


def task_weight_file(task_id: int, round_id: int) -> str:
    dirname = os.path.join(config.task_dir, "task", str(task_id), "weight")
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return os.path.join(dirname, f"{round_id}.weight")


def task_result_file(task_id: int, round_id: int, member_id: str = None) -> str:
    dirname = os.path.join(config.task_dir, "task", str(task_id), "result")
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    if member_id is None:
        return os.path.join(dirname, f"{round_id}.result")
    else:
        return os.path.join(dirname, f"{round_id}.{member_id}.result")
