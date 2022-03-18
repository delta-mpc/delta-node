from typing import Optional

from .monitor import start


async def run(timeout: Optional[int] = None, retry_attemps: Optional[int] = None):
    await start(timeout=timeout, retry_attemps=retry_attemps)
