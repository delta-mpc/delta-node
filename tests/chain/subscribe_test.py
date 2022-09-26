import asyncio

from delta_node.chain import subscribe
from delta_node.entity import HeartbeatEvent


async def test_subscribe_heartbeart(address: str, subscribe_client: subscribe.Client):
    event_gen = subscribe_client.subscribe(address, timeout=1, yield_heartbeat=True)

    event = await asyncio.wait_for(event_gen.asend(None), timeout=2)
    assert isinstance(event, HeartbeatEvent)
    