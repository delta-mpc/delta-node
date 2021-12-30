from fastapi import FastAPI
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio

from .v1 import router as v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/v1")


async def run(host: str, port: int):
    config = Config()
    config.bind = [f"{host}:{port}"]
    config.accesslog = "-"

    await serve(app, config, shutdown_trigger=lambda: asyncio.Future())  # type: ignore
