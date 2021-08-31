from typing import IO

import delta.serialize
from delta.task import HorizontolTask
from delta_node import config
from sqlalchemy.orm import Session

from .. import contract, db, model, node, serialize
from .location import task_cfg_file, task_weight_file
from ..exceptions import TaskCreateError


@db.with_session
def create_task(task_file: IO[bytes], *, session: Session = None):
    assert session is not None
    task = delta.serialize.load_task(task_file)
    if task.type not in ["horizontal"]:
        raise TaskCreateError(f"unknown task type {task.type}")

    node_id = node.get_node_id(session=session)
    task_id = contract.create_task(node_id, task.name)

    with open(task_cfg_file(task_id), mode="wb") as f:
        task.dump(f)

    if task.type == "horizontol":
        assert isinstance(task, HorizontolTask), TaskCreateError("task type not match task.type")
        with open(task_weight_file(task_id, 0), mode="wb") as f:
            weight_arr = task.get_weight()
            serialize.dump_arr(f, weight_arr)

    task_item = model.Task(
        name=task.name,
        type=task.type,
        dataset=task.dataset,
        url=config.node_address,
        node_id=node_id,
        task_id=task_id,
        status=model.TaskStatus.PENDING,
    )
    session.add(task_item)
    session.commit()
    return task_id
