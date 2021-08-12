from io import BytesIO
import json
import logging
from base64 import b64decode, b64encode
from typing import List, Optional
from tempfile import TemporaryFile

import numpy as np

from .. import utils
from ..channel import ChannelGroup, InnerChannel, Message
from ..crypto import ecdhe
from . import base

_logger = logging.getLogger(__name__)


class Aggregator(base.Aggregator):
    def __init__(self, task_id: int, timeout: Optional[float] = None) -> None:
        super().__init__(task_id, timeout)

    def aggregate(self, member_ids: List[str], group: ChannelGroup) -> np.ndarray:
        accept_members = group.wait(member_ids, self._timeout)
        assert len(accept_members) == len(member_ids)
        _logger.debug("all member registered")

        pk_msgs = group.recv_msgs(member_ids, self._timeout)
        assert len(pk_msgs) == len(member_ids)
        assert all(msg.type == "text" for msg in pk_msgs.values())
        _logger.debug("recv pk msgs")

        pks = {
            member_id: msg.content.decode("utf-8") for member_id, msg in pk_msgs.items()
        }
        for member_id, pk in pks.items():
            _logger.info(
                f"task {self._task_id} recv member {member_id} public key: {pk}",
                extra={"task_id": self._task_id},
            )
        pks_str = json.dumps(pks)
        pks_msgs = {
            member_id: Message("json", pks_str.encode("utf-8"))
            for member_id in member_ids
        }
        group.send_msgs(pks_msgs)
        _logger.info(
            f"task {self._task_id} broadcast public key",
            extra={"task_id": self._task_id},
        )

        result_files = {member_id: TemporaryFile("w+b") for member_id in member_ids}

        finish_map = group.recv_files(result_files, self._timeout)
        assert len(finish_map) == len(member_ids)
        assert all(finish_map.values())
        _logger.debug("recv result files")
        _logger.info(
            f"task {self._task_id} recv result from {member_ids}",
            extra={"task_id": self._task_id},
        )

        result_arr = None
        for file in result_files.values():
            file.seek(0)
            arr = utils.load_arr(file)
            if result_arr is None:
                result_arr = arr
            else:
                result_arr += arr
        assert result_arr is not None

        group.close()
        _logger.info(
            f"task {self._task_id} result aggregation completed",
            extra={"task_id": self._task_id},
        )
        return result_arr


class Uploader(base.Uploader):
    def __init__(
        self, node_id: str, task_id: int, timeout: Optional[float] = None
    ) -> None:
        super().__init__(node_id, task_id, timeout)

    def callback(self, ch: InnerChannel):
        assert self._result_arr is not None
        curve = ecdhe.CURVES["secp256r1"]
        sk_bytes, pk_bytes = ecdhe.generate_key_pair(curve)
        pk_msg = Message(type="text", content=b64encode(pk_bytes))
        ch.send(pk_msg)
        _logger.info(
            f"task {self._task_id} send public key {pk_msg.content}",
            extra={"task_id": self._task_id},
        )

        peer_pk_msg = ch.recv(timeout=self._timeout)
        assert peer_pk_msg.type == "json"
        raw_peer_pks = json.loads(peer_pk_msg.content)
        peer_pks = {
            member_id: b64decode(raw_pk) for member_id, raw_pk in raw_peer_pks.items()
        }
        assert self._node_id in peer_pks
        assert peer_pks.pop(self._node_id) == pk_bytes
        _logger.info(
            f"task {self._task_id} recv peer public keys {peer_pks}",
            extra={"task_id": self._task_id},
        )

        for member_id, peer_pk in peer_pks.items():
            key = ecdhe.generate_shared_key(sk_bytes, peer_pk, curve)
            mask = utils.make_mask(key, self._result_arr.shape)
            if member_id < self._node_id:
                mask = -mask
            self._result_arr += mask

        with BytesIO() as f:
            utils.dump_arr(f, self._result_arr)
            f.seek(0)
            ch.send_file(f)
        _logger.info(
            f"task {self._task_id} upload result", extra={"task_id": self._task_id}
        )
        ch.close()
        self._result_arr = None
