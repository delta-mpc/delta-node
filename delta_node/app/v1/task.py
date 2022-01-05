import asyncio
import logging
import math
import os
import shutil
from typing import IO, List, Optional

import sqlalchemy as sa
from delta_node import chain, coord, db, entity, pool, registry
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

_logger = logging.getLogger(__name__)

task_router = APIRouter(prefix="/task")


class CreateTaskResp(BaseModel):
    task_id: str


def dump_task(task_id: str, task_file: IO[bytes]):
    task_file.seek(0)
    with open(coord.task_config_file(task_id), mode="wb") as f:
        shutil.copyfileobj(task_file, f)
        _logger.debug(f"save task config file of {task_id}")


@task_router.post("", response_model=CreateTaskResp)
async def create_task(
    *,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
    background: BackgroundTasks,
):
    loop = asyncio.get_running_loop()
    task_item = await loop.run_in_executor(pool.IO_POOL, coord.create_task, file.file)
    node_address = await registry.get_node_address()
    tx_hash, task_id = await chain.get_client().create_task(
        node_address, task_item.dataset, task_item.commitment, task_item.type
    )
    task_item.creator = node_address
    task_item.task_id = task_id
    task_item.status = entity.TaskStatus.RUNNING
    session.add(task_item)
    await session.commit()

    await loop.run_in_executor(pool.IO_POOL, dump_task, task_id, file.file)
    _logger.info(
        f"create task {task_id}", extra={"task_id": task_id, "tx_hash": tx_hash}
    )

    background.add_task(coord.run_task, task_id)
    return CreateTaskResp(task_id=task_id)


class Task(BaseModel):
    id: str
    created_at: int
    name: str
    type: str
    creator: str
    status: str


@task_router.get("/list", response_model=List[Task])
async def get_task_list(
    task_ids: List[str] = Query(...),
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.task_id.in_(task_ids))  # type: ignore
    tasks: List[entity.Task] = (await session.execute(q)).scalars().all()
    task_dict = {task.task_id: task for task in tasks}
    task_items = []
    for task_id in task_ids:
        task = task_dict[task_id]
        task_items.append(
            Task(
                id=task.task_id,
                created_at=task.created_at,
                name=task.name,
                type=task.type,
                creator=task.creator,
                stauts=task.status.name,
            )
        )
    return task_items


@task_router.get("/metadata", response_model=Task)
async def get_task_metadata(
    task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+"),
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.task_id == task_id)
    task: Optional[entity.Task] = (await session.execute(q)).scalar_one_or_none()
    if task is None:
        raise HTTPException(400, f"task {task_id} does not exist")

    return Task(
        id=task.task_id,
        created_at=task.created_at,
        name=task.name,
        type=task.type,
        creator=task.creator,
        stauts=task.status.name,
    )


@task_router.get("/result")
def get_task_result(task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+")):
    result_filename = coord.task_result_file(task_id)
    if not os.path.exists(result_filename):
        raise HTTPException(400, f"task {task_id} does not exist")

    def file_iter():
        chunk_size = 1024 * 1024
        with open(result_filename, mode="rb") as f:
            while True:
                content = f.read(chunk_size)
                if len(content) == 0:
                    break
                yield content

    return StreamingResponse(
        file_iter(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={task_id}.result"},
    )


class TaskLog(BaseModel):
    created_at: int
    message: str
    tx_hash: Optional[str] = None


@task_router.get("/logs", response_model=List[TaskLog])
async def get_task_logs(
    task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, gt=0),
    *,
    session: AsyncSession = Depends(db.get_session),
):
    q = (
        sa.select(entity.Record)
        .where(entity.Record.task_id == task_id)
        .order_by(entity.Record.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    records: List[entity.Record] = (await session.execute(q)).scalars().all()

    logs = [
        TaskLog(
            created_at=int(record.created_at.timestamp()),
            message=record.message,
            tx_hash=record.tx_hash,
        )
        for record in records
    ]
    return logs


router = APIRouter()
router.include_router(task_router)


class TasksPage(BaseModel):
    tasks: List[Task]
    total_pages: int


@router.get("/tasks", response_model=TasksPage)
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, gt=0),
    session: AsyncSession = Depends(db.get_session),
):
    q = (
        sa.select(entity.Task)
        .order_by(entity.Task.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    tasks: List[entity.Task] = (await session.execute(q)).scalars().all()

    q = sa.select(sa.func(entity.Task.id))
    task_count = (await session.execute(q)).scalar_one()

    total_pages = math.ceil(task_count / page_size)

    task_items = [
        Task(
            id=task.task_id,
            created_at=task.created_at,
            name=task.name,
            type=task.type,
            creator=task.creator,
            stauts=task.status.name,
        )
        for task in tasks
    ]
    tasks_page = TasksPage(tasks=task_items, total_pages=total_pages)
    return tasks_page
