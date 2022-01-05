import math
from typing import List

from delta_node import chain
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class Node(BaseModel):
    id: str
    url: str
    name: str


class NodesPage(BaseModel):
    nodes: List[Node]
    total_pages: int


@router.get("/nodes", response_model=NodesPage)
async def get_nodes(page: int = Query(..., ge=1), page_size: int = Query(20, gt=0)):
    nodes, total_count = await chain.get_client().get_nodes(
        page=page, page_size=page_size
    )
    total_pages = math.ceil(total_count / page_size)
    return NodesPage(
        nodes=[Node(id=node.address, url=node.url, name=node.name) for node in nodes],
        total_pages=total_pages,
    )
