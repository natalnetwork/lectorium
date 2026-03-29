from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

BASE_DIR: Path = Path(__file__).resolve().parents[2]
DB_PATH: Path = BASE_DIR / "data" / "db" / "lectorium.db"


class Base(DeclarativeBase):
    pass


def _make_engine(path: Path) -> Engine:
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )


engine: Engine = _make_engine(DB_PATH)


def init_db() -> None:
    # Import to register ORM classes with Base before create_all
    from backend.app.models import db_models as _  # noqa: F401

    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
