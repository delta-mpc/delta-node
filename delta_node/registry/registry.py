import asyncio
import logging
from typing import Optional

import sqlalchemy as sa
from async_lru import alru_cache
from delta_node import config, db
from delta_node.chain import identity
from delta_node.entity.identity import Node
from sqlalchemy.exc import NoResultFound

__all__ = ["get_node_address", "Registry"]


_logger = logging.getLogger(__name__)


@alru_cache
async def get_node_address() -> str:
    async with db.session_scope() as sess:
        q = sa.select(Node).where(Node.id == 1)
        try:
            node: Node = (await sess.execute(q)).scalars().one()
            return node.address
        except NoResultFound:
            _logger.error("node has not been registered")
            raise


class Registry(object):
    def __init__(
        self, url: str = config.node_url, name: str = config.node_name
    ) -> None:
        self.url = url
        self.name = name

        self.running_task: Optional[asyncio.Task] = None

    async def register(self):
        _, address = await identity.get_client().join(self.url, self.name)

        async with db.session_scope() as sess:
            q = sa.select(Node).where(Node.id == 1)
            node: Optional[Node] = (await sess.execute(q)).scalars().one_or_none()

            if node is not None:
                update = False
                if node.address != address:
                    node.address = address
                    update = True
                if node.url != self.url:
                    node.url = self.url
                    update = True
                if node.name != self.name:
                    node.name = self.name
                    update = True
                if update:
                    sess.add(node)
                    await sess.commit()
                    _logger.info(f"register new node, node address: {address}")
                else:
                    _logger.info(f"registered node, node address: {address}")
            else:
                node = Node(url=self.url, name=self.name, address=address)
                sess.add(node)
                await sess.commit()
                _logger.info(f"register new node, node address: {address}")

    async def unregister(self):
        address = await get_node_address()
        await identity.get_client().leave(address)

        async with db.session_scope() as sess:
            q = sa.select(Node).where(Node.id == 1)
            node = (await sess.execute(q)).scalar_one()

            await sess.delete(node)
            await sess.commit()

        _logger.info(f"node {address} leave")

    async def start(self, interval: int = 60):
        async def run():
            while True:
                await asyncio.sleep(interval)
                await identity.get_client().join(self.url, self.name)

        if self.running_task is None:
            self.running_task = asyncio.create_task(run())
            try:
                await self.running_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                _logger.exception(e)
                raise
        else:
            raise ValueError("registry is already started")

    async def stop(self):
        if self.running_task is not None:
            self.running_task.cancel()
            _logger.info("stop registry")
