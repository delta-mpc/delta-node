from pydantic import BaseModel
from enum import Enum


class RespStatus(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"


class CommonResp(BaseModel):
    status: RespStatus
    msg: str = ""
