import math
from typing import List, Dict, Any

from delta.core.task import TaskType
from delta_node import entity, utils
from pydantic import BaseModel


class TaskConfig(BaseModel):
    name: str
    dataset: List[str]
    type: TaskType
    enable_verify: bool
    options: Dict[str, Any]


def create_task(task_config: TaskConfig, task_filename: str) -> entity.Task:
    dataset = ",".join(task_config.dataset)

    with open(task_filename, mode="rb") as f:
        commitment = utils.calc_commitment(f)

    if task_config.type == "hlr":
        tol = -int(math.log10(task_config.options["tol"]))
        task_item = entity.Task(
            creator="",
            task_id="",
            dataset=dataset,
            commitment=commitment,
            status=entity.TaskStatus.PENDING,
            name=task_config.name,
            type=task_config.type,
            enable_verify=task_config.enable_verify,
            tolerance=tol
        )
    elif task_config.type == "horizontal":
        task_item = entity.Task(
            creator="",
            task_id="",
            dataset=dataset,
            commitment=commitment,
            status=entity.TaskStatus.PENDING,
            name=task_config.name,
            type=task_config.type,
            enable_verify=False,
            tolerance=0,
        )
    else:
        raise TypeError(f"unknown task type {task_config.type}")
    return task_item
