from delta_node.chain import datahub


async def test_datahub(address: str, datahub_client: datahub.Client):
    name = "mnist"
    commitment1 = bytes([0 for _ in range(31)] + [1])
    commitment2 = bytes([0 for _ in range(31)] + [2])
    await datahub_client.register(address, name, 0, commitment1)
    await datahub_client.register(address, name, 1, commitment2)

    _commitment1 = await datahub_client.get_data_commitment(address, name, 0)
    assert _commitment1 == commitment1
    _commitment2 = await datahub_client.get_data_commitment(address, name, 1)
    assert _commitment2 == commitment2
