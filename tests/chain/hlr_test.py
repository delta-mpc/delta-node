import asyncio
import random

from delta_node import serialize
from delta_node.chain import datahub, hlr, subscribe
from delta_node.entity import (
    AggregationStartedEvent,
    CalculationStartedEvent,
    PartnerSelectedEvent,
    RoundEndedEvent,
    RoundStartedEvent,
    TaskCreateEvent,
    TaskFinishEvent,
    TaskMemberVerifiedEvent,
    TaskVerificationConfirmedEvent,
)
from delta_node.entity.hlr import RoundStatus


async def test_horizontal(
    address: str,
    url: str,
    hlr_client: hlr.Client,
    subscribe_client: subscribe.Client,
    datahub_client: datahub.Client,
):
    dataset = "mnist1"
    data_commitment = serialize.int_to_bytes(
        6981156750146001390596683852942006945948523736948468087198643842575491393764
    )
    await datahub_client.register(address, dataset, 0, data_commitment)

    event_gen = subscribe_client.subscribe(address)

    # create task
    event_fut = asyncio.ensure_future(event_gen.asend(None))
    task_commitment = bytes(random.getrandbits(8) for _ in range(32))
    task_type = "hlr"
    enable_verify = True
    tolerance = 6
    _, task_id = await hlr_client.create_task(
        address, dataset, task_commitment, enable_verify, tolerance
    )
    event = await event_fut
    assert isinstance(event, TaskCreateEvent)
    assert event.address == address
    assert event.task_id == task_id
    assert event.dataset == dataset
    assert event.commitment == task_commitment
    assert event.url == url
    assert event.task_type == task_type
    assert event.enable_verify == enable_verify
    assert event.tolerance == tolerance

    # start round
    round = 1
    weight_commitment = serialize.int_to_bytes(
        4485354118406336729363675711000348342713746016780773923827638902243253344914
    )
    await hlr_client.start_round(address, task_id, round, weight_commitment)
    event = await event_gen.asend(None)
    assert isinstance(event, RoundStartedEvent)
    assert event.task_id == task_id
    assert event.round == round

    # get weight commitment
    _weight_commitment = await hlr_client.get_weight_commitment(task_id, round)
    assert _weight_commitment == weight_commitment

    # join round
    pk1 = bytes(random.getrandbits(8) for _ in range(33))
    pk2 = bytes(random.getrandbits(8) for _ in range(33))
    await hlr_client.join_round(address, task_id, round, pk1, pk2)
    task_round = await hlr_client.get_task_round(task_id, round)
    assert task_round.round == 1
    assert task_round.status == RoundStatus.STARTED
    assert len(task_round.joined_clients) == 1
    assert task_round.joined_clients[0] == address
    assert len(task_round.finished_clients) == 0

    # select candidates
    await hlr_client.select_candidates(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, PartnerSelectedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload seed commitment and secret key commitment
    seed_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await hlr_client.upload_seed_commitment(
        address, task_id, round, [address], [seed_commitment]
    )
    secret_key_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await hlr_client.upload_secret_key_commitment(
        address, task_id, round, [address], [secret_key_commitment]
    )
    ss_datas = await hlr_client.get_secret_share_datas(
        task_id, round, [address], address
    )
    assert len(ss_datas) == 1
    assert len(ss_datas[0].seed) == 0
    assert len(ss_datas[0].secret_key) == 0
    assert ss_datas[0].seed_commitment == seed_commitment
    assert ss_datas[0].secret_key_commitment == secret_key_commitment

    # get client public keys
    pks = await hlr_client.get_client_public_keys(task_id, round, [address])
    assert len(pks) == 1
    assert pks[0][0] == pk1
    assert pks[0][1] == pk2

    # start calculation
    await hlr_client.start_calculation(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, CalculationStartedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload and get result commitment
    result_commitment = bytes(random.getrandbits(8) for _ in range(32))
    await hlr_client.upload_result_commitment(
        address, task_id, round, result_commitment
    )
    result_commitment_ = await hlr_client.get_result_commitment(task_id, round, address)
    assert result_commitment == result_commitment_

    # start aggregationd
    await hlr_client.start_aggregation(address, task_id, round, [address])
    event = await event_gen.asend(None)
    assert isinstance(event, AggregationStartedEvent)
    assert event.task_id == task_id
    assert event.round == round
    assert len(event.addrs) == 1
    assert event.addrs[0] == address

    # upload seed and secret key share
    seed_share = bytes(random.getrandbits(8) for _ in range(32))
    await hlr_client.upload_seed(address, task_id, round, [address], [seed_share])
    ss_datas = await hlr_client.get_secret_share_datas(
        task_id, round, [address], address
    )
    assert len(ss_datas) == 1
    assert ss_datas[0].seed == seed_share
    assert len(ss_datas[0].secret_key) == 0

    # end round
    await hlr_client.end_round(address, task_id, round)
    event = await event_gen.asend(None)
    assert isinstance(event, RoundEndedEvent)
    assert event.task_id == task_id
    assert event.round == round

    # finish task
    await hlr_client.finish_task(address, task_id)
    event = await event_gen.asend(None)
    assert isinstance(event, TaskFinishEvent)
    assert event.task_id == task_id

    # verify
    proof = '{"A":["13989034285667332156863945648246897742674312644133132588373172835712588341153","5778726377028194157326570132911467619850434533037748124717051431170636978473","1"],"B":["7067988665891297605009556013994645698259560744489349482939628863695178106149","3772641902673928269308252846097173328741387070269402122961261392634566718339","1"],"C":["18076880681698079363538206973762272139905501717577910388157927392291980245900","4935815316812856497349036381677145356004722377435339508751844815015243310204","1"],"Z":["4149404417037143409963150090542277946936707828941879779695691354595910800811","13556978960241709399146172497703856702084938517589912645237126819962813143860","1"],"T1":["8289540291413456751366034229385039652935951787981229417089526810905739594141","6286515015273322741550608206414077974633693837790210572280564293179623798757","1"],"T2":["13833987513537201287546169846756552683447371358907114576816714749174310288608","12512688588930653647926172747413577527834504363572762172086871991189445619400","1"],"T3":["6882109800166642453526289235605128864108351565361407044449215505533636890557","61590497150453077797057837950959375353874323908322149746048922926860196244","1"],"eval_a":"12898297461251965369578031204217522202291648993068625717720394577876244771323","eval_b":"16906856015390455709233565884736716676955779941021643781713154533385019315556","eval_c":"13708333598733630691539421243869251790223241445099711061414908868648134072750","eval_s1":"5687624493605359331856737705531888037276978580018672829449163060450999654690","eval_s2":"7006571840591234412856343835916889617606267189975030540021236008759160050641","eval_zw":"1288929679404388863956973957139693728654822044168978603659468368994894316098","eval_r":"9567287344224728287155998783342384298725379281359290876413759823154289964166","Wxi":["7179084238719293720469501309467860616905930952121686397311179093011643220880","2378002621023216790784026892808797364630938303939799035332551852170058147012","1"],"Wxiw":["18089386244511803320810813708080348105684460352538469969259679547565493049373","17133643524870634106124851557608310040548287865712255292603319459784458626059","1"],"protocol":"plonk","curve":"bn128"}'
    pub_signals = [
        "21888242871839275222246405745257275088548364400416034299972841686575808495617",
        "29",
        "21888242871839275222246405745257275088548364400416034017709454186575808495617",
        "29",
        "21888242871839275222246405745257275088548364400416034336161954186575808495617",
        "29",
        "4485354118406336729363675711000348342713746016780773923827638902243253344914",
        "6981156750146001390596683852942006945948523736948468087198643842575491393764",
    ]

    _, valid = await hlr_client.verify(address, task_id, 3, proof, pub_signals, 0, 32)
    assert valid
    event = await event_gen.asend(None)
    assert isinstance(event, TaskMemberVerifiedEvent)
    assert event.address == address
    assert event.task_id == task_id
    assert event.verified

    # get verifier state
    state = await hlr_client.get_verifier_state(task_id)
    assert len(state.unfinished_clients) == 0
    assert len(state.invalid_clients) == 0
    assert state.valid

    # confirm verification
    await hlr_client.confirm_verification(address, task_id)
    event = await event_gen.asend(None)
    assert isinstance(event, TaskVerificationConfirmedEvent)
    assert event.task_id == task_id
