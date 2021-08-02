from delta_node.channel.msg import Message
from typing import List, Optional
from ..channel import ChannelGroup
import json
from .utils import load_arr, add_arrs


def aggregate(
    member_ids: List[str], group: ChannelGroup, timeout: Optional[float] = None
):
    accept_members = group.wait(member_ids, timeout)
    assert len(accept_members) == len(member_ids)

    init_msgs = group.recv_msgs(member_ids, timeout)
    assert len(init_msgs) == len(member_ids)
    assert all(msg.type == "init" for msg in init_msgs.values())

    pk_msgs = group.recv_msgs(member_ids, timeout)
    assert len(pk_msgs) == len(member_ids)
    assert all(msg.type == "text" for msg in pk_msgs.values())

    pks = {member_id: msg.content.decode("utf-8") for member_id, msg in pk_msgs.items()}
    pks_str = json.dumps(pks)
    pks_msgs = {
        member_id: Message("json", pks_str.encode("utf-8")) for member_id in member_ids
    }
    group.send_msgs(pks_msgs)

    result_files = group.recv_files(member_ids, timeout)
    assert len(result_files) == len(member_ids)

    arrs = [load_arr(file) for file in result_files.values()]
    result_arr = add_arrs(arrs)
    return result_arr
