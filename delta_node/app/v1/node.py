from typing import List

from delta_node import contract
from delta_node.app import utils
from fastapi import APIRouter

router = APIRouter()


@router.get("/nodes", response_model=utils.NodesResp)
def get_nodes(page: int = 1, page_size: int = 20):
    resp = contract.get_nodes(page, page_size)
    node_list = [utils.Node(id=node.id, url=node.url, name=node.name) for node in resp.nodes]
    res = utils.NodesResp(nodes=node_list, total_pages=resp.total_pages)
    return res
