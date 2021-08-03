import uvicorn
from fastapi import FastAPI

from . import controller, config, db

app = FastAPI()
app.include_router(controller.node_router)
app.include_router(controller.task_router)
app.include_router(controller.task_member_router)
app.include_router(controller.round_router)
app.include_router(controller.pub_key_router)
app.include_router(controller.event_router, prefix="/event")


def main():
    db.init_db()
    uvicorn.run("monkey_chain.app:app", host=config.host, port=config.port)
