import json
import logging
from zipfile import ZipFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import utils
from .. import db, task

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task")


@router.post("", response_model=utils.CommonResp)
def upload_task(
    file: UploadFile = File(...), session: Session = Depends(db.get_session)
):
    with ZipFile(file.file, mode="r") as zip_f:
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
        task.create_task(metadata, cfg_file, weight_file, session)
        cfg_file.close()
        weight_file.close()

    resp = utils.CommonResp(
        status=utils.RespStatus.SUCCESS,
    )
    return resp
