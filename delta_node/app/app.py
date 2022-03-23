import asyncio
from typing import Any

from delta_node import shutdown
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

from .v1 import router as v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/v1")


async def run(host: str, port: int):
    config = Config()
    config.bind = [f"{host}:{port}"]
    config.accesslog = "-"
    config.errorlog = "-"

    shutdown_event = asyncio.Event()

    try:
        await serve(app, config, shutdown_trigger=shutdown_event.wait)  # type: ignore
    except asyncio.CancelledError:
        shutdown_event.set()
