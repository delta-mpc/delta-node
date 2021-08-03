import os
import sqlite3
from contextlib import contextmanager
from functools import wraps
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .. import config

__all__ = ["Base", "session_scope", "get_session", "close", "with_session", "init_db"]

_engine = create_engine(
    config.db, pool_pre_ping=True, connect_args={"check_same_thread": False}
)

_session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

Base = declarative_base(bind=_engine)


def get_session() -> Generator[Session, None, None]:
    session: Session = _session()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


session_scope = contextmanager(get_session)


def close():
    _session.close_all()
    _engine.dispose()


def with_session(f):
    @wraps(f)
    def impl(*args, **kwargs):
        session: Session = kwargs.get("session", None)
        if session is None:
            with session_scope() as session:
                kwargs["session"] = session
                return f(*args, **kwargs)
        else:
            return f(*args, **kwargs)

    return impl


def init_db():
    db_path = config.db.split(r":///", maxsplit=2)[1]
    db_name = db_path.split(r"/")[-1]
    db_dir = db_path[: -len(db_name)]

    if not os.path.exists(db_path):
        os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.close()
    Base.metadata.create_all(_engine)
