from typing import List

from fastapi import APIRouter

from .. import contract
from . import utils

router = APIRouter()


@router.get("/nodes", response_model=List[utils.Node])
def get_nodes(page: int = 1, page_size: int = 20):
    nodes = contract.get_nodes(page, page_size)
    res = [utils.Node(id=node.id, url=node.url) for node in nodes]
    return res
