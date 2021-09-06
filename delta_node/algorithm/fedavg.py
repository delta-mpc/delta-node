import json
import logging
from io import BytesIO
from tempfile import TemporaryFile

import numpy as np

from .. import serialize, utils
from ..channel import ChannelGroup, InnerChannel, Message
from ..crypto import ecdhe
from .base import Algorithm

_logger = logging.getLogger(__name__)


class FedAvg(Algorithm):
    @property
    def name(self) -> str:
        return "FedAvg"

    def aggregate(self, member_ids: List[str], group: ChannelGroup, **kwargs) -> np.ndarray:
        try:
            accept_members = group.wait(member_ids, self._timeout)
            assert len(accept_members) == len(member_ids)
            _logger.debug("all member registered")

            precision: int = kwargs.get("precision", 8)
            assert isinstance(precision, int), "precision should be a int"
            curve: str = kwargs.get("curve", "secp256r1")
            assert isinstance(curve, str), "curve should be a string"
            assert curve in ecdhe.CURVES, f"{curve} is not a valid ecdhe curve name"

            cfg = {"precision": precision, "curve": curve}
            cfg_bytes = json.dumps(cfg).encode("utf-8")
            cfg_msgs = {
                member_id: Message("json", cfg_bytes) for member_id in member_ids
            }
            group.send_msgs(cfg_msgs)

            pk_msgs = group.recv_msgs(member_ids, self._timeout)
            assert len(pk_msgs) == len(member_ids)
            assert all(msg.type == "text" for msg in pk_msgs.values())
            _logger.debug("recv pk msgs")

            pks = {
                member_id: msg.content.decode("utf-8")
                for member_id, msg in pk_msgs.items()
            }
            for member_id, pk in pks.items():
                _logger.info(
                    f"task {self._task_id} recv member {member_id} public key: {pk}",
                    extra={"task_id": self._task_id},
                )
            pks_bytes = json.dumps(pks).encode("utf-8")
            pks_msgs = {
                member_id: Message("json", pks_bytes) for member_id in member_ids
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
            _logger.debug("recv agg files")
            _logger.info(
                f"task {self._task_id} recv result from {member_ids}",
                extra={"task_id": self._task_id},
            )

            result_arr = None
            for file in result_files.values():
                file.seek(0)
                arr = serialize.load_arr(file)
                if result_arr is None:
                    result_arr = arr
                else:
                    result_arr += arr
            assert result_arr is not None
            result_arr = utils.unfix_precision(result_arr, precision)
            result_arr /= len(member_ids)
            _logger.debug(f"result arr {result_arr}")

            _logger.info(
                f"task {self._task_id} aggregation completed",
                extra={"task_id": self._task_id},
            )
            return result_arr
        except Exception as e:
            _logger.exception(e)
            raise
        finally:
            group.close()

    def upload(self, node_id: str, result: np.ndarray, ch: InnerChannel):
        try:
            assert result is not None

            cfg_msg = ch.recv(timeout=self._timeout)
            assert cfg_msg.type == "json"
            cfg = json.loads(cfg_msg.content)
            assert "precision" in cfg
            assert "curve" in cfg
            precision = cfg["precision"]
            curve_name = cfg["curve"]
            assert isinstance(precision, int)
            assert isinstance(curve_name, str)
            assert curve_name in ecdhe.CURVES
            _logger.debug(f"result arr {result}")
            result_arr = utils.fix_precision(result, precision)

            curve = ecdhe.CURVES[curve_name]
            sk_bytes, pk_bytes = ecdhe.generate_key_pair(curve)
            pk_msg = Message(
                type="text", content=serialize.key_to_str(pk_bytes).encode("utf-8")
            )
            ch.send(pk_msg)
            _logger.info(
                f"task {self._task_id} send public key {pk_msg.content}",
                extra={"task_id": self._task_id},
            )

            peer_pk_msg = ch.recv(timeout=self._timeout)
            assert peer_pk_msg.type == "json"
            raw_peer_pks = json.loads(peer_pk_msg.content)
            peer_pks = {
                member_id: serialize.str_to_key(raw_pk)
                for member_id, raw_pk in raw_peer_pks.items()
            }
            assert node_id in peer_pks
            assert peer_pks.pop(node_id) == pk_bytes
            _logger.info(
                f"task {self._task_id} recv peer public keys {peer_pks}",
                extra={"task_id": self._task_id},
            )

            for member_id, peer_pk in peer_pks.items():
                key = ecdhe.generate_shared_key(sk_bytes, peer_pk, curve)
                mask = utils.make_mask(key, result_arr.shape)
                if member_id < node_id:
                    mask = -mask
                result_arr += mask

            with BytesIO() as f:
                serialize.dump_arr(f, result_arr)
                f.seek(0)
                ch.send_file(f)
            _logger.info(
                f"task {self._task_id} upload result", extra={"task_id": self._task_id}
            )
        except Exception as e:
            _logger.exception(e)
            raise
        finally:
            ch.close()

    def update(self, weight: np.ndarray, result: np.ndarray) -> np.ndarray:
        return result
