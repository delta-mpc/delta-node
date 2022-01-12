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

    shutdown_event = asyncio.Event()

    def _signal_handler(*_: Any) -> None:
        shutdown_event.set()

    shutdown.add_handler(_signal_handler)

    await serve(app, config, shutdown_trigger=shutdown_event.wait)  # type: ignore
