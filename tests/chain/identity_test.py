from delta_node.chain import identity


async def test_identity(identity_client: identity.Client):
    url = "http://127.0.0.1:6700"
    name = "node1"
    # join
    _, address = await identity_client.join(url, name)

    info = await identity_client.get_node_info(address)
    assert info.name == name
    assert info.url == url
    # update url
    new_url = "http://127.0.0.1:6800"
    await identity_client.update_url(address, new_url)
    info = await identity_client.get_node_info(address)
    assert info.url == new_url
    url = new_url
    # update name
    new_name = "node_1"
    await identity_client.update_name(address, new_name)
    info = await identity_client.get_node_info(address)
    assert info.name == new_name
    name = new_name
    # get nodes
    nodes, count = await identity_client.get_nodes(1, 20)
    assert count == 1
    assert nodes[0].address == address
    assert nodes[0].name == name
    assert nodes[0].url == url

