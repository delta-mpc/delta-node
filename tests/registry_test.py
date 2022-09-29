
import pytest
from delta_node import db, registry, chain
from delta_node.chain import identity


@pytest.mark.asyncio
async def test_register():
    await db.init("sqlite+aiosqlite://")
    chain.init("127.0.0.1", 4500)
    url = "http://127.0.0.1:6800"
    name = "node1"
    await registry.register(url, name)
    address = await registry.get_node_address()

    node_info = await identity.get_client().get_node_info(address=address)
    assert node_info.address == address
    assert node_info.name == name
    assert node_info.url == url

    await registry.unregister()
    chain.close()
    await db.close()