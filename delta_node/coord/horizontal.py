import asyncio
import json
import logging
import os
import random
from collections import defaultdict
from typing import Dict, List, Optional

import delta
import delta.serialize
import numpy as np
import sqlalchemy as sa
from delta.algorithm.horizontal import HorizontalAlgorithm
from delta_node import chain, db, entity, pool, registry, serialize, utils
from delta_node.crypto import ecdhe, shamir
from sqlalchemy import func

from . import loc

_logger = logging.getLogger(__name__)


async def run_task(task_entity: entity.Task):
    loop = asyncio.get_running_loop()

    task_id = task_entity.task_id

    task = await loop.run_in_executor(pool.IO_POOL, init_task, task_id)
    alg = task.algorithm()
    max_rounds = task.max_rounds
    del task

    node_address = await registry.get_node_address()
    async with db.session_scope() as sess:
        q = (
            sa.select(entity.TaskRound)
            .where(entity.TaskRound.task_id == task_id)
            .order_by(sa.desc(entity.TaskRound.round))
            .limit(1)
            .offset(0)
        )
        round_entity: Optional[entity.TaskRound] = (
            (await sess.execute(q)).scalars().first()
        )
    start_round = 1 if round_entity is None else round_entity.round

    try:
        for round in range(start_round, max_rounds + 1):
            await run_task_round(alg, node_address, task_id, round)
        async with db.session_scope() as sess:
            task_entity.status = entity.TaskStatus.FINISHED
            sess.add(task_entity)
            await sess.commit()
        await finish_task(node_address, task_id)
    except Exception:
        async with db.session_scope() as sess:
            task_entity.status = entity.TaskStatus.ERROR
            sess.add(task_entity)
            await sess.commit()
        _logger.info(f"task {task_id} error", extra={"task_id": task_id})
        raise


def init_task(task_id: str):
    config_file = loc.task_config_file(task_id)
    task = delta.serialize.load_task(config_file)
    assert isinstance(task, delta.task.HorizontalTask)

    init_weight_file = loc.task_weight_file(task_id, 0)
    if not os.path.exists(init_weight_file):
        weight = task.get_weight()
        delta.serialize.dump_arr(init_weight_file, weight)
    return task


async def finish_task(node_address: str, task_id: str):
    tx_hash = await chain.get_client().finish_task(node_address, task_id)
    async with db.session_scope() as sess:
        q = sa.select(entity.Task).where(entity.Task.task_id == task_id)
        task: entity.Task = (await sess.execute(q)).scalar_one()
        task.status = entity.TaskStatus.FINISHED
        sess.add(task)
        await sess.commit()
    _logger.info(
        f"task {task_id} finished", extra={"task_id": task_id, "tx_hash": tx_hash}
    )


async def run_task_round(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    # start round
    tx_hash = await chain.get_client().start_round(node_address, task_id, round)
    _logger.info(
        f"task {task_id} round {round} start",
        extra={"task_id": task_id, "tx_hash": tx_hash},
    )

    connection_timeout = alg.connnection_timeout or 60
    wait_timeout = alg.wait_timeout or 60

    # wait for clients to join the round
    await asyncio.sleep(connection_timeout)
    # select candidates
    await select_candidates(alg, node_address, task_id, round)

    # wait for clients to upload secret shares
    await asyncio.sleep(connection_timeout)
    # start calculation
    await start_calculation(alg, node_address, task_id, round)

    # wait for clients to do calculation and upload result
    await asyncio.sleep(wait_timeout)
    # start aggregation
    await start_aggreation(alg, node_address, task_id, round)

    # wait for clients to upload seed of secret key secret share to coordinator to unmask result
    await asyncio.sleep(connection_timeout)
    # end round
    await end_round(alg, node_address, task_id, round)


async def select_candidates(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    async with db.session_scope() as sess:
        # wait for clients to join in the round

        task_round = await chain.get_client().get_task_round(task_id, round)

        clients = task_round.clients
        if len(clients) < alg.min_clients:
            raise ValueError("not enough clients in select candidates")

        if len(clients) > alg.max_clients:
            clients = random.sample(clients, alg.max_clients)

        # update db
        task_round.clients = clients
        task_round.status = entity.RoundStatus.RUNNING
        sess.add(task_round)
        for addr in clients:
            member = entity.RoundMember(
                task_round.id, addr, entity.RoundStatus.RUNNING, task_round
            )
            sess.add(member)
        sess.add(task_round)

        await sess.commit()
        # select candidates
        tx_hash = await chain.get_client().select_candidates(
            node_address, task_id, round, clients
        )
        _logger.info(
            f"task {task_id} round {round} select candidates {clients}",
            extra={"task_id": task_id, "tx_hash": tx_hash},
        )


async def start_calculation(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    async with db.session_scope() as sess:
        # get clients which has uploaded secret shares
        q = (
            sa.select(entity.TaskRound)
            .where(entity.TaskRound.task_id == task_id)
            .where(entity.TaskRound.round == round)
        )
        round_entity: entity.TaskRound = (await sess.execute(q)).scalar_one()

        q = (
            sa.select(func.count(entity.RoundMember.id))
            .where(entity.RoundMember.round_id == round_entity.id)
            .where(entity.RoundMember.status == entity.RoundStatus.RUNNING)
        )
        last_clients_cnt: int = (await sess.execute(q)).scalar_one()

        q = (
            sa.select(entity.RoundMember)
            .where(entity.RoundMember.round_id == round_entity.id)
            .where(entity.RoundMember.status == entity.RoundStatus.RUNNING)
            .join(entity.RoundMember.send_shares)
            .group_by(entity.RoundMember.id)
            .having(func.count(entity.SecretShare.id) == last_clients_cnt)
        )
        members: List[entity.RoundMember] = (await sess.execute(q)).scalars().all()

        next_clients = [member.address for member in members]
        if len(next_clients) < alg.min_clients:
            raise ValueError("not enough clients in start calculation")

        # update db
        round_entity.status = entity.RoundStatus.CALCULATING
        for member in members:
            member.status = entity.RoundStatus.CALCULATING
        sess.add(round_entity)
        sess.add_all(members)
        await sess.commit()
        # start calculation
        tx_hash = await chain.get_client().start_calculation(
            node_address, task_id, round, next_clients
        )
        _logger.info(
            f"task {task_id} round {round} {next_clients} start calculation",
            extra={"task_id": task_id, "tx_hash": tx_hash},
        )


def get_local_result_commitments(task_id: str, round: int) -> Dict[str, bytes]:
    res = {}
    for root, _, filenames in os.walk(loc.task_round_result_dir(task_id, round)):
        for filename in filenames:
            with open(os.path.join(root, filename), mode="rb") as f:
                commitment = utils.calc_commitment(f)
            address = filename[:-7]  # {address}.result
            res[address] = commitment
    return res


async def check_result_commitments(
    task_id: str, round: int, client: str, commitment: bytes
):
    commitment_ = await chain.get_client().get_result_commitment(task_id, round, client)
    if commitment_ == commitment:
        return client
    else:
        return None


def make_masked_result(task_id: str, round: int, clients: List[str]):
    total_result = None
    for client in clients:
        result_filename = loc.task_member_result_file(task_id, round, client)
        result_arr = delta.serialize.load_arr(result_filename)
        if total_result is None:
            total_result = result_arr
        else:
            total_result += result_arr
    assert total_result is not None
    _logger.debug(f"masked arr {total_result} {total_result.dtype}")
    delta.serialize.dump_arr(loc.task_masked_result_file(task_id, round), total_result)
    _logger.info(
        f"task {task_id} round {round} masked result {total_result}",
        extra={"task_id": task_id},
    )

    if os.path.exists(loc.task_round_metrics_dir(task_id, round)):
        total_metrics = defaultdict(int)
        for client in clients:
            metrics_filename = loc.task_member_metrics_file(task_id, round, client)
            with open(metrics_filename, mode="r", encoding="utf-8") as f:
                metrics = json.load(f)
            for key, val in metrics.items():
                total_metrics[key] += val
        _logger.debug(f"masked metrics {total_metrics}")
        masked_metrics_filename = loc.task_masked_metrics_file(task_id, round)
        with open(masked_metrics_filename, mode="w", encoding="utf-8") as f:
            json.dump(total_metrics, f)
        _logger.info(
            f"task {task_id} round {round} masked metrics {dict(total_metrics)}",
            extra={"task_id": task_id},
        )


async def start_aggreation(
    alg: HorizontalAlgorithm,
    node_address: str,
    task_id: str,
    round: int,
):
    loop = asyncio.get_running_loop()

    async with db.session_scope() as sess:
        result_commitments = await loop.run_in_executor(
            pool.IO_POOL, get_local_result_commitments, task_id, round
        )

        futs: List[asyncio.Task[Optional[str]]] = []
        for client, commitment in result_commitments.items():
            fut = asyncio.create_task(
                check_result_commitments(task_id, round, client, commitment)
            )
            futs.append(fut)

        clients = await asyncio.gather(*futs)
        valid_clients = [client for client in clients if client is not None]
        if len(valid_clients) < alg.min_clients:
            raise ValueError("not enough clients in start aggregation")

        await loop.run_in_executor(
            pool.WORKER_POOL, make_masked_result, task_id, round, valid_clients
        )

        # update db
        q = (
            sa.select(entity.TaskRound)
            .where(entity.TaskRound.task_id == task_id)
            .where(entity.TaskRound.round == round)
        )
        round_entity: entity.TaskRound = (await sess.execute(q)).scalar_one()

        q = (
            sa.select(entity.RoundMember)
            .where(entity.RoundMember.round_id == round_entity.id)
            .where(entity.RoundMember.status == entity.RoundStatus.CALCULATING)
            .where(entity.RoundMember.address.in_(valid_clients))  # type: ignore
        )
        members: List[entity.RoundMember] = (await sess.execute(q)).scalars().all()

        round_entity.status = entity.RoundStatus.AGGREGATING
        for member in members:
            member.status = entity.RoundStatus.AGGREGATING
        sess.add(round_entity)
        sess.add_all(members)
        await sess.commit()
        # start aggregation
        tx_hash = await chain.get_client().start_aggregation(
            node_address, task_id, round, valid_clients
        )
        _logger.info(
            f"task {task_id} round {round} {valid_clients} start aggregation",
            extra={"task_id": task_id, "tx_hash": tx_hash},
        )


def unmask_result(
    task_id: str,
    round: int,
    pub_keys: Dict[str, bytes],
    secret_keys: Dict[str, bytes],
    seeds: Dict[str, bytes],
    curve: ecdhe.EllipticCurve,
    precision: int,
):

    share_keys = {}
    for u, sk in secret_keys.items():
        for v, pk in pub_keys.items():
            key = ecdhe.generate_shared_key(sk, pk, curve)
            share_keys[(u, v)] = key

    mask_arr = delta.serialize.load_arr(loc.task_masked_result_file(task_id, round))
    metrics_filename = loc.task_masked_metrics_file(task_id, round)

    seed_mask = np.zeros_like(mask_arr, dtype=np.int64)
    sk_mask = np.zeros_like(mask_arr, dtype=np.int64)

    for addr, seed in seeds.items():
        mask = utils.make_mask(seed, mask_arr.shape)
        _logger.debug(f"{addr} seed mask {mask}")
        seed_mask += mask

    for (u, v), key in share_keys.items():
        mask = utils.make_mask(key, mask_arr.shape)
        if u < v:
            sk_mask -= mask
        else:
            sk_mask += mask

    _logger.debug(f"seed mask {seed_mask} {seed_mask.dtype}")
    _logger.debug(f"sk mask {sk_mask} {sk_mask.dtype}")  # type: ignore
    unmask_arr: np.ndarray = mask_arr - seed_mask + sk_mask  # type: ignore
    unmask_arr = utils.unfix_precision(unmask_arr, precision)
    unmask_arr /= len(seeds)
    _logger.debug(f"weight arr: {unmask_arr}")
    delta.serialize.dump_arr(loc.task_weight_file(task_id, round), unmask_arr)
    _logger.info(
        f"task {task_id} round {round} unmasked result {unmask_arr}",
        extra={"task_id": task_id},
    )

    if os.path.exists(metrics_filename):
        with open(metrics_filename, mode="r", encoding="utf-8") as f:
            metrics = json.load(f)
            _logger.debug(f"metrics: {metrics}")
        metrics_keys, metrics_vals = zip(*metrics.items())
        _logger.debug(f"metrics vals {metrics_vals}")
        mask_metrics_arr = np.array(metrics_vals, dtype=np.int64)

        seed_mask = np.zeros_like(mask_metrics_arr)
        sk_mask = np.zeros_like(mask_metrics_arr)

        for addr, seed in seeds.items():
            mask = utils.make_mask(seed, mask_metrics_arr.shape)
            _logger.debug(f"{addr} seed mask {mask}")
            seed_mask += mask

        for (u, v), key in share_keys.items():
            mask = utils.make_mask(key, mask_metrics_arr.shape)
            if u < v:
                sk_mask -= mask
            else:
                sk_mask += mask

        unmask_metrics_arr: np.ndarray = mask_metrics_arr - seed_mask + sk_mask  # type: ignore
        _logger.debug(f"unmask_metrics_arr: {unmask_metrics_arr}")
        unmask_metrics_arr = utils.unfix_precision(unmask_metrics_arr, precision)
        unmask_metrics_arr /= len(seeds)
        unmask_metrics = {
            key: val for key, val in zip(metrics_keys, unmask_metrics_arr.tolist())
        }
        _logger.debug(f"metrics: {unmask_metrics}")
        with open(
            loc.task_metrics_file(task_id, round), mode="w", encoding="utf-8"
        ) as f:
            json.dump(unmask_metrics, f)
        _logger.info(
            f"task {task_id} round {round} metrics {unmask_metrics}",
            extra={"task_id": task_id},
        )


async def end_round(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    loop = asyncio.get_running_loop()

    async with db.session_scope() as sess:
        q = (
            sa.select(entity.TaskRound)
            .where(entity.TaskRound.task_id == task_id)
            .where(entity.TaskRound.round == round)
        )
        round_entity: entity.TaskRound = (await sess.execute(q)).scalar_one()

        q = (
            sa.select(entity.RoundMember)
            .where(entity.RoundMember.round_id == round_entity.id)
            .where(entity.RoundMember.status == entity.RoundStatus.AGGREGATING)
        )
        alive_members: List[entity.RoundMember] = (
            (await sess.execute(q)).scalars().all()
        )
        alive_addrs = [member.address for member in alive_members]
        _logger.info(
            f"task {task_id} round {round} alive members {alive_addrs}",
            extra={"task_id": task_id},
        )

        q = (
            sa.select(entity.RoundMember)
            .where(entity.RoundMember.round_id == round_entity.id)
            .where(entity.RoundMember.status == entity.RoundStatus.CALCULATING)
        )
        dead_members: List[entity.RoundMember] = (await sess.execute(q)).scalars().all()
        dead_addrs = [member.address for member in dead_members]
        if len(dead_addrs):
            _logger.info(
                f"task {task_id} round {round} dead members {dead_addrs}",
                extra={"task_id": task_id},
            )
        else:
            _logger.info(f"task {task_id} round {round} no dead members")

        secret_share = shamir.SecretShare(alg.min_clients)

        # members who upload secret shares for unmasking
        final_addrs = set(alive_addrs)

        # get secret key of dead members
        secret_key_shares: Dict[str, List[bytes]] = defaultdict(list)
        secret_keys: Dict[str, bytes] = {}
        if len(dead_addrs) > 0:
            for receiver in alive_addrs:
                ss_datas = await chain.get_client().get_secret_share_datas(
                    task_id, round, dead_addrs, receiver
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
                        f"task {task_id} round {round} {receiver} upload dead members sk secret share",
                        extra={"task_id": task_id},
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
                task_id, round, alive_addrs, receiver
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
                    f"task {task_id} round {round} {receiver} upload alive members seed secret share"
                )
            else:
                final_addrs.remove(receiver)
        for sender, shares in seed_shares.items():
            seeds[sender] = secret_share.resolve_shares(shares)
            _logger.debug(
                f"{sender[:8]} seed {serialize.bytes_to_hex(seeds[sender])[:8]}"
            )
        _logger.info(
            f"task {task_id} round {round} {final_addrs} complete task execution",
            extra={"task_id": task_id},
        )

        pks = await chain.get_client().get_client_public_keys(
            task_id, round, alive_addrs
        )
        pk2_dict = {addr: pk[1] for addr, pk in zip(alive_addrs, pks)}
        _logger.info(
            f"task {task_id} round {round} get alive members public keys",
            extra={"task_id": task_id},
        )

        curve = ecdhe.CURVES[alg.curve]
        precision = alg.precision
        await loop.run_in_executor(
            pool.WORKER_POOL,
            unmask_result,
            task_id,
            round,
            pk2_dict,
            secret_keys,
            seeds,
            curve,
            precision,
        )

        # update db
        round_entity.status = entity.RoundStatus.FINISHED
        sess.add(round_entity)
        for member in alive_members:
            if member.address in final_addrs:
                member.status = entity.RoundStatus.FINISHED
                sess.add(member)
        await sess.commit()

        # end round
        tx_hash = await chain.get_client().end_round(node_address, task_id, round)
        _logger.info(
            f"task {task_id} round {round} finish",
            extra={"task_id": task_id, "tx_hash": tx_hash},
        )
