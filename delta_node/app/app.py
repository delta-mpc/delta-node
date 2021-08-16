import uvicorn
from fastapi import FastAPI

from .v1 import router as v1_router

app = FastAPI()
app.include_router(v1_router)


def run(host: str, port: int):
    uvicorn.run("delta_node.app:app", host=host, port=port)
