from fastapi import APIRouter

from . import task, coord

__all__ = ["router"]

router = APIRouter()
router.include_router(task.router)
router.include_router(coord.router)
