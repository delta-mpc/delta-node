from pydantic import BaseModel
from enum import Enum

from typing import List


class CreateTaskResp(BaseModel):
    task_id: int


class Node(BaseModel):
    id: str
    url: str


class Task(BaseModel):
    id: int
    name: str
    type: str
    creator: str
    status: str
    created_at: int


class TasksResp(BaseModel):
    tasks: List[Task]
    total_pages: int


class TaskLog(BaseModel):
    created_at: int
    message: str