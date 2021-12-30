import os

from delta_node import config


__all__ = ["task_config_file", "task_state_file", "task_result_file", "task_metrics_file", "task_weight_file"]


def task_dir(task_id: str) -> str:
    dirname = os.path.join(config.task_dir, "runner", task_id)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return dirname


def task_config_file(task_id: str) -> str:
    return os.path.join(task_dir(task_id), "task.config")


def task_state_file(task_id: str) -> str:
    return os.path.join(task_dir(task_id), "task.state")


def task_result_file(task_id: str, round: int) -> str:
    return os.path.join(task_dir(task_id), f"task.{round}.result")


def task_weight_file(task_id: str, round: int) -> str:
    return os.path.join(task_dir(task_id), f"task.{round}.weight")


def task_metrics_file(task_id: str, round: int) -> str:
    return os.path.join(task_dir(task_id), f"task.{round}.metrics")
    