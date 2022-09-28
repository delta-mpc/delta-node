from typing import IO

import delta
import delta.serialize
from delta_node import entity, utils


def create_task(task_file: IO[bytes]) -> entity.Task:
    task_file.seek(0)

    task = delta.serialize.load_task(task_file)
    dataset = ",".join(task.dataset)

    task_file.seek(0)
    commitment = utils.calc_commitment(task_file)

    if task.type == "hlr":
        task_item = entity.Task(
            creator="",
            task_id="",
            dataset=dataset,
            commitment=commitment,
            status=entity.TaskStatus.PENDING,
            name=task.name,
            type=task.type,
            enable_verify=task.enable_verify,  # type: ignore
            tolerance=task.options["tol"],  # type: ignore
        )
    elif task.type == "horizontal":
        task_item = entity.Task(
            creator="",
            task_id="",
            dataset=dataset,
            commitment=commitment,
            status=entity.TaskStatus.PENDING,
            name=task.name,
            type=task.type,
            enable_verify=False,
            tolerance=0,
        )
    else:
        raise TypeError(f"unknown task type {task.type}")
    return task_item
