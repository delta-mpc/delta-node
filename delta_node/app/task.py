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
