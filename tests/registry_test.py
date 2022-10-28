import asyncio

import pytest
from delta_node import db, registry, chain
from delta_node.chain import identity


@pytest.mark.asyncio
async def test_register():
    await db.init("sqlite+aiosqlite://")
    chain.init("127.0.0.1", 4500)
    url = "http://127.0.0.1:6800"
    name = "node1"

    r = registry.Registry(url, name)
    await r.register()

    fut = asyncio.create_task(r.start(interval=1))
    
    address = await registry.get_node_address()
    info = await identity.get_client().get_node_info(address)
    assert info.address == address
    assert info.name == name
    assert info.url == url

    try:
        await asyncio.wait_for(fut, timeout=2)
    except asyncio.TimeoutError:
        pass

    await r.stop()
    await r.unregister()
    chain.close()
    await db.close()