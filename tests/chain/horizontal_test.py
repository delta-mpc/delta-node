import asyncio
import random

from delta_node.chain import horizontal, subscribe
from delta_node.entity import (
    TaskCreateEvent,
    RoundStartedEvent,
    PartnerSelectedEvent,
    CalculationStartedEvent,
    AggregationStartedEvent,
    RoundEndedEvent,
    TaskFinishEvent
)
from delta_node.entity.horizontal import RoundStatus


async def test_horizontal(address: str, horizontal_client: horizontal.Client, subscribe_client: subscribe.Client, url: str):
    event_gen = subscribe_client.subscribe(address)

    # create task
    event_fut = asyncio.ensure_future(event_gen.asend(None))
    dataset = "mnist"
    task_commitment = bytes(random.getrandbits(8) for _ in range(32))
    task_type = "horizontal"
    _, task_id = await horizontal_client.create_task(address, dataset, task_commitment, task_type)
    event = await event_fut
    assert isinstance(event, TaskCreateEvent)
    assert event.address == address
    assert event.task_id == task_id
    assert event.dataset == dataset
    assert event.commitment == task_commitment
    assert event.url == url
    assert event.task_type == task_type

    # start round
    round = 1
    await horizontal_client.start_round(address, task_id, round)
    event = await event_gen.asend(None)
    assert isinstance(event, RoundStartedEvent)
    assert event.task_id == task_id
    assert event.round == round

    # join round
    pk1 = bytes(random.getrandbits(8) for _ in range(33))
    pk2 = bytes(random.getrandbits(8) for _ in range(33))
    await horizontal_client.join_round(address, task_id, round, pk1, pk2)
    task_round = await horizontal_client.get_task_round(task_id, round)
    assert task_round.round == 1
    assert task_round.status == RoundStatus.STARTED
    assert len(task_round.clients) == 1
    assert task_round.clients[0] == address

    # select candidates
    await horizontal_client.select_candidates(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, PartnerSelectedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload seed commitment and secret key commitment
    seed_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await horizontal_client.upload_seed_commitment(
        address, task_id, round, [address], [seed_commitment]
    )
    secret_key_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await horizontal_client.upload_secret_key_commitment(
        address, task_id, round, [address], [secret_key_commitment]
    )
    ss_datas = await horizontal_client.get_secret_share_datas(task_id, round, [address], address)
    assert len(ss_datas) == 1
    assert len(ss_datas[0].seed) == 0
    assert len(ss_datas[0].secret_key) == 0
    assert ss_datas[0].seed_commitment == seed_commitment
    assert ss_datas[0].secret_key_commitment == secret_key_commitment

    # get client public keys
    pks = await horizontal_client.get_client_public_keys(task_id, round, [address])
    assert len(pks) == 1
    assert pks[0][0] == pk1
    assert pks[0][1] == pk2

    # start calculation
    await horizontal_client.start_calculation(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, CalculationStartedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload and get result commitment
    result_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await horizontal_client.upload_result_commitment(address, task_id, round, result_commitment)
    result_commitment_ = await horizontal_client.get_result_commitment(task_id, round, address)
    assert result_commitment == result_commitment_

    # start aggregationd
    await horizontal_client.start_aggregation(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, AggregationStartedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload seed and secret key share
    seed_share = bytes(random.getrandbits(8) for _ in range(32))
    await horizontal_client.upload_seed(address, task_id, round, [address], [seed_share])
    ss_datas = await horizontal_client.get_secret_share_datas(task_id, round, [address], address)
    assert len(ss_datas) == 1
    assert ss_datas[0].seed == seed_share
    assert len(ss_datas[0].secret_key) == 0

    # end round
    await horizontal_client.end_round(address, task_id, round)
    event = await event_gen.asend(None)
    assert isinstance(event, RoundEndedEvent)
    assert event.task_id == task_id
    assert event.round == round

    # finish task
    await horizontal_client.finish_task(address, task_id)
    event = await event_gen.asend(None)
    assert isinstance(event, TaskFinishEvent)
    assert event.task_id == task_id

    await event_gen.aclose()
