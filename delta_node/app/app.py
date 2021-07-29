from fastapi import FastAPI
import uvicorn

from .task import router as task_router

app = FastAPI()
app.include_router(task_router)


def run(host: str, port: int):
    uvicorn.run("delta_node.app:app", host=host, port=port)
