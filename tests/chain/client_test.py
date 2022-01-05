import asyncio
import random

import pytest
from delta_node import chain, entity
from grpclib.client import Channel


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client():
    async with Channel("127.0.0.1", 4500, ssl=False) as ch:
        client = chain.ChainClient(ch)
        yield client


url = "127.0.0.1:6700"
name = "node1"


@pytest.fixture(scope="module")
async def address(client: chain.ChainClient):
    _, address = await client.join(url, name)
    yield address
    await client.leave(address)


@pytest.mark.asyncio
async def test_client(client: chain.ChainClient, address: str):
    global name, url
    info = await client.get_node_info(address)
    assert info.name == name
    assert info.url == url
    # update url
    new_url = "127.0.0.1:6800"
    await client.updaet_url(address, new_url)
    info = await client.get_node_info(address)
    assert info.url == new_url
    url = new_url
    # update name
    new_name = "node_1"
    await client.update_name(address, new_name)
    info = await client.get_node_info(address)
    assert info.name == new_name
    name = new_name
    # get nodes
    nodes, count = await client.get_nodes(1, 20)
    assert count == 1
    assert nodes[0].address == address
    assert nodes[0].name == name
    assert nodes[0].url == url

    # event generator
    event_gen = client.subscribe(address)

    # create task
    event_fut = asyncio.ensure_future(event_gen.asend(None))
    dataset = "mnist"
    task_commitment = bytes(random.getrandbits(8) for _ in range(32))
    task_type = "horizontal"
    _, task_id = await client.create_task(address, dataset, task_commitment, task_type)
    event = await event_fut
    assert isinstance(event, entity.TaskCreateEvent)
    assert event.address == address
    assert event.task_id == task_id
    assert event.dataset == dataset
    assert event.commitment == task_commitment
    assert event.url == url
    assert event.task_type == task_type

    # start round
    round = 1
    await client.start_round(address, task_id, round)
    event = await event_gen.asend(None)
    assert isinstance(event, entity.RoundStartedEvent)
    assert event.task_id == task_id
    assert event.round == round

    # join round
    pk1 = bytes(random.getrandbits(8) for _ in range(33))
    pk2 = bytes(random.getrandbits(8) for _ in range(33))
    await client.join_round(address, task_id, round, pk1, pk2)
    task_round = await client.get_task_round(task_id, round)
    assert task_round.round == 1
    assert task_round.status == entity.RoundStatus.STARTED
    assert len(task_round.clients) == 1
    assert task_round.clients[0] == address

    # select candidates
    await client.select_candidates(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, entity.PartnerSelectedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload seed commitment and secret key commitment
    seed_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await client.upload_seed_commitment(
        address, task_id, round, [address], [seed_commitment]
    )
    secret_key_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await client.upload_secret_key_commitment(
        address, task_id, round, [address], [secret_key_commitment]
    )
    ss_datas = await client.get_secret_share_datas(task_id, round, [address], address)
    assert len(ss_datas) == 1
    assert len(ss_datas[0].seed) == 0
    assert len(ss_datas[0].secret_key) == 0
    assert ss_datas[0].seed_commitment == seed_commitment
    assert ss_datas[0].secret_key_commitment == secret_key_commitment

    # get client public keys
    pks = await client.get_client_public_keys(task_id, round, [address])
    assert len(pks) == 1
    assert pks[0][0] == pk1
    assert pks[0][1] == pk2

    # start calculation
    await client.start_calculation(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, entity.CalculationStartedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload and get result commitment
    result_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await client.upload_result_commitment(address, task_id, round, result_commitment)
    result_commitment_ = await client.get_result_commitment(task_id, round, address)
    assert result_commitment == result_commitment_

    # start aggregation
    await client.start_aggregation(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, entity.AggregationStartedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload seed and secret key share
    seed_share = bytes(random.getrandbits(8) for _ in range(32))
    await client.upload_seed(address, task_id, round, [address], [seed_share])
    ss_datas = await client.get_secret_share_datas(task_id, round, [address], address)
    assert len(ss_datas) == 1
    assert ss_datas[0].seed == seed_share
    assert len(ss_datas[0].secret_key) == 0

    # end round
    await client.end_round(address, task_id, round)
    event = await event_gen.asend(None)
    assert isinstance(event, entity.RoundEndedEvent)
    assert event.task_id == task_id
    assert event.round == round
