import os

from delta_node import config


__all__ = [
    "task_dir",
    "task_round_dir",
    "task_round_result_dir",
    "task_config_file",
    "task_weight_file",
    "task_result_file",
    "task_member_result_file",
    "task_masked_result_file"
]


def task_dir(task_id: str) -> str:
    dirname = os.path.join(config.task_dir, "coord", task_id)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return dirname


def task_round_dir(task_id: str, round: int) -> str:
    dirname = os.path.join(task_dir(task_id), str(round))
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return dirname


def task_round_result_dir(task_id: str, round: int) -> str:
    dirname = os.path.join(task_round_dir(task_id, round), "result")
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return dirname


def task_config_file(task_id: str) -> str:
    return os.path.join(task_dir(task_id), "task.config")


def task_weight_file(task_id: str, round: int) -> str:
    return os.path.join(task_round_dir(task_id, round), "task.weight")


def task_result_file(task_id: str) -> str:
    return os.path.join(task_dir(task_id), "task.result")


def task_member_result_file(task_id: str, round: int, address: str) -> str:
    return os.path.join(task_round_result_dir(task_id, round), f"{address}.result")


def task_masked_result_file(task_id: str, round: int) -> str:
    return os.path.join(task_round_dir(task_id, round), "masked.result")
