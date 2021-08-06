import json
import logging
import shutil
from contextlib import contextmanager
from tempfile import TemporaryFile
from typing import Dict
from zipfile import ZipFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import db, manager
from . import utils

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task")


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
            manager.create_task(metadata, cfg_file, weight_file, session=session)
            cfg_file.close()
            weight_file.close()

    resp = utils.CommonResp(
        status=utils.RespStatus.SUCCESS,
    )
    return resp
