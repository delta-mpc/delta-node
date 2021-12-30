import shutil
import tempfile
from typing import IO

import delta
import delta.serialize
from delta_node import entity, utils


def create_task(task_file: IO[bytes]) -> entity.Task:
    with tempfile.TemporaryFile(mode="w+b") as f:
        shutil.copyfileobj(task_file, f)
        f.seek(0)

        task = delta.serialize.load_task(f)
        dataset = task.dataset

        f.seek(0)
        commitment = utils.calc_commitment(f)

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
