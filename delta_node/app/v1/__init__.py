from fastapi import APIRouter

from . import node, task

__all__ = ["router"]

router = APIRouter()
router.include_router(node.router)
router.include_router(task.router)
