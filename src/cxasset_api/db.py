from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from cxasset_api.config import settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    db_path = database_url.replace("sqlite:///", "", 1)
    if db_path.startswith("./") or db_path.startswith(".\\"):
        resolved = (Path.cwd() / db_path[2:]).resolve()
    else:
        resolved = Path(db_path).resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent(settings.database_url)


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
