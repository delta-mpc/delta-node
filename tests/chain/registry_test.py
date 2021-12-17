import os

import pytest
from delta_node import chain, db, registry


@pytest.mark.asyncio
async def test_register():
    await db.init("sqlite+aiosqlite:///test.db")
    chain.init("127.0.0.1", 4500)
    await registry.register("127.0.0.1:6800", "node1")
    address = await registry.get_node_address()

    node_info = await chain.get_client().get_node_info(address=address)
    assert node_info.address == address
    assert node_info.name == "node1"
    assert node_info.url == "127.0.0.1:6800"

    await registry.unregister()
    chain.close()
    os.remove("test.db")
