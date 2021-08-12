import uvicorn
from fastapi import FastAPI

from .node import router as node_router
from .task import router as task_router

app = FastAPI()
app.include_router(task_router)
app.include_router(node_router)

def run(host: str, port: int):
    uvicorn.run("delta_node.app:app", host=host, port=port)
