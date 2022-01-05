import logging
from typing import IO, Dict, List

import httpx
from delta_node import entity, serialize

_logger = logging.getLogger(__name__)


class Client(object):
    def __init__(
        self, url: str, client: httpx.Client, aclient: httpx.AsyncClient
    ) -> None:
        self.base_url = url + "/v1/coord"
        self.client = client
        self.aclient = aclient

    def download_task_config(self, task_id: str, dst: IO[bytes]):
        params = {"task_id": task_id}
        with self.client.stream("GET", self.base_url + "/config", params=params) as resp:
            size = 0
            for chunk in resp.iter_bytes():
                dst.write(chunk)
                size += len(chunk)

    async def upload_secret_shares(
        self,
        node_address: str,
        task_id: str,
        round: int,
        shares: List[entity.SecretShareData],
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

        resp = await self.aclient.post(self.base_url + "/secret_shares", json=data)
        resp.raise_for_status()

    async def get_secret_shares(
        self, node_address: str, task_id: str, round: int
    ) -> List[entity.SecretShareData]:
        data = {"address": node_address, "task_id": task_id, "round": round}

        resp = await self.aclient.get(self.base_url + "/secret_shares", params=data)
        resp.raise_for_status()
        result = resp.json()

        ret = [
            entity.SecretShareData(
                sender=share["sender"],
                receiver=share["receiver"],
                seed=serialize.hex_to_bytes(share["seed_share"]),
                secret_key=serialize.hex_to_bytes(share["sk_share"]),
            )
            for share in result["shares"]
        ]
        return ret

    def download_task_weight(self, task_id: str, round: int, dst: IO[bytes]):
        params = {"task_id": task_id, "round": round}
        with self.client.stream(
            "GET", self.base_url + "/weight", params=params
        ) as resp:
            for chunk in resp.iter_bytes():
                dst.write(chunk)

    def upload_task_round_result(
        self, address: str, task_id: str, round: int, src: IO[bytes]
    ):
        files = {"file": src}
        data = {"address": address, "task_id": task_id, "round": round}
        resp = self.client.post(self.base_url + "/result", data=data, files=files)
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
        resp = self.client.post(self.base_url + "/metrics", json=data)
        resp.raise_for_status()
