import os

from .. import config


def task_state_file(task_id: int, round_id: int) -> str:
    dirname = os.path.join(config.task_dir, "task", str(task_id), "state")
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return os.path.join(dirname, f"{round_id}.state")
