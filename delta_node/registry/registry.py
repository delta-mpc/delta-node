import asyncio
import logging
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.exc import NoResultFound
from async_lru import alru_cache
from delta_node import config, db
from delta_node.entity.identity import Node
from delta_node.chain import identity

__all__ = ["register", "get_node_address", "unregister"]


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


async def register(
    url: str = config.node_url,
    name: str = config.node_name,
):
    async with db.session_scope() as sess:
        q = sa.select(Node).where(Node.id == 1)
        node: Optional[Node] = (await sess.execute(q)).scalars().one_or_none()

        if node:
            # join first to avoid address changed when connect to monkey chain connector
            await identity.get_client().join(url, name)
            updated = False
            if node.url != url:
                await identity.get_client().updaet_url(node.address, url)
                node.url = url
                updated = True
            if node.name != name:
                await identity.get_client().update_name(node.address, name)
                node.name = name
                updated = True
            if updated:
                sess.add(node)
                await sess.commit()
            _logger.info(f"registered node, node address: {node.address}")

        else:
            _, address = await identity.get_client().join(url, name)
            node = Node(url=url, name=name, address=address)
            sess.add(node)
            await sess.commit()
            await sess.refresh(node)
            _logger.info(f"register new node, node address: {node.address}")


async def unregister():
    address = await get_node_address()
    await identity.get_client().leave(address)

    async with db.session_scope() as sess:
        q = sa.select(Node).where(Node.id == 1)
        node = (await sess.execute(q)).scalar_one()

        await sess.delete(node)
        await sess.commit()

    _logger.info(f"node {address} leave")
