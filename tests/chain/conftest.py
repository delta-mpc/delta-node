import pytest
from delta_node import chain, db
from delta_node.chain import identity, datahub, horizontal, hlr, subscribe


pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module", autouse=True)
async def init(anyio_backend):
    await db.init("sqlite+aiosqlite://")
    await chain.init("127.0.0.1", 4500)
    yield
    await chain.close()
    await db.close()


@pytest.fixture(scope="module")
def identity_client():
    return identity.get_client()


@pytest.fixture(scope="module")
def datahub_client():
    return datahub.get_client()


@pytest.fixture(scope="module")
def horizontal_client():
    return horizontal.get_client()


@pytest.fixture(scope="module")
def hlr_client():
    return hlr.get_client()


@pytest.fixture(scope="module")
def subscribe_client():
    return subscribe.get_client()


@pytest.fixture(scope="module")
def url():
    return "http://127.0.0.1:6700"


@pytest.fixture(scope="module")
def name():
    return "node1"


@pytest.fixture()
async def address(identity_client: identity.Client, url: str, name: str):
    _, address = await identity_client.join(url, name)
    yield address
    await identity_client.leave(address)
