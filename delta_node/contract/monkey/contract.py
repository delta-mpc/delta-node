from typing import Dict, Any

import requests

from ... import config

__all__ = ["register_node", "create_task", "join_task", "start_round", "publish_pub_key"]


def call_tx_func(func_name: str, data: Dict[str, Any]):
    url = config.contract_address + "/" + func_name
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()


def register_node(url: str) -> str:
    """
    register this node in contract
    :param url: node url
    :return: node id
    """
    data = {"url": url}
    resp_data = call_tx_func("node", data)
    return resp_data["id"]


def create_task(node_id: str, task_name: str) -> int:
    """
    create task
    :param node_id: self node id
    :param task_name: task name
    :return: task id
    """
    data = {"creator": node_id, "name": task_name}
    resp_data = call_tx_func("task", data)

    return resp_data["id"]


def join_task(node_id: str, task_id: int) -> bool:
    """
    join this task
    :param node_id: self node id
    :param task_id: id of task to be joined
    :return:
    """
    data = {"node_id": node_id, "task_id": task_id}
    resp_data = call_tx_func("task_member", data)
    return resp_data["status"] == "ok"


def start_round(node_id: str, task_id: int) -> int:
    """
    start a training round of the task
    :param node_id: self node id, should be creator of the task
    :param task_id: task id
    :return: round id
    """
    data = {"node_id": node_id, "task_id": task_id}
    resp_data = call_tx_func("round", data)
    return resp_data["round_id"]


def publish_pub_key(node_id: str, task_id: int, round_id: int, pub_key: str) -> bool:
    """
    publish public key to the contract which used for secure aggregation in this round
    :param node_id: self node id
    :param task_id: task id
    :param round_id: round id
    :param pub_key: public key
    :return:
    """
    data = {"node_id": node_id, "task_id": task_id, "round_id": round_id, "pub_key": pub_key}
    resp_data = call_tx_func("pub_key", data)
    return resp_data["status"] == "ok"
