from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from database.connection import engine

_session_factory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


@contextmanager
def get_session():
    session = _session_factory()

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
