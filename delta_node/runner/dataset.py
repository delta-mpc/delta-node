import os

from delta_node import config


def check_dataset(dataset: str):
    return os.path.exists(os.path.join(config.task_dir, dataset))
