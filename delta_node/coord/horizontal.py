import asyncio
import os
import random
from typing import Dict, List, Optional, Tuple

import delta
import delta.serialize
from delta.algorithm.horizontal import HorizontalAlgorithm
import numpy as np
import sqlalchemy as sa
from delta_node import chain, db, entity, pool, registry, serialize, utils
from delta_node.crypto import ecdhe, shamir
from sqlalchemy import func

from . import loc


async def run_task(task_entity: entity.Task):
    loop = asyncio.get_running_loop()

    task_id = task_entity.task_id
    
    task = await loop.run_in_executor(pool.IO_POOL, init_task, task_id)
    alg = task.algorithm()
    max_rounds = task.max_rounds
    del task

    node_address = await registry.get_node_address()
    try:
        for round in range(1, max_rounds + 1):
            await run_task_round(alg, node_address, task_id, round)
        async with db.get_session() as sess:
            task_entity.status = entity.TaskStatus.FINISHED
            sess.add(task_entity)
            await sess.commit()

    except Exception:
        async with db.get_session() as sess:
            task_entity.status = entity.TaskStatus.ERROR
            sess.add(task_entity)
            await sess.commit()
        raise


def init_task(task_id: str):
    task = delta.serialize.load_task(loc.task_config_file(task_id))

    assert isinstance(task, delta.task.HorizontalTask)
    weight = task.get_weight()
    delta.serialize.dump_arr(loc.task_weight_file(task_id, 0), weight)
    return task


async def run_task_round(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    # start round
    await chain.get_client().start_round(node_address, task_id, round)

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
    await asyncio.sleep(wait_timeout)
    # end round
    await end_round(alg, node_address, task_id, round)


async def select_candidates(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    async with db.get_session() as sess:
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
        await chain.get_client().select_candidates(
            node_address, task_id, round, clients
        )


async def start_calculation(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    async with db.get_session() as sess:
        # get clients which has uploaded secret shares
        q = (
            sa.select(entity.TaskRound)
            .where(entity.TaskRound.task_id == task_id)
            .where(entity.TaskRound.round == round)
        )
        round_entity: entity.TaskRound = (await sess.execute(q)).scalar_one()

        q = (
            sa.select(func.count(entity.RoundMember))
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
        await chain.get_client().start_calculation(
            node_address, task_id, round, next_clients
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
    delta.serialize.dump_arr(loc.task_masked_result_file(task_id, round), total_result)


async def start_aggreation(
    alg: HorizontalAlgorithm,
    node_address: str,
    task_id: str,
    round: int,
):
    loop = asyncio.get_running_loop()

    async with db.get_session() as sess:
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
        await chain.get_client().start_aggregation(
            node_address, task_id, round, valid_clients
        )


async def get_seed_share(task_id: str, round: int, sender: str, receiver: str) -> bytes:
    ss_data = await chain.get_client().get_secret_share_data(
        task_id, round, sender, receiver
    )
    if len(ss_data.seed) > 0:
        commitment = utils.calc_commitment(ss_data.seed)
        assert commitment == ss_data.seed_commitment, ValueError(
            "seed commitment is inconsistent"
        )
        return ss_data.seed
    else:
        raise ValueError(
            """task {task_id} round {round} member {receiver} does not 
                            upload seed secret share of member {sender}"""
        )


async def get_seed(
    task_id: str,
    round: int,
    sender: str,
    receivers: List[str],
    secret_share: shamir.SecretShare,
) -> Tuple[bytes, List[str]]:
    loop = asyncio.get_running_loop()

    futs: List[asyncio.Task[bytes]] = []
    for receiver in receivers:
        fut = asyncio.create_task(get_seed_share(task_id, round, sender, receiver))
        futs.append(fut)
    shares = await asyncio.gather(*futs, return_exceptions=True)
    valid_receivers: List[str] = []
    valid_shares: List[shamir.Share] = []
    for receiver, share in zip(receivers, shares):
        if isinstance(share, bytes):
            valid_receivers.append(receiver)
            valid_shares.append(shamir.bytes_to_share(share))
    if len(valid_shares) < secret_share.threshold:
        raise ValueError("not enough clients in end round get seed")
    seed = await loop.run_in_executor(
        pool.WORKER_POOL, secret_share.resolve_shares, valid_shares
    )
    return serialize.int_to_bytes(seed), valid_receivers


async def get_secret_key_share(
    task_id: str, round: int, sender: str, receiver: str
) -> bytes:
    ss_data = await chain.get_client().get_secret_share_data(
        task_id, round, sender, receiver
    )
    if len(ss_data.secret_key) > 0:
        commitment = utils.calc_commitment(ss_data.secret_key)
        assert commitment == ss_data.secret_key_commitment, ValueError(
            "secret key commitment is inconsistent"
        )
        return ss_data.secret_key
    else:
        raise ValueError(
            """task {task_id} round {round} member {receiver} does not 
                            upload secret key secret share of member {sender}"""
        )


async def get_secret_key(
    task_id: str,
    round: int,
    sender: str,
    receivers: List[str],
    secret_share: shamir.SecretShare,
) -> Tuple[bytes, List[str]]:
    loop = asyncio.get_running_loop()

    futs: List[asyncio.Task[bytes]] = []
    for receiver in receivers:
        fut = asyncio.create_task(
            get_secret_key_share(task_id, round, sender, receiver)
        )
        futs.append(fut)
    shares = await asyncio.gather(*futs, return_exceptions=True)
    valid_receivers: List[str] = []
    valid_shares: List[shamir.Share] = []
    for receiver, share in zip(receivers, shares):
        if isinstance(share, bytes):
            valid_receivers.append(receiver)
            valid_shares.append(shamir.bytes_to_share(share))
    if len(valid_shares) < secret_share.threshold:
        raise ValueError("not enough clients in end round get secret key")
    secret_key = await loop.run_in_executor(
        pool.WORKER_POOL, secret_share.resolve_shares, valid_shares
    )
    return serialize.int_to_bytes(secret_key), valid_receivers


async def get_public_keys(
    task_id: str, round: int, clients: List[str]
) -> Dict[str, bytes]:
    futs: List[asyncio.Task[Tuple[bytes, bytes]]] = []
    for client in clients:
        fut = asyncio.create_task(
            chain.get_client().get_client_public_keys(task_id, round, client)
        )
        futs.append(fut)
    bytes_tups = await asyncio.gather(*futs)
    res = {client: tup[1] for client, tup in zip(clients, bytes_tups)}
    return res


def unmask_result(
    task_id: str,
    round: int,
    pub_keys: Dict[str, bytes],
    secret_keys: Dict[str, bytes],
    seeds: Dict[str, bytes],
    curve: ecdhe.EllipticCurve,
    precision: int,
):
    mask_arr = delta.serialize.load_arr(loc.task_masked_result_file(task_id, round))

    seed_mask = np.zeros_like(mask_arr)
    sk_mask = np.zeros_like(mask_arr)

    for seed in seeds.values():
        mask = utils.make_mask(seed, mask_arr.shape)
        seed_mask += mask

    for u, sk in secret_keys.items():
        for v, pk in pub_keys.items():
            key = ecdhe.generate_shared_key(sk, pk, curve)
            mask = utils.make_mask(key, mask_arr.shape)
            if u < v:
                sk_mask -= mask
            else:
                sk_mask += mask

    unmask_arr: np.ndarray = mask_arr - seed_mask + sk_mask  # type: ignore
    unmask_arr = utils.unfix_precision(unmask_arr, precision)
    delta.serialize.dump_arr(loc.task_weight_file(task_id, round), unmask_arr)


async def end_round(
    alg: HorizontalAlgorithm, node_address: str, task_id: str, round: int
):
    loop = asyncio.get_running_loop()

    async with db.get_session() as sess:
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

        q = (
            sa.select(entity.RoundMember)
            .where(entity.RoundMember)
            .where(entity.RoundMember.round_id == round_entity.id)
            .where(entity.RoundMember.status == entity.RoundStatus.CALCULATING)
        )
        dead_members: List[entity.RoundMember] = (await sess.execute(q)).scalars().all()
        dead_addrs = [member.address for member in dead_members]

        secret_share = shamir.SecretShare(alg.min_clients)

        # members who upload secret shares for unmasking
        final_addrs = set(alive_addrs)

        # get secret key of dead members
        secret_keys: Dict[str, bytes] = {}
        for sender in dead_addrs:
            secret_key, valid_addrs = await get_secret_key(
                task_id, round, sender, alive_addrs, secret_share
            )
            secret_keys[sender] = secret_key
            final_addrs.intersection_update(valid_addrs)

        # get secret key of alive members
        seeds: Dict[str, bytes] = {}
        for sender in alive_addrs:
            seed, valid_addrs = await get_seed(
                task_id, round, sender, alive_addrs, secret_share
            )
            seeds[sender] = seed
            final_addrs.intersection_update(valid_addrs)

        pub_keys = await get_public_keys(task_id, round, alive_addrs)

        # TODO: add curve and precision config in delta task
        curve = ecdhe.CURVES["secp256k1"]
        precision = 8
        await loop.run_in_executor(
            pool.WORKER_POOL,
            unmask_result,
            task_id,
            round,
            pub_keys,
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
        await chain.get_client().end_round(node_address, task_id, round)
