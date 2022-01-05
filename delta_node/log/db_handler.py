import asyncio
from logging import Handler, LogRecord

from delta_node import db, entity


async def write_log_record(record: entity.Record):
    async with db.session_scope() as sess:
        sess.add(record)
        await sess.commit()


class DBWriteHandler(Handler):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super(DBWriteHandler, self).__init__()
        self.loop = loop

    def emit(self, record: LogRecord) -> None:
        if hasattr(record, "task_id"):
            task_id = getattr(record, "task_id")
            level = record.levelname
        
            tx_hash = getattr(record, "tx_hash", None)
            log = entity.Record(level=level, message=record.message, task_id=task_id, tx_hash=tx_hash)
            asyncio.run_coroutine_threadsafe(write_log_record(log), self.loop)
