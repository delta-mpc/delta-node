from collections import defaultdict
from delta_node import model

from sqlalchemy.sql.functions import mode
from delta_node.task.manager import TaskManager
import json
import logging
import shutil
from tempfile import TemporaryFile
from contextlib import contextmanager
from typing import Dict
from zipfile import ZipFile
import threading

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import db, task
from . import utils

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task")


_task_manager_registry: Dict[int, task.TaskManager] = {}
_task_manager_lock: Dict[int, threading.Lock] = defaultdict(threading.Lock)


def _get_task_manager(
    task_id: int, *, session: Session = Depends(db.get_session)
) -> TaskManager:
    lock = _task_manager_lock[task_id]
    with lock:
        if task_id not in _task_manager_registry:
            try:
                manager = task.TaskManager(task_id, session=session)
                _task_manager_registry[task_id] = manager
            except task.TaskNotReadyError as e:
                _logger.info(str(e))
                raise HTTPException(500, f"task {task_id} is not ready")
        return _task_manager_registry[task_id]


@contextmanager
def tmp_upload_file(file: UploadFile):
    with TemporaryFile() as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file.seek(0)
        yield temp_file
        file.file.close()
        _logger.info("upload file close")
    _logger.info("upload temp file close")


@router.post("", response_model=utils.CommonResp)
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
            task.create_task(metadata, cfg_file, weight_file, session=session)
            cfg_file.close()
            weight_file.close()

    resp = utils.CommonResp(
        status=utils.RespStatus.SUCCESS,
    )
    return resp


@router.get("/{task_id}/cfg")
def get_cfg_file(
    task_id: int = Path(...),
    member: str = Query(...),
    session: Session = Depends(db.get_session),
    manager: task.TaskManager = Depends(_get_task_manager),
):  
    try:
        manager.join(member_id=member, session=session)
        cfg_file = task.task_cfg_file(task_id)
        f = open(cfg_file, mode="rb")
        return StreamingResponse(f, media_type="application/octet-stream",
                                headers={"Content-Disposition": f"attachment; filename={cfg_file}"})
    except task.TaskError as e:
        _logger.error(str(e))
        raise HTTPException(400, str(e))


@router.get("/{task_id}/weight")
def get_weight_file(
    task_id: int = Path(...),
    member: str = Query(...),
    session: Session = Depends(db.get_session),
    manager: task.TaskManager = Depends(_get_task_manager),
):  
    try:
        round_id = manager.start_round(member_id=member, session=session)
        weight_file = task.task_weight_file(task_id, round_id)
        f = open(weight_file, mode="rb")
        return StreamingResponse(f, media_type="application/octet-stream",
                            headers={"Content-Disposition": f"attachment; filename={weight_file}"})
    except task.TaskError as e:
        _logger.error(str(e))
        raise HTTPException(400, str(e))


@router.post("/{task_id}/result")
def upload_result(
    task_id: int = Path(...),
    member: str = Query(...),
    round: int = Query(...),
    file: UploadFile = File(...),
    session: Session = Depends(db.get_session),
    manager: task.TaskManager = Depends(_get_task_manager),
):  
    try:
        status = manager.round_status(member, round, session=session)
        if status == model.RoundStatus.RUNNING:
            res_file = task.task_result_file(task_id, round, member)
            with tmp_upload_file(file) as tmp, open(res_file, mode="wb") as f:
                shutil.copyfileobj(tmp, f)
            manager.finish_round(member, round, session=session)
    except task.TaskError as e:
        _logger.error(str(e))
        raise HTTPException(400, str(e))
