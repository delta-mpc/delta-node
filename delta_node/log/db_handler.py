from logging import LogRecord, Handler
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Tuple

from .. import db
from ..model import Log


class DBWriteHandler(Handler):
    def __init__(self):
        super(DBWriteHandler, self).__init__()

    def emit(self, record: LogRecord) -> None:
        with db.session_scope() as session:
            if hasattr(record, "task_id"):
                task_id = getattr(record, "task_id")
                created_at = int(record.created * 1000)
                level = record.levelname

                log = Log(
                    created_at=created_at,
                    level=level,
                    task_id=task_id,
                    message=record.message,
                )

                session.add(log)
                session.commit()

handler = DBWriteHandler()
