from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_diary_columns(eng: Engine) -> None:
    """补齐旧库中缺失的 diaries 列（create_all 不会 ALTER 已有表）。"""
    insp = inspect(eng)
    if "diaries" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("diaries")}
    with eng.begin() as conn:
        if "axiang_observation" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE diaries ADD COLUMN axiang_observation TEXT NOT NULL DEFAULT ('')"
                )
            )
        if "daily_ritual" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE diaries ADD COLUMN daily_ritual TEXT NOT NULL DEFAULT ('')"
                )
            )


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
