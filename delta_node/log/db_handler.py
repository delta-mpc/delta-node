import asyncio
from logging import Handler, LogRecord

from delta_node import db, entity


async def write_log_record(record: entity.Record):
    async with db.session_scope() as sess:
        sess.add(record)
        await sess.commit()


class DBWriteHandler(Handler):
    def __init__(self):
        super(DBWriteHandler, self).__init__()

    def emit(self, record: LogRecord) -> None:
        if hasattr(record, "task_id"):
            task_id = getattr(record, "task_id")
            level = record.levelname

            log = entity.Record(level=level, message=record.message, task_id=task_id)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(write_log_record(log))


handler = DBWriteHandler()
