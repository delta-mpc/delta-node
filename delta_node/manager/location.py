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


def task_result_file(task_id: int) -> str:
    dirname = os.path.join(config.task_dir, "task", str(task_id), "result")
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return os.path.join(dirname, f"task.result")


def task_metrics_file(task_id: int, round_id: int) -> str:
    dirname = os.path.join(config.task_dir, "task", str(task_id), "metrics")
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return os.path.join(dirname, f"{round_id}.metrics")
