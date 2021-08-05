import json
import logging
import shutil
from io import BytesIO
from functools import partial

import numpy as np

from delta_node import channel, commu, config, db, node, agg

_logger = logging.getLogger(__name__)

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
    with open(f"{node_id}.cfg", mode="wb") as f:
        client.get_file(1, node_id, 0, "cfg", f)
    print("get cfg")
    for _ in range(10):
        round_id = client.get_round_id(1, node_id)
        print(f"round {round_id}")
        with open(f"{node_id}.weight", mode="wb") as f:
            client.get_file(1, node_id, round_id - 1, "weight", f)
        upload_method = agg.get_upload_method(0)
        result_arr = np.random.rand(100)
        client.upload_result(1, node_id, round_id, partial(upload_method, result_arr=result_arr))
        print("upload result")


if __name__ == "__main__":
    main()
