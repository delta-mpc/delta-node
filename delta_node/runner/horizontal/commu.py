from __future__ import annotations

from typing import IO, Dict, List

import httpx

from delta_node import config, entity, pool, serialize


class CommuClient(object):
    def __init__(self, url: str) -> None:
        if url == config.node_url:
            url = f"http://localhost:{config.api_port}"

        base_url = url + "/v1/coord/"
        self.client = httpx.Client(base_url=base_url)

    def download_task_config(self, task_id: str, dst: IO[bytes]):
        params = {"task_id": task_id}
        with self.client.stream("GET", "config", params=params) as resp:
            resp.raise_for_status()
            size = 0
            for chunk in resp.iter_bytes():
                dst.write(chunk)
                size += len(chunk)

    async def upload_secret_shares(
        self,
        node_address: str,
        task_id: str,
        round: int,
        shares: List[entity.horizontal.SecretShareData],
    ):
        data = {
            "address": node_address,
            "task_id": task_id,
            "round": round,
            "shares": [
                {
                    "sender": node_address,
                    "receiver": share.receiver,
                    "seed_share": serialize.bytes_to_hex(share.seed),
                    "sk_share": serialize.bytes_to_hex(share.secret_key),
                }
                for share in shares
            ],
        }

        def _call():
            resp = self.client.post("secret_shares", json=data)
            resp.raise_for_status()

        await pool.run_in_io(_call)

    async def get_secret_shares(
        self, node_address: str, task_id: str, round: int
    ) -> List[entity.horizontal.SecretShareData]:
        data = {"address": node_address, "task_id": task_id, "round": round}

        def _call():
            resp = self.client.get("secret_shares", params=data)
            resp.raise_for_status()
            result = resp.json()
            return result

        result = await pool.run_in_io(_call)

        ret = [
            entity.horizontal.SecretShareData(
                sender=share["sender"],
                receiver=share["receiver"],
                seed=serialize.hex_to_bytes(share["seed_share"]),
                secret_key=serialize.hex_to_bytes(share["sk_share"]),
            )
            for share in result["shares"]
        ]
        return ret

    def download_task_context(self, task_id: str, var_name: str, dst: IO[bytes]):
        params = {"task_id": task_id, "name": var_name}
        with self.client.stream("GET", "context", params=params) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_bytes():
                dst.write(chunk)

    def download_task_weight(self, task_id: str, round: int, dst: IO[bytes]):
        params = {"task_id": task_id, "round": round}
        with self.client.stream("GET", "weight", params=params) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_bytes():
                dst.write(chunk)

    def upload_task_round_result(
        self, address: str, task_id: str, round: int, src: IO[bytes]
    ):
        files = {"file": ("round_result.pkl", src, "application/octet-stream")}
        data = {"address": address, "task_id": task_id, "round": round}
        resp = self.client.post("result", data=data, files=files, timeout=None)
        resp.raise_for_status()

    def upload_task_round_metrics(
        self, address: str, task_id: str, round: int, metrics: Dict[str, int]
    ):
        data = {
            "address": address,
            "task_id": task_id,
            "round": round,
            "metrics": metrics,
        }
        resp = self.client.post("metrics", json=data)
        resp.raise_for_status()

    def close(self):
        self.client.close()
