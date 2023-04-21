import logging
import math
import os
import shutil
from tempfile import gettempdir
from typing import List, Optional

import sqlalchemy as sa
from delta_node import coord, db, entity, pool, registry
from delta_node.chain import hlr, horizontal
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ValidationError
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget

from delta_node.utils import random_str

_logger = logging.getLogger(__name__)

task_router = APIRouter(prefix="/task")


async def run_task(task_item: entity.Task, task_filename: str):
    node_address = await registry.get_node_address()

    try:
        if task_item.type == "horizontal":
            tx_hash, task_id = await horizontal.get_client().create_task(
                node_address, task_item.dataset, task_item.commitment, task_item.type
            )
        elif task_item.type == "hlr":
            tx_hash, task_id = await hlr.get_client().create_task(
                node_address,
                task_item.dataset,
                task_item.commitment,
                task_item.enable_verify,
                task_item.tolerance,
            )
        else:
            raise TypeError(f"unknown task type {task_item.type}")
    except Exception as e:
        async with db.session_scope() as sess:
            task_item.status = entity.TaskStatus.ERROR
            task_item = await sess.merge(task_item)
            sess.add(task_item)
            await sess.commit()
        _logger.error(f"create task of id {task_item.id} error: {str(e)}")
        raise

    task_item.task_id = task_id
    task_item.creator = node_address
    task_item.status = entity.TaskStatus.RUNNING

    final_task_file = coord.loc.task_config_file(task_id)
    await run_in_threadpool(shutil.move, task_filename, final_task_file)
    _logger.info(
        f"[Create Task] create task {task_id}",
        extra={"task_id": task_id, "tx_hash": tx_hash},
    )

    await coord.run_task(node_address, task_item)


class CreateTaskResp(BaseModel):
    task_id: int


async def parse_task_request(req: Request):
    task_filename = os.path.join(gettempdir(), "delta_" + random_str(10) + ".task")

    file_target = FileTarget(task_filename)
    config_target = ValueTarget()

    parser = StreamingFormDataParser(req.headers)
    parser.register("file", file_target)
    parser.register("config", config_target)

    async for chunk in req.stream():
        await run_in_threadpool(parser.data_received, chunk)

    if not os.path.isfile(task_filename):
        raise ValueError("task file is missing")
    if len(config_target.value) == 0:
        raise ValueError("task config file is missing")

    config = coord.TaskConfig.parse_raw(
        config_target.value, content_type="application/pickle", allow_pickle=True
    )
    return config, task_filename


@task_router.post("", response_model=CreateTaskResp)
async def create_task(
    req: Request,
    *,
    session: AsyncSession = Depends(db.get_session),
    background: BackgroundTasks,
):
    try:
        task_config, task_filename = await parse_task_request(req)
    except ValidationError as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))

    try:
        task_item = await pool.run_in_io(coord.create_task, task_config, task_filename)
    except TypeError as e:
        raise HTTPException(400, str(e))
    session.add(task_item)
    await session.commit()
    await session.refresh(task_item)

    background.add_task(run_task, task_item, task_filename)
    return CreateTaskResp(task_id=task_item.id)


class Task(BaseModel):
    id: int
    created_at: int
    name: str
    type: str
    creator: str
    status: str
    enable_verify: bool


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
                    enable_verify=task.enable_verify,
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
        enable_verify=task.enable_verify,
    )


def task_result_file(task_id: str) -> Optional[str]:
    result_filename = coord.loc.task_result_file(task_id)
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

    result_filename = await pool.run_in_io(task_result_file, task.task_id)
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
    id: int
    created_at: int
    message: str
    tx_hash: Optional[str] = None


@task_router.get("/logs", response_model=List[TaskLog])
async def get_task_logs(
    task_id: int = Query(..., ge=1),
    start: int = Query(0, ge=0),
    limit: int = Query(20, gt=0),
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
        .where(entity.Record.id >= start)
        .order_by(entity.Record.id)
        .limit(limit)
    )
    records: List[entity.Record] = (await session.execute(q)).scalars().all()

    logs = [
        TaskLog(
            id=record.id,
            created_at=int(record.created_at.timestamp() * 1000),
            message=record.message,
            tx_hash=record.tx_hash,
        )
        for record in records
    ]
    return logs


class TaskStatus(BaseModel):
    status: entity.TaskStatus

    class Config:
        use_enum_values = True


@task_router.get("/status", response_model=TaskStatus)
async def get_task_status(
    task_id: int = Query(..., ge=1), *, session: AsyncSession = Depends(db.get_session)
):
    q = sa.select(entity.Task).where(entity.Task.id == task_id)
    task: Optional[entity.Task] = (await session.execute(q)).scalar_one_or_none()
    if task is None:
        raise HTTPException(400, f"task {task_id} does not exist")

    res = TaskStatus(status=task.status)
    return res


router = APIRouter()
router.include_router(task_router)


class TasksPage(BaseModel):
    tasks: List[Task]
    total_pages: int


@router.get("/tasks", response_model=TasksPage)
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, gt=0),
    order: str = Query("desc", regex=r"^asc|desc$"),
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).limit(page_size).offset((page - 1) * page_size)
    if order == "asc":
        q = q.order_by(entity.Task.id)
    else:
        q = q.order_by(desc(entity.Task.id))
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
            enable_verify=task.enable_verify,
        )
        for task in tasks
    ]
    tasks_page = TasksPage(tasks=task_items, total_pages=total_pages)
    return tasks_page
