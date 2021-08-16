import json
import logging
import shutil
from contextlib import contextmanager
from tempfile import TemporaryFile
from typing import List
from zipfile import ZipFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from delta_node.app import utils
from delta_node import db, model, manager

_logger = logging.getLogger(__name__)

router = APIRouter()


@contextmanager
def tmp_upload_file(file: UploadFile):
    with TemporaryFile() as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file.seek(0)
        yield temp_file
        file.file.close()
        _logger.info("upload file close")
    _logger.info("upload temp file close")


@router.post("/task", response_model=utils.CreateTaskResp)
def upload_task(
    file: UploadFile = File(...),
    session: Session = Depends(db.get_session),
):
    with tmp_upload_file(file) as tmp:
        with ZipFile(tmp, mode="r") as zip_f:
            namelist = zip_f.namelist()
            for name in ["metadata", "cfg", "weight"]:
                if name not in namelist:
                    err = f"missing {name} in task file"
                    _logger.error(err)
                    raise HTTPException(400, err)

            with zip_f.open("metadata", mode="r") as f:
                metadata = json.load(f)

            cfg_file = zip_f.open("cfg", mode="r")
            weight_file = zip_f.open("weight", mode="r")
            task_id = manager.create_task(
                metadata, cfg_file, weight_file, session=session
            )
            cfg_file.close()
            weight_file.close()

    resp = utils.CreateTaskResp(task_id=task_id)
    return resp


@router.get("/tasks", response_model=utils.TasksResp)
def get_tasks(
    page: int = 1, page_size: int = 20, *, session: Session = Depends(db.get_session)
):
    tasks = (
        session.query(model.Task)
        .order_by(desc(model.Task.id))
        .limit(page_size)
        .offset((page - 1) * page_size)
        .all()
    )
    task_count = session.query(func.count(model.Task.id)).scalar()
    page_count = (task_count + page_size - 1) // page_size

    task_items = [
        utils.Task(
            name=task.name,
            type=task.type,
            creator=task.node_id,
            id=task.task_id,
            created_at=task.created_at,
            status=model.TaskStatus(task.status).name,
        )
        for task in tasks
    ]
    resp = utils.TasksResp(tasks=task_items, total_pages=page_count)
    return resp


@router.get("/task/list", response_model=List[utils.Task])
def get_task_list(
    task_ids: List[int] = Query(...), *, session: Session = Depends(db.get_session)
):
    tasks = session.query(model.Task).filter(model.Task.task_id.in_(task_ids)).all()
    task_items = [
        utils.Task(
            name=task.name,
            type=task.type,
            creator=task.node_id,
            id=task.task_id,
            created_at=task.created_at,
            status=model.TaskStatus(task.status).name,
        )
        for task in tasks
    ]
    task_items = sorted(task_items, key=lambda task: task_ids.index(task.id))
    return task_items


@router.get("/task/metadata", response_model=utils.Task)
def get_task_metadata(task_id: int, *, session: Session = Depends(db.get_session)):
    task = session.query(model.Task).filter(model.Task.task_id == task_id).one_or_none()
    if task is None:
        raise HTTPException(400, f"no such task of task id {task_id}")

    task_item = utils.Task(
        name=task.name,
        type=task.type,
        creator=task.node_id,
        id=task.task_id,
        created_at=task.created_at,
        status=model.TaskStatus(task.status).name,
    )
    return task_item


@router.get("/task/logs", response_model=List[utils.TaskLog])
def get_task_logs(
    task_id: int,
    page: int = 1,
    page_size: int = 20,
    *,
    session: Session = Depends(db.get_session),
):
    logs = (
        session.query(model.Log)
        .filter(model.Log.task_id == task_id)
        .order_by(model.Log.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
        .all()
    )
    res = [
        utils.TaskLog(created_at=log.created_at, message=log.message) for log in logs
    ]
    return res