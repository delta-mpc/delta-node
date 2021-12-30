from fastapi import APIRouter

from . import task

__all__ = ["router"]

router = APIRouter()
router.include_router(task.router)
