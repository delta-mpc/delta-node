from typing import List

from delta_node import contract
from delta_node.app import utils
from fastapi import APIRouter

router = APIRouter()


@router.get("/nodes", response_model=List[utils.Node])
def get_nodes(page: int = 1, page_size: int = 20):
    nodes = contract.get_nodes(page, page_size)
    res = [utils.Node(id=node.id, url=node.url) for node in nodes]
    return res
