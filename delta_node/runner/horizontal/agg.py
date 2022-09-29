from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager
from tempfile import TemporaryFile
from typing import Dict, List, Tuple

import numpy as np
from delta.core.strategy import Strategy
from delta.core.task import AggResultType
from delta_node import entity, pool, serialize, utils
from delta_node.chain import horizontal as chain
from delta_node.crypto import aes, ecdhe, shamir
from delta_node.runner.event_box import EventBox

from .commu import CommuClient
from .context import ClientTaskContext

_logger = logging.getLogger(__name__)


class NotSelected(Exception):
    def __init__(self, node_address: str, task_id: str, round: int) -> None:
        self.node_address = node_address
        self.task_id = task_id
        self.round = round

    def __str__(self) -> str:
        return f"{self.node_address} has not been selected in task {self.task_id} round {self.round}"


class ClientAggregator(object):
    def __init__(
        self,
        node_address: str,
        task_id: str,
        round: int,
        strategy: Strategy,
        agg_vars: List[str],
        event_box: EventBox,
        client: CommuClient,
    ) -> None:
        self.node_address = node_address
        self.task_id = task_id
        self.round = round
        self.strategy = strategy
        self.agg_vars = agg_vars
        self.event_box = event_box
        self.client = client

        self.curve = ecdhe.CURVES[self.strategy.curve]

    @asynccontextmanager
    async def aggregate(self, ctx: ClientTaskContext):
        sk1, sk2 = await self.join_round()

        u1 = await self.wait_partner_selected()
        pk1s, pk2s = await self.get_public_keys(u1)
        commu_keys = self.calc_commu_keys(sk1, pk1s)
        seed = secrets.token_bytes(32)
        await self.upload_secret_shares(u1, seed, sk2, commu_keys)

        u2 = await self.wait_calculation_started()
        seed_shares, sk_shares = await self.get_secret_shares(u2, commu_keys)

        yield

        unmask_result = {}
        for var_name in self.agg_vars:
            unmask_result[var_name] = ctx.get_agg_result(var_name)
        await self.upload_result(u2, seed, sk2, pk2s, unmask_result)

        u3 = await self.wait_aggregation_started()
        alive_members = u3
        dead_members = list(set(u2) - set(u3))
        await self.upload_alive_seed_shares(alive_members, seed_shares)
        await self.upload_dead_sk_shares(dead_members, sk_shares)

    async def join_round(self):
        sk1, pk1 = ecdhe.generate_key_pair(curve=self.curve)
        sk2, pk2 = ecdhe.generate_key_pair(curve=self.curve)

        tx_hash = await chain.get_client().join_round(
            self.node_address, self.task_id, self.round, pk1, pk2
        )

        _logger.info(
            f"[Join the training round] try to join in task {self.task_id} round {self.round}",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        return sk1, sk2

    async def wait_partner_selected(self) -> List[str]:
        event = await self.event_box.wait_for_event(
            "partner_selected", self.strategy.wait_timeout * 2
        )
        assert isinstance(event, entity.PartnerSelectedEvent)
        assert event.task_id == self.task_id
        assert event.round == self.round
        if self.node_address not in event.addrs:
            raise NotSelected(self.node_address, self.task_id, self.round)
        _logger.info(
            f"join in task {self.task_id} round {self.round}",
            extra={"task_id": self.task_id},
        )
        return event.addrs

    async def get_public_keys(
        self, u1: List[str]
    ) -> Tuple[Dict[str, bytes], Dict[str, bytes]]:
        pks = await chain.get_client().get_client_public_keys(
            self.task_id, self.round, u1
        )
        pk1s, pk2s = zip(*pks)

        pk1_dict = {}
        pk2_dict = {}

        for addr, pk1, pk2 in zip(u1, pk1s, pk2s):
            pk1_dict[addr] = pk1
            pk2_dict[addr] = pk2

        return pk1_dict, pk2_dict

    def calc_commu_keys(self, sk1: bytes, pk1s: Dict[str, bytes]) -> Dict[str, bytes]:
        res = {}
        for addr, pk1 in pk1s.items():
            key = ecdhe.generate_shared_key(sk1, pk1, curve=self.curve)
            res[addr] = key
            _logger.debug(
                f"{self.node_address[:8]} -> {addr[:8]} share key {serialize.bytes_to_hex(key)[:8]}"
            )
        _logger.debug("generate shared keys for communication")
        return res

    async def upload_secret_shares(
        self, u1: List[str], seed: bytes, sk2: bytes, commu_keys: Dict[str, bytes]
    ):
        _logger.debug(f"{self.node_address} seed {serialize.bytes_to_hex(seed)}")

        ss = shamir.SecretShare(self.strategy.select_strategy.min_clients)

        seed_shares = ss.make_shares(seed, len(u1))
        _logger.debug(
            f"{self.node_address} seed shares {[serialize.bytes_to_hex(share) for share in seed_shares]}"
        )
        for receiver, share in zip(u1, seed_shares):
            _logger.debug(
                f"{self.node_address[:8]} -> {receiver[:8]} seed share {serialize.bytes_to_hex(share)[:8]}"
            )
        _logger.debug("make seed shares")
        sk_shares = ss.make_shares(sk2, len(u1))
        for receiver, share in zip(u1, sk_shares):
            _logger.debug(
                f"{self.node_address[:8]} -> {receiver[:8]} sk share {serialize.bytes_to_hex(share)[:8]}"
            )
        _logger.debug("make sk shares")

        seed_commitments = [utils.calc_commitment(share) for share in seed_shares]
        _logger.debug("generate seed share commitments")
        sk_commitments = [utils.calc_commitment(share) for share in sk_shares]
        _logger.debug("generate sk share commitments")

        tx_hash = await chain.get_client().upload_seed_commitment(
            self.node_address,
            self.task_id,
            self.round,
            u1,
            seed_commitments,
        )
        _logger.debug("upload seed share commitments")
        _logger.info(
            f"[Secret Sharing Parts Commitments] task {self.task_id} round {self.round} upload seed secret share commitments",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        tx_hash = await chain.get_client().upload_secret_key_commitment(
            self.node_address,
            self.task_id,
            self.round,
            u1,
            sk_commitments,
        )
        _logger.debug("upload sk share commitments")
        _logger.info(
            f"[Secret Sharing Parts Commitments] task {self.task_id} round {self.round} upload secret key secret share commitments",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

        ss_datas: List[entity.horizontal.SecretShareData] = []
        for u, seed_share, sk_share in zip(u1, seed_shares, sk_shares):
            enc_seed_share = aes.encrypt(commu_keys[u], seed_share)
            _logger.debug(
                f"{self.node_address[:8]} -> {u[:8]} enc seed share {serialize.bytes_to_hex(enc_seed_share)[:8]}"
            )
            enc_sk_share = aes.encrypt(commu_keys[u], sk_share)
            _logger.debug(
                f"{self.node_address[:8]} -> {u[:8]} enc sk share {serialize.bytes_to_hex(enc_sk_share)[:8]}"
            )
            ss_datas.append(
                entity.horizontal.SecretShareData(
                    sender=self.node_address,
                    receiver=u,
                    seed=enc_seed_share,
                    secret_key=enc_sk_share,
                )
            )

        await self.client.upload_secret_shares(
            self.node_address, self.task_id, self.round, ss_datas
        )
        _logger.debug("upload secret shares to coordinator")
        _logger.info(
            f"task {self.task_id} round {self.round} upload secret shares",
            extra={"task_id": self.task_id},
        )

    async def wait_calculation_started(self) -> List[str]:
        event = await self.event_box.wait_for_event(
            "calculation_started", self.strategy.wait_timeout * 2
        )
        assert isinstance(event, entity.CalculationStartedEvent)
        assert event.task_id == self.task_id
        assert event.round == self.round
        assert self.node_address in event.addrs
        return event.addrs

    async def get_secret_shares(
        self, u2: List[str], commu_keys: Dict[str, bytes]
    ) -> Tuple[Dict[str, bytes], Dict[str, bytes]]:
        # get and check secret shares
        ss_commitments = await chain.get_client().get_secret_share_datas(
            self.task_id, self.round, u2, self.node_address
        )
        _logger.debug("get secret shares")
        ss_datas = await self.client.get_secret_shares(
            self.node_address, self.task_id, self.round
        )
        _logger.debug("get secret share commitments")
        for data in ss_datas:
            _logger.debug(
                f"{data.sender[:8]} -> {data.receiver[:8]} enc seed share {serialize.bytes_to_hex(data.seed)[:8]}"
            )
            _logger.debug(
                f"{data.sender[:8]} -> {data.receiver[:8]} enc secret key share {serialize.bytes_to_hex(data.secret_key)[:8]}"
            )

        ss_data_dict = {ss.sender: ss for ss in ss_datas}
        ss_commitment_dict = {ss.sender: ss for ss in ss_commitments}

        seed_shares = {}
        sk_shares = {}
        try:
            for u in u2:
                data = ss_data_dict.get(u)
                commitment = ss_commitment_dict.get(u)
                if data is not None and commitment is not None:
                    seed_share = aes.decrypt(commu_keys[u], data.seed)
                    seed_commitment = commitment.seed_commitment
                    if seed_commitment == utils.calc_commitment(seed_share):
                        seed_shares[u] = seed_share
                        _logger.debug(
                            f"{u[:8]} -> {self.node_address[:8]} seed share {serialize.bytes_to_hex(seed_share)[:8]}"
                        )

                    sk_share = aes.decrypt(commu_keys[u], data.secret_key)
                    sk_commitment = commitment.secret_key_commitment
                    if sk_commitment == utils.calc_commitment(sk_share):
                        sk_shares[u] = sk_commitment
                        _logger.debug(
                            f"{u[:8]} -> {self.node_address[:8]} secret key share {serialize.bytes_to_hex(sk_share)[:8]}"
                        )
        except Exception as e:
            _logger.exception(e)
            raise

        _logger.info(
            f"task {self.task_id} round {self.round} get and validate other members' secret shares",
            extra={"task_id": self.task_id},
        )

        return seed_shares, sk_shares

    def mask_result(
        self,
        u2: List[str],
        seed: bytes,
        sk2: bytes,
        pk2s: Dict[str, bytes],
        result: Dict[str, AggResultType],
    ) -> Dict[str, AggResultType]:
        masked_result = {}

        for var_name in result:
            tmp = {}
            for key, val in result[var_name].items():
                seed_mask = utils.make_mask(seed, val.shape)

                sk_mask = np.zeros(val.shape, np.int64)

                for addr in u2:
                    if self.node_address != addr:
                        pk2 = pk2s[addr]
                        share_key = ecdhe.generate_shared_key(sk2, pk2, self.curve)
                        mask = utils.make_mask(share_key, val.shape)
                        if self.node_address < addr:
                            sk_mask -= mask
                        else:
                            sk_mask += mask

                tmp[key] = (
                    utils.fix_precision(val, self.strategy.precision)
                    + seed_mask
                    + sk_mask
                )
            masked_result[var_name] = tmp

        return masked_result

    async def upload_result(
        self,
        u2: List[str],
        seed: bytes,
        sk2: bytes,
        pk2s: Dict[str, bytes],
        result: Dict[str, AggResultType],
    ):
        def _upload_result():
            _logger.debug(f"unmask result {result}")
            masked_result = self.mask_result(u2, seed, sk2, pk2s, result)
            _logger.debug(f"masked result {masked_result}")
            with TemporaryFile(mode="w+b") as file:
                serialize.dump_agg_result(file, masked_result)
                file.seek(0)
                self.client.upload_task_round_result(
                    self.node_address, self.task_id, self.round, file
                )
                _logger.info(
                    f"task {self.task_id} round {self.round} upload masked result",
                    extra={"task_id": self.task_id},
                )
                file.seek(0)
                commitment = utils.calc_commitment(file)
                _logger.debug(f"calculate commitment of task round {self.round} result")
                return commitment

        result_commitment = await pool.run_in_io(_upload_result)
        tx_hash = await chain.get_client().upload_result_commitment(
            self.node_address, self.task_id, self.round, result_commitment
        )
        _logger.info(
            f"[Masked Result Commitment] task {self.task_id} round {self.round} upload result commitment",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

    async def wait_aggregation_started(self) -> List[str]:
        event = await self.event_box.wait_for_event(
            "aggregation_started", self.strategy.wait_timeout * 2
        )
        assert isinstance(event, entity.AggregationStartedEvent)
        assert event.task_id == self.task_id
        assert event.round == self.round
        assert self.node_address in event.addrs
        return event.addrs

    async def upload_alive_seed_shares(
        self, alive_members: List[str], seed_shares: Dict[str, bytes]
    ):
        _logger.info(
            f"task {self.task_id} round {self.round} alive members {alive_members}",
            extra={"task_id": self.task_id},
        )
        res: List[bytes] = []
        for addr in alive_members:
            res.append(seed_shares[addr])
        tx_hash = await chain.get_client().upload_seed(
            self.node_address,
            self.task_id,
            self.round,
            alive_members,
            res,
        )
        _logger.info(
            f"[Secret Sharing Parts Data] task {self.task_id} round {self.round} upload alive members' seed secret shares",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

    async def upload_dead_sk_shares(
        self, dead_members: List[str], sk_shares: Dict[str, bytes]
    ):
        if len(dead_members) > 0:
            _logger.info(
                f"task {self.task_id} round {self.round} dead members {dead_members}",
                extra={"task_id": self.task_id},
            )
            res: List[bytes] = []
            for addr in dead_members:
                res.append(sk_shares[addr])
            tx_hash = await chain.get_client().upload_secret_key(
                self.node_address,
                self.task_id,
                self.round,
                dead_members,
                res,
            )
            _logger.info(
                f"[Secret Sharing Parts Data] task {self.task_id} round {self.round} upload dead members' secret key secret shares",
                extra={"task_id": self.task_id, "tx_hash": tx_hash},
            )
