import json
import logging
import random
from collections import defaultdict
from io import BytesIO
from tempfile import TemporaryFile
from typing import Dict, List, Optional

import numpy as np

from .. import serialize, utils
from ..channel import ChannelGroup, InnerChannel, Message
from ..crypto import aes, ecdhe, shamir
from .base import Algorithm

_logger = logging.getLogger(__name__)


class FaultTolerantFedAvg(Algorithm):
    @property
    def name(self) -> str:
        return "FaultTolerantFedAvg"

    def aggregate(self, member_ids: List[str], group: ChannelGroup, **kwargs) -> np.ndarray:
        try:
            u0_list = group.wait(member_ids, timeout=self._timeout)
            _logger.debug(f"members {u0_list} regsiteded")

            precision: int = kwargs.get("precision", 8)
            assert isinstance(precision, int), "precision should be a int"
            curve_name: str = kwargs.get("curve", "secp256r1")
            assert isinstance(curve_name, str), "curve should be a string"
            assert curve_name in ecdhe.CURVES, f"{curve_name} is not a valid ecdhe curve name"
            curve = ecdhe.CURVES[curve_name]

            threshold: int = kwargs.get("threshold", 2)
            assert isinstance(threshold, int)
            secret_share = shamir.SecretShare(threshold)

            cfg = {
                "precision": precision,
                "curve": curve_name,
                "threshold": threshold,
            }
            cfg_bytes = json.dumps(cfg).encode("utf-8")
            cfg_msgs = {u: Message("json", cfg_bytes) for u in u0_list}
            _logger.debug("send cfg msgs to members")
            group.send_msgs(cfg_msgs)

            pk_msgs = group.recv_msgs(u0_list, timeout=self._timeout)
            u1_list = list(pk_msgs.keys())
            assert set(u1_list) & set(u0_list) == set(u1_list)
            _logger.debug(f"recv public keys from members: {u1_list}")

            s_pks = {}
            all_pks = {}
            for u, msg in pk_msgs.items():
                assert msg.type == "json"
                pks: Dict[str, str] = json.loads(msg.content)
                _logger.debug(f"member {u} public key {pks}")
                all_pks[u] = pks
                s_pk = serialize.str_to_key(pks["s_pk"])
                s_pks[u] = s_pk

            all_pks_msg = Message("json", json.dumps(all_pks).encode("utf-8"))
            all_pks_msgs = {u: all_pks_msg for u in u1_list}
            group.send_msgs(all_pks_msgs)
            _logger.debug("broadcast public keys to members")

            share_msgs = group.recv_msgs(u1_list, timeout=self._timeout)
            u2_list = list(share_msgs.keys())
            assert set(u2_list) & set(u1_list) == set(u2_list)
            _logger.debug(f"recv shares from members {u2_list}")

            all_shares = defaultdict(dict)
            for u, msg in share_msgs.items():
                assert msg.type == "json"
                shares = json.loads(msg.content)
                for v, share_content in shares.items():
                    if v in u2_list:
                        _logger.debug(f"member {u} send {v} share {share_content}")
                        all_shares[v].update({u: share_content})
            all_shares_msgs = {
                u: Message("json", json.dumps(share).encode("utf-8"))
                for u, share in all_shares.items()
            }
            group.send_msgs(all_shares_msgs)
            _logger.debug("broadcast shares to members")

            arr_files = {u: TemporaryFile(mode="w+b") for u in u2_list}
            status = group.recv_files(arr_files, timeout=self._timeout)
            u3_list = [u for u, finished in status.items() if finished]
            assert set(u3_list) & set(u2_list) == set(u3_list)
            _logger.debug(f"recv mask arrays from {u3_list}")
            for u, finished in status.items():
                if not finished:
                    file = arr_files.pop(u)
                    file.close()

            mask_arr = None
            for u, file in arr_files.items():
                file.seek(0)
                arr = serialize.load_arr(file)
                _logger.debug(f"member {u} mask array: {arr}")
                if mask_arr is None:
                    mask_arr = arr
                else:
                    mask_arr += arr
            assert mask_arr is not None

            users_msg = Message("json", json.dumps(u3_list).encode("utf-8"))
            users_msgs = {u: users_msg for u in u3_list}
            group.send_msgs(users_msgs)
            _logger.debug(f"broadcast user list {u3_list}")

            resolve_share_msgs = group.recv_msgs(u3_list, timeout=self._timeout)
            u4_list = list(resolve_share_msgs.keys())
            assert set(u4_list) & set(u3_list) == set(u4_list)
            assert len(u4_list) >= threshold
            _logger.debug(f"recv shares from {u4_list}")

            resolve_shares = defaultdict(list)
            for u, msg in resolve_share_msgs.items():
                assert msg.type == "json"
                shares = json.loads(msg.content)
                for v, share_content in shares.items():
                    resolve_shares[v].append(share_content)

            bus = {}
            sks = {}
            for u, shares in resolve_shares.items():
                _logger.debug(f"member {u} shares {shares}")
                if len(shares) > 0:
                    val = secret_share.resolve_shares(shares)
                    if u in u3_list:
                        _logger.debug(f"member {u} bu {val}")
                        bus[u] = val
                    else:
                        _logger.debug(f"member {u} sk {val}")
                        sks[u] = val

            bu_mask = np.zeros(mask_arr.shape, dtype=np.int64)
            for u, bu in bus.items():
                mask = utils.make_mask(bu, mask_arr.shape)
                bu_mask += mask

            ck_mask = np.zeros(mask_arr.shape, dtype=np.int64)
            for u in u3_list:
                pk = s_pks[u]
                for v, sk in sks.items():
                    sk = serialize.int_to_bytes(sk)
                    ck = ecdhe.generate_shared_key(sk, pk, curve)
                    mask = utils.make_mask(serialize.bytes_to_int(ck), mask_arr.shape)
                    if u < v:
                        mask = -mask
                    ck_mask += mask

            result_arr = mask_arr - bu_mask + ck_mask
            result_arr = utils.unfix_precision(result_arr, precision)
            result_arr /= len(u3_list)
            _logger.debug(f"result array {result_arr}")
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
            _logger.debug(f"recv cfg msg {cfg_msg}")
            assert cfg_msg.type == "json"
            cfg = json.loads(cfg_msg.content)
            assert "precision" in cfg
            assert "curve" in cfg
            assert "threshold" in cfg
            precision = cfg["precision"]
            curve_name = cfg["curve"]
            threshold = cfg["threshold"]
            assert isinstance(precision, int)
            assert isinstance(curve_name, str)
            assert curve_name in ecdhe.CURVES
            assert isinstance(threshold, int)

            curve = ecdhe.CURVES[curve_name]
            _logger.debug(f"result arr {result}")
            result_arr = utils.fix_precision(result, precision)
            secret_share = shamir.SecretShare(threshold)

            c_sk, c_pk = ecdhe.generate_key_pair(curve)
            _logger.debug(f"c_sk {c_sk} c_pk {c_pk}")
            s_sk, s_pk = ecdhe.generate_key_pair(curve)
            _logger.debug(f"s_sk {s_sk} s_pk {s_pk}")

            pks = {
                "c_pk": serialize.key_to_str(c_pk),
                "s_pk": serialize.key_to_str(s_pk),
            }
            pks_msg = Message("json", json.dumps(pks).encode("utf-8"))
            ch.send(pks_msg)
            _logger.debug("send public keys to server")

            all_pks_msg = ch.recv(self._timeout)
            assert all_pks_msg.type == "json"
            all_pks = json.loads(all_pks_msg.content)
            u1_list = list(all_pks.keys())
            _logger.debug(f"recv public keys from {u1_list}")

            enc_keys = {}
            mask_keys = {}
            for u, pks in all_pks.items():
                c_pk = serialize.str_to_key(pks["c_pk"])
                s_pk = serialize.str_to_key(pks["s_pk"])
                _logger.debug(f"member {u} c_pk {c_pk} s_pk {s_pk}")
                enc_keys[u] = ecdhe.generate_shared_key(c_sk, c_pk, curve)
                if u != node_id:
                    mask_keys[u] = ecdhe.generate_shared_key(s_sk, s_pk, curve)

            bu = random.randint(1, shamir.PRIME - 1)
            _logger.debug(f"bu {bu}")
            bu_shares = secret_share.make_shares(bu, len(u1_list))
            s_sk_shares = secret_share.make_shares(
                serialize.bytes_to_int(s_sk), len(u1_list)
            )

            remote_shares_dict = {}
            local_shares_dict = {}
            for u, bu_share, s_sk_share in zip(u1_list, bu_shares, s_sk_shares):
                data = {
                    "bu": list(bu_share),
                    "sk": list(s_sk_share),
                }
                _logger.debug(f"share to {u} {data}")
                key = enc_keys[u]
                enc_data = aes.encrypt(key, json.dumps(data).encode("utf-8"))
                remote_shares_dict[u] = enc_data.decode("utf-8")

                if u == node_id:
                    local_shares_dict[u] = data

            remote_shares_msg = Message(
                "json", json.dumps(remote_shares_dict).encode("utf-8")
            )
            ch.send(remote_shares_msg)
            _logger.debug("send shares to server")

            all_shares_msg = ch.recv(self._timeout)
            assert all_shares_msg.type == "json"

            enc_shares = json.loads(all_shares_msg.content)
            u2_list = list(enc_shares.keys())
            assert set(u2_list) & set(u1_list) == set(u2_list)
            _logger.debug(f"recv shares from {u2_list}")

            for u, enc_share in enc_shares.items():
                if u != node_id:
                    key = enc_keys[u]
                    share_str = aes.decrypt(key, enc_share.encode("utf-8")).decode(
                        "utf-8"
                    )
                    share = json.loads(share_str)
                    local_shares_dict[u] = share
                    _logger.debug(f"recv share from {u} {share}")

            bu_mask = utils.make_mask(bu, result_arr.shape)
            ck_mask = np.zeros(result_arr.shape, dtype=np.int32)

            for u, mask_key in mask_keys.items():
                if u != node_id:
                    mask = utils.make_mask(mask_key, result_arr.shape)
                    if u < node_id:
                        mask = -mask
                    ck_mask += mask

            _logger.debug(f"bu mask {bu_mask}")
            _logger.debug(f"ck mask {ck_mask}")
            mask_arr = result_arr + bu_mask + ck_mask
            _logger.debug(f"mask array {mask_arr}")

            with BytesIO() as f:
                serialize.dump_arr(f, mask_arr)
                f.seek(0)
                ch.send_file(f)
                _logger.debug("send result arr to server")

            users_msg = ch.recv(self._timeout)
            assert users_msg.type == "json"
            u3_list = json.loads(users_msg.content)
            _logger.debug(f"u2_list: {u2_list}")
            _logger.debug(f"u3_list: {u3_list}")
            assert set(u3_list) & set(u2_list) == set(u3_list)
            _logger.debug(f"recv alive members from server {u3_list}")

            resolve_shares = {}
            for u in u2_list:
                if u in u3_list:
                    share = local_shares_dict[u]["bu"]
                    _logger.debug(f"member {u} bu share {share}")
                else:
                    share = local_shares_dict[u]["sk"]
                    _logger.debug(f"member {u} sk share {share}")
                resolve_shares[u] = share
            resolve_share_msg = Message(
                "json", json.dumps(resolve_shares).encode("utf-8")
            )
            ch.send(resolve_share_msg)
            _logger.debug("send resolve share msg to server")
            ch.close()
        except Exception as e:
            _logger.exception(e)
            raise
        finally:
            ch.close()

    def update(self, weight: np.ndarray, result: np.ndarray) -> np.ndarray:
        return result
