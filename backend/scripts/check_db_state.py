"""Check DB state: alembic_version + key ENUM types."""
import os
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _database_url() -> str:
    direct = (os.getenv("DIRECT_URL") or "").strip()
    if direct:
        return direct
    db = (os.getenv("DATABASE_URL") or "").strip()
    if db:
        return db
    raise SystemExit(
        "Defina DIRECT_URL ou DATABASE_URL em backend/.env. "
        "Se a porta 6543 (transaction pooler) der timeout, use a URL com :5432 no host do pooler."
    )


URL = _database_url()
connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "15"))
connect_args: dict = {"connect_timeout": connect_timeout}
if "sslmode=" not in URL and "ssl=require" not in URL:
    connect_args["sslmode"] = "require"

engine = sa.create_engine(URL, connect_args=connect_args)

with engine.connect() as conn:
    avrows = conn.execute(
        sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")
    ).fetchall()
    print("alembic_version:", [r[0] for r in avrows])

    enum_query = sa.text(
        "SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname"
    )
    enums = conn.execute(enum_query).fetchall()
    print("ENUMs:", [r[0] for r in enums])
