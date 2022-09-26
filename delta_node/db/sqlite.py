from __future__ import annotations

import os
import threading
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from delta_node import config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import registry, sessionmaker

__all__ = ["session_scope", "init", "close", "mapper_registry", "get_session"]

_local = threading.local()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if (not hasattr(_local, "session")) or (not hasattr(_local, "engine")):
        raise ValueError("db has not been initialized")
    session: sessionmaker = _local.session
    async with session() as sess:
        try:
            yield sess
        except:
            await sess.rollback()
            raise


session_scope = asynccontextmanager(get_session)

mapper_registry: registry = registry()


async def init(db: str = config.db):
    if hasattr(_local, "session") or hasattr(_local, "engine"):
        raise ValueError("db has been initialized")

    engine = create_async_engine(
        db,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
        # echo=True,
    )
    session = sessionmaker(
        engine,
        class_=AsyncSession,  # type: ignore
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    paths = db.split("://", maxsplit=1)
    if len(paths) == 2 and len(paths[1]) > 0:
        path = paths[1].split(r"/", maxsplit=1)[1]

        filename = path.split(r"/")[-1]
        dirname = path[: -len(filename)]

        if not os.path.exists(path):
            if len(dirname) > 0:
                os.makedirs(dirname, exist_ok=True)

            async with engine.begin() as conn:
                await conn.run_sync(mapper_registry.metadata.create_all)
    else:
        async with engine.begin() as conn:
            await conn.run_sync(mapper_registry.metadata.create_all)

    _local.engine = engine
    _local.session = session


async def close():
    if (not hasattr(_local, "session")) or (not hasattr(_local, "engine")):
        raise ValueError("db has not been initialized")

    engine: AsyncEngine = _local.engine
    await engine.dispose()

    delattr(_local, "engine")
    delattr(_local, "session")
