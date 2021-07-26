import shutil
from typing import IO, Any, Dict

from delta_node import config
from sqlalchemy.orm import Session

from .. import contract, model, node
from .location import task_cfg_file, task_weight_file


def create_task(
    metadata: Dict[str, Any],
    cfg_file: IO[bytes],
    weight_file: IO[bytes],
    session: Session = None,
):
    assert session is not None
    name = metadata["name"]
    type = metadata["type"]
    secure_level = metadata["secure_level"]
    algorithm = metadata["algorithm"]
    members = metadata["members"]

    node_id = node.get_node_id(session)
    task_id = contract.create_task(node_id, name)

    # save cfg
    with open(task_cfg_file(task_id), mode="wb") as f:
        shutil.copyfileobj(cfg_file, f)
    # save weight
    with open(task_weight_file(task_id), mode="wb") as f:
        shutil.copyfileobj(weight_file, f)

    # add task to db
    task = model.Task(
        name=name,
        type=type,
        secure_level=secure_level,
        algorithm=algorithm,
        url=config.url,
        member_count=len(members),
        node_id=node_id,
        task_id=task_id,
        status=model.TaskStatus.INIT,
    )
    session.add(task)
    # add members to db
    task_members = []
    for member_id in members:
        member = model.TaskMember(task_id=task_id, node_id=member_id, joined=False)
        task_members.append(member)
    session.bulk_save_objects(task_members)
    session.commit()
