from __future__ import annotations

import asyncio
import logging
import os
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Tuple

import sqlalchemy as sa
from delta.core.strategy import Strategy
from delta.core.task import AggResultType
from sqlalchemy import func

from delta_node import db, pool, serialize, utils
from delta_node.entity.hlr import RoundMember, RoundStatus, TaskRound, SecretShare
from delta_node.chain import hlr as chain
from delta_node.crypto import ecdhe, shamir
from delta_node.coord import loc
from .context import ServerTaskContext

_logger = logging.getLogger(__name__)


class ServerAggregator(object):
    def __init__(
        self,
        node_address: str,
        task_round: TaskRound,
        strategy: Strategy,
        agg_vars: List[str],
    ) -> None:
        self.node_address = node_address
        self.task_round = task_round
        self.task_id = task_round.task_id
        self.round = task_round.round
        self.strategy = strategy
        self.agg_vars = agg_vars

    @asynccontextmanager
    async def aggregate(self, ctx: ServerTaskContext) -> AsyncGenerator[None, None]:
        members, result = await self.gather()

        for var_name in self.agg_vars:
            ctx.set_agg_result(var_name, result[var_name], len(members))

        yield

        async with db.session_scope() as sess:
            self.task_round.status = RoundStatus.FINISHED
            task_round = await sess.merge(self.task_round)
            sess.add(task_round)
            for member in members:
                member = await sess.merge(member)
                member.status = RoundStatus.FINISHED
                member.round = task_round
                sess.add(member)
            await sess.commit()

    async def gather(self) -> Tuple[List[RoundMember], Dict[str, AggResultType]]:
        # wait for clients to join the round
        await asyncio.sleep(self.strategy.connection_timeout)
        # select candidates
        u1 = await self.select_u1()
        await self.select_candidates(u1)

        # wait for clients to upload secret shares
        await asyncio.sleep(self.strategy.connection_timeout)
        # get clients who have upload secret shares
        u2 = await self.get_u2(u1)
        # start calculation
        await self.start_calculation(u2)

        # wait for clients to do calculation and upload result
        await asyncio.sleep(self.strategy.wait_timeout)
        u3 = await self.get_u3(u2)
        u3, masked_result = await pool.run_in_worker(self.make_masked_results, u3)

        # start aggregation
        await self.start_aggregation(u3)
        # wait for clients to upload seed of secret key secret share to coordinator to unmask result
        await asyncio.sleep(self.strategy.connection_timeout)
        # unmask result
        result = await self.unmask_result(u2, u3, masked_result)
        _logger.debug(f"coord aggregate result {result}")
        return u3, result

    async def select_u1(self) -> List[RoundMember]:
        task_round = await chain.get_client().get_task_round(self.task_id, self.round)
        u0 = task_round.joined_clients

        async with db.session_scope() as sess:
            q = (
                sa.select(TaskRound)
                .where(TaskRound.task_id == self.task_id)
                .where(TaskRound.round == self.round - 1)
                .where(TaskRound.status == RoundStatus.FINISHED)
            )
            last_round: TaskRound | None = (
                await sess.execute(q)
            ).scalar_one_or_none()

            last_round_clients: List[str] | None = None
            if last_round is not None:
                q = (
                    sa.select(RoundMember)
                    .where(RoundMember.round_id == last_round.id)
                    .where(RoundMember.status == RoundStatus.FINISHED)
                )
                last_round_members: List[RoundMember] = (
                    (await sess.execute(q)).scalars().all()
                )
                last_round_clients = [member.address for member in last_round_members]

        clients = self.strategy.select(u0, last_round_clients)
        _logger.debug(f"task {self.task_id} round {self.round} id {self.task_round.id}")
        members = [
            RoundMember(
                self.task_round.id,
                addr,
                RoundStatus.RUNNING,
            )
            for addr in clients
        ]

        return members

    async def select_candidates(self, u1: List[RoundMember]):
        async with db.session_scope() as sess:
            self.task_round.joined_clients = [member.address for member in u1]
            self.task_round.status = RoundStatus.RUNNING
            task_round = await sess.merge(self.task_round)
            sess.add(task_round)
            for member in u1:
                member = await sess.merge(member)
                sess.add(member)

            await sess.commit()
        # select candidates
        addrs = [member.address for member in u1]
        tx_hash = await chain.get_client().select_candidates(
            self.node_address, self.task_id, self.round, addrs
        )
        _logger.info(
            f"[Select Candidates] task {self.task_id} round {self.round} select candidates {[u.address for u in u1]}",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

    async def get_u2(self, u1: List[RoundMember]) -> List[RoundMember]:
        async with db.session_scope() as sess:
            # get clients which has uploaded secret shares
            last_clients_cnt = len(u1)
            q = (
                sa.select(RoundMember)
                .where(RoundMember.round_id == self.task_round.id)
                .where(RoundMember.status == RoundStatus.RUNNING)
                .join(RoundMember.send_shares)
                .group_by(RoundMember.id)
                .having(func.count(SecretShare.id) == last_clients_cnt)
            )
            members: List[RoundMember] = (await sess.execute(q)).scalars().all()
            if len(members) < self.strategy.select_strategy.min_clients:
                raise ValueError("not enough clients in start calculation")
            return members

    async def start_calculation(self, u2: List[RoundMember]):
        async with db.session_scope() as sess:
            # update db
            self.task_round.status = RoundStatus.CALCULATING
            task_round = await sess.merge(self.task_round)
            for member in u2:
                member = await sess.merge(member)
                member.status = RoundStatus.CALCULATING
                member.round = task_round
                sess.add(member)
            sess.add(task_round)
            await sess.commit()
        # start calculation
        addrs = [member.address for member in u2]
        tx_hash = await chain.get_client().start_calculation(
            self.node_address, self.task_id, self.round, addrs
        )
        _logger.info(
            f"[Start Calculation] task {self.task_id} round {self.round} {addrs} start calculation",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

    def get_result_commitments(self) -> Dict[str, bytes]:
        res = {}
        for root, _, filenames in os.walk(
            loc.task_round_result_dir(self.task_id, self.round)
        ):
            for filename in filenames:
                with open(os.path.join(root, filename), mode="rb") as f:
                    commitment = utils.calc_commitment(f)
                address = filename[:-7]  # {address}.result
                res[address] = commitment
        return res

    async def check_result_commitments(self, commitments: Dict[str, Any]) -> List[str]:
        async def _check_one(addr: str, commitment: bytes) -> bool:
            commitment_ = await chain.get_client().get_result_commitment(
                self.task_id, self.round, addr
            )
            return commitment == commitment_

        is_valid = await asyncio.gather(
            *(_check_one(addr, commitment) for addr, commitment in commitments.items())
        )
        res = [addr for addr, valid in zip(commitments, is_valid) if valid]
        return res

    async def get_u3(self, u2: List[RoundMember]) -> List[RoundMember]:
        commitments = await pool.run_in_io(self.get_result_commitments)
        addrs = await self.check_result_commitments(commitments)

        addr_set = set(addrs)
        res = []
        for member in u2:
            if member.address in addr_set:
                res.append(member)

        if len(res) < self.strategy.select_strategy.min_clients:
            raise ValueError("not enough clients in start calculation")
        return res

    def make_masked_results(
        self, u3: List[RoundMember]
    ) -> Tuple[List[RoundMember], Dict[str, AggResultType]]:
        result: Dict[str, AggResultType] = defaultdict(dict)
        valid_members: List[RoundMember] = []

        for member in u3:
            result_filename = loc.task_member_result_file(
                self.task_id, self.round, member.address
            )
            member_result = serialize.load_agg_result(result_filename)
            var_names = member_result.keys()
            if (
                len(var_names) == len(self.agg_vars)
                and len(set(var_names) - set(self.agg_vars)) == 0
            ):
                valid_members.append(member)
                for var_name in var_names:
                    for key, val in member_result[var_name].items():
                        if key in result[var_name]:
                            result[var_name][key] += val
                        else:
                            result[var_name][key] = val

        return valid_members, result

    async def start_aggregation(self, u3: List[RoundMember]):
        async with db.session_scope() as sess:
            self.task_round.status = RoundStatus.AGGREGATING
            task_round = await sess.merge(self.task_round)
            for member in u3:
                member.status = RoundStatus.AGGREGATING
                member = await sess.merge(member, load=False)
                member.round = task_round
                sess.add(member)
            sess.add(task_round)
            await sess.commit()
        # start aggregation
        addrs = [member.address for member in u3]
        tx_hash = await chain.get_client().start_aggregation(
            self.node_address, self.task_id, self.round, addrs
        )
        _logger.info(
            f"[Start Aggregation] task {self.task_id} round {self.round} {addrs} start aggregation",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

    async def unmask_result(
        self,
        u2: List[RoundMember],
        u3: List[RoundMember],
        masked_result: Dict[str, AggResultType],
    ) -> Dict[str, AggResultType]:
        u2_addrs = [member.address for member in u2]
        u3_addrs = [member.address for member in u3]

        alive_addrs = u2_addrs
        dead_addrs = list(set(u2_addrs) - set(u3_addrs))
        if len(dead_addrs):
            _logger.info(
                f"task {self.task_id} round {self.round} dead members {dead_addrs}",
                extra={"task_id": self.task_id},
            )
        else:
            _logger.info(
                f"task {self.task_id} round {self.round} no dead members",
                extra={"task_id": self.task_id},
            )

        secret_share = shamir.SecretShare(self.strategy.select_strategy.min_clients)

        # members who upload secret shares for unmasking
        final_addrs = set(alive_addrs)

        # get secret key of dead members
        secret_key_shares: Dict[str, List[bytes]] = defaultdict(list)
        secret_keys: Dict[str, bytes] = {}
        if len(dead_addrs) > 0:
            for receiver in alive_addrs:
                ss_datas = await chain.get_client().get_secret_share_datas(
                    self.task_id, self.round, dead_addrs, receiver
                )
                if len(ss_datas) == len(dead_addrs) and all(
                    (
                        len(ss.seed) == 0
                        and len(ss.secret_key) > 0
                        and len(ss.secret_key_commitment) > 0
                        and utils.calc_commitment(ss.secret_key)
                        == ss.secret_key_commitment
                    )
                    for ss in ss_datas
                ):
                    for sender, ss in zip(dead_addrs, ss_datas):
                        secret_key_shares[sender].append(ss.secret_key)
                        _logger.debug(
                            f"{sender[:8]} -> {receiver[:8]} sk share {serialize.bytes_to_hex(ss.secret_key)[:8]}"
                        )
                    _logger.info(
                        f"task {self.task_id} round {self.round} {receiver} upload dead members sk secret share",
                    )
                else:
                    final_addrs.remove(receiver)
            for sender, shares in secret_key_shares.items():
                secret_keys[sender] = secret_share.resolve_shares(shares)
                _logger.debug(
                    f"{sender[:8]} sk2 {serialize.bytes_to_hex(secret_keys[sender])[:8]}"
                )

        # get secret key of alive members
        seed_shares: Dict[str, List[bytes]] = defaultdict(list)
        seeds: Dict[str, bytes] = {}
        for receiver in alive_addrs:
            ss_datas = await chain.get_client().get_secret_share_datas(
                self.task_id, self.round, alive_addrs, receiver
            )
            if len(ss_datas) == len(alive_addrs) and all(
                (
                    len(ss.secret_key) == 0
                    and len(ss.seed) > 0
                    and len(ss.seed_commitment) > 0
                    and utils.calc_commitment(ss.seed) == ss.seed_commitment
                )
                for ss in ss_datas
            ):
                for sender, ss in zip(alive_addrs, ss_datas):
                    seed_shares[sender].append(ss.seed)
                    _logger.debug(
                        f"{sender[:8]} -> {receiver[:8]} seed share {serialize.bytes_to_hex(ss.seed)[:8]}"
                    )
                _logger.info(
                    f"task {self.task_id} round {self.round} {receiver} upload alive members seed secret share"
                )
            else:
                final_addrs.remove(receiver)
        for sender, shares in seed_shares.items():
            seeds[sender] = secret_share.resolve_shares(shares)
            _logger.debug(
                f"{sender[:8]} seed {serialize.bytes_to_hex(seeds[sender])[:8]}"
            )
        _logger.info(
            f"task {self.task_id} round {self.round} {final_addrs} complete task execution",
            extra={"task_id": self.task_id},
        )

        pks = await chain.get_client().get_client_public_keys(
            self.task_id, self.round, alive_addrs
        )
        pk2_dict = {addr: pk[1] for addr, pk in zip(alive_addrs, pks)}
        _logger.info(
            f"task {self.task_id} round {self.round} get alive members public keys",
        )

        curve = ecdhe.CURVES[self.strategy.curve]

        def _unmask_result():
            share_keys = {}
            for u, sk in secret_keys.items():
                for v, pk in pk2_dict.items():
                    key = ecdhe.generate_shared_key(sk, pk, curve)
                    share_keys[(u, v)] = key

            res: Dict[str, AggResultType] = defaultdict(dict)
            for var_name in masked_result:
                for key, val in masked_result[var_name].items():
                    for addr, seed in seeds.items():
                        mask = utils.make_mask(seed, val.shape)
                        val -= mask

                    for (u, v), key in share_keys.items():
                        mask = utils.make_mask(key, val.shape)
                        if u < v:
                            val -= mask # type: ignore
                        else:
                            val += mask
                    res[var_name][key] = utils.unfix_precision(
                        val, self.strategy.precision
                    )
            return res

        return await pool.run_in_worker(_unmask_result)
