import json
import logging
import shutil
from io import BytesIO

import numpy as np

from delta_node import channel, commu, config, db, node

_logger = logging.getLogger(__name__)


def result_callback(ch: channel.InnerChannel):
    pk_msg = channel.Message(type="text", content=b"1")
    ch.send(pk_msg)
    _logger.info("send pk msg")

    pks_msg = ch.recv()
    _logger.info("recv pk msgs")
    assert pks_msg.type == "json"
    pks = json.loads(pks_msg.content)
    assert pks["2"] == "1"

    arr = np.random.rand(100)
    with BytesIO() as f:
        np.savez(f, arr)
        f.seek(0)
        _logger.info("generate result array")
        while True:
            content = f.read(config.MAX_BUFF_SIZE)
            msg = channel.Message(type="file", content=content)
            ch.send(msg)
            _logger.info("send file content")
            if len(content) == 0:
                break
    ch.close()


def main():
    logging.basicConfig(level=logging.INFO)
    db.init_db()
    node.register_node()

    node_id = node.get_node_id()
    client = commu.CommuClient("127.0.0.1:6800")
    client.join_task(1, node_id)
    print("join task")
    metadata = client.get_metadata(1, node_id)
    print(metadata)
    cfg_file = client.get_file(1, node_id, 0, "cfg")
    with open(f"{node_id}.cfg", mode="wb") as f:
        shutil.copyfileobj(cfg_file, f)
    print("get cfg")
    for _ in range(10):
        round_id = client.get_round_id(1, node_id)
        print(f"round {round_id}")
        weight_file = client.get_file(1, node_id, round_id - 1, "weight")
        with open(f"{node_id}.weight", mode="wb") as f:
            shutil.copyfileobj(weight_file, f)
        client.upload_result(1, node_id, round_id, result_callback)
        print("upload result")


if __name__ == "__main__":
    main()
