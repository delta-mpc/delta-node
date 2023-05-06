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
    await identity_client.update_url(address, url)
    # update name
    new_name = "node_1"
    await identity_client.update_name(address, new_name)
    info = await identity_client.get_node_info(address)
    assert info.name == new_name
    await identity_client.update_name(address, name)
    # get nodes
    nodes, _ = await identity_client.get_nodes(1, 20)
    assert address in [node.address for node in nodes]
    node = next(filter(lambda node: node.address == address, nodes))
    assert node.name == name
    assert node.url == url

