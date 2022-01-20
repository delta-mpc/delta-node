import asyncio
import logging
import math
import os
import shutil
from tempfile import TemporaryFile
from typing import IO, List, Optional

import sqlalchemy as sa
from delta_node import chain, coord, db, entity, pool, registry
from fastapi import (APIRouter, BackgroundTasks, Depends, File, HTTPException,
                     Query, UploadFile)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

_logger = logging.getLogger(__name__)

task_router = APIRouter(prefix="/task")


def create_task_file(task_file: IO[bytes]):
    f = TemporaryFile(mode="w+b")
    shutil.copyfileobj(task_file, f)
    return f


def move_task_file(task_file: IO[bytes], task_id: str):
    task_file.seek(0)
    with open(coord.task_config_file(task_id), mode="wb") as f:
        shutil.copyfileobj(task_file, f)
    task_file.close()


async def run_task(id: int, task_file: IO[bytes]):
    node_address = await registry.get_node_address()

    async with db.session_scope() as sess:
        q = sa.select(entity.Task).where(entity.Task.id == id)
        task_item: entity.Task = (await sess.execute(q)).scalar_one()

        tx_hash, task_id = await chain.get_client().create_task(
            node_address, task_item.dataset, task_item.commitment, task_item.type
        )
        task_item.task_id = task_id
        task_item.creator = node_address
        task_item.status = entity.TaskStatus.RUNNING
        sess.add(task_item)
        await sess.commit()

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(pool.IO_POOL, move_task_file, task_file, task_id)
    _logger.info(
        f"[Create Task] create task {task_id}", extra={"task_id": task_id, "tx_hash": tx_hash}
    )

    await coord.run_task(task_id)


class CreateTaskResp(BaseModel):
    task_id: int


@task_router.post("", response_model=CreateTaskResp)
async def create_task(
    *,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
    background: BackgroundTasks,
):
    loop = asyncio.get_running_loop()
    f = await loop.run_in_executor(pool.IO_POOL, create_task_file, file.file)
    task_item = await loop.run_in_executor(pool.IO_POOL, coord.create_task, f)
    session.add(task_item)
    await session.commit()
    await session.refresh(task_item)

    background.add_task(run_task, task_item.id, f)
    return CreateTaskResp(task_id=task_item.id)


class Task(BaseModel):
    id: int
    created_at: int
    name: str
    type: str
    creator: str
    status: str


@task_router.get("/list", response_model=List[Task])
async def get_task_list(
    task_ids: List[int] = Query(...),
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.id.in_(task_ids))  # type: ignore
    tasks: List[entity.Task] = (await session.execute(q)).scalars().all()
    task_dict = {task.id: task for task in tasks}
    task_items = []
    for task_id in task_ids:
        if task_id in task_dict:
            task = task_dict[task_id]
            task_items.append(
                Task(
                    id=task.id,
                    created_at=int(task.created_at.timestamp() * 1000),
                    name=task.name,
                    type=task.type,
                    creator=task.creator,
                    status=task.status.name,
                )
            )
    return task_items


@task_router.get("/metadata", response_model=Task)
async def get_task_metadata(
    task_id: int = Query(..., ge=1),
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.id == task_id)
    task: Optional[entity.Task] = (await session.execute(q)).scalar_one_or_none()
    if task is None:
        raise HTTPException(400, f"task {task_id} does not exist")

    return Task(
        id=task.id,
        created_at=int(task.created_at.timestamp() * 1000),
        name=task.name,
        type=task.type,
        creator=task.creator,
        status=task.status.name,
    )


def task_result_file(task_id: str) -> Optional[str]:
    result_filename = coord.task_result_file(task_id)
    if os.path.exists(result_filename):
        return result_filename


@task_router.get("/result")
async def get_task_result(
    task_id: int = Query(..., ge=1), session: AsyncSession = Depends(db.get_session)
):
    q = sa.select(entity.Task).where(entity.Task.id == task_id)
    task: Optional[entity.Task] = (await session.execute(q)).scalar_one_or_none()
    if task is None:
        raise HTTPException(400, f"task {task_id} does not exist")

    loop = asyncio.get_running_loop()
    result_filename = await loop.run_in_executor(
        pool.IO_POOL, task_result_file, task.task_id
    )
    if result_filename is None:
        raise HTTPException(400, f"task {task_id} is not finished")

    def file_iter(filename: str):
        chunk_size = 1024 * 1024
        with open(filename, mode="rb") as f:
            while True:
                content = f.read(chunk_size)
                if len(content) == 0:
                    break
                yield content

    return StreamingResponse(
        file_iter(result_filename),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={task_id}.result"},
    )


class TaskLog(BaseModel):
    created_at: int
    message: str
    tx_hash: Optional[str] = None


@task_router.get("/logs", response_model=List[TaskLog])
async def get_task_logs(
    task_id: int = Query(..., ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, gt=0),
    *,
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.id == task_id)
    task: Optional[entity.Task] = (await session.execute(q)).scalar_one_or_none()
    if task is None:
        raise HTTPException(400, f"task {task_id} does not exist")

    q = (
        sa.select(entity.Record)
        .where(entity.Record.task_id == task.task_id)
        .order_by(entity.Record.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    records: List[entity.Record] = (await session.execute(q)).scalars().all()

    logs = [
        TaskLog(
            created_at=int(record.created_at.timestamp() * 1000),
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

    q = sa.select(sa.func.count(entity.Task.id))
    task_count = (await session.execute(q)).scalar_one()

    total_pages = math.ceil(task_count / page_size)

    task_items = [
        Task(
            id=task.id,
            created_at=int(task.created_at.timestamp() * 1000),
            name=task.name,
            type=task.type,
            creator=task.creator,
            status=task.status.name,
        )
        for task in tasks
    ]
    tasks_page = TasksPage(tasks=task_items, total_pages=total_pages)
    return tasks_page
