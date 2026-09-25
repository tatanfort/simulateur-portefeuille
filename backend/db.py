"""Database setup. Defaults to a local SQLite file for development; set the
DATABASE_URL environment variable (e.g. a managed Postgres connection
string) in production so data survives redeploys on hosts with an
ephemeral filesystem.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATA_DIR / 'app.db'}")

# Some providers (Heroku-style) hand out "postgres://" URLs, which older
# SQLAlchemy releases reject — normalize to the "postgresql://" scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_lightweight_migrations():
    """`Base.metadata.create_all` only creates missing TABLES, never adds
    columns to a table that already exists - so an already-deployed database
    needs its `users` table patched by hand whenever a column is added to
    the model. No Alembic here (overkill for a personal project); just a
    small idempotent ALTER TABLE runner, safe to call on every startup.
    """
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return  # fresh DB - create_all() already created it with every column
    existing = {c["name"] for c in insp.get_columns("users")}
    new_columns = {
        "email_verified": "BOOLEAN DEFAULT FALSE",
        "verification_token": "VARCHAR",
        "verification_token_expires": "TIMESTAMP",
        "reset_token": "VARCHAR",
        "reset_token_expires": "TIMESTAMP",
    }
    with engine.begin() as conn:
        for name, ddl_type in new_columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl_type}"))
