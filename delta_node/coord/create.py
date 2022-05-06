import shutil
import tempfile
from typing import IO, Tuple

import delta
import delta.serialize
from delta_node import entity, utils


def create_task(task_file: IO[bytes]) -> entity.Task:
    task_file.seek(0)

    task = delta.serialize.load_task(task_file)
    dataset = ",".join(task.dataset)

    task_file.seek(0)
    commitment = utils.calc_commitment(task_file)

    task_item = entity.Task(
        creator="",
        task_id="",
        dataset=dataset,
        commitment=commitment,
        status=entity.TaskStatus.PENDING,
        name=task.name,
        type=task.type,
    )
    return task_item
