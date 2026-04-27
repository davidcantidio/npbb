"""Fail fast when the runtime database is reachable but behind Alembic head."""

from __future__ import annotations

from pathlib import Path

import sqlalchemy as sa
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.exc import DBAPIError, OperationalError

from app.db.database import engine, get_database_endpoint_info


BASE_DIR = Path(__file__).resolve().parents[1]


def _head_revisions() -> list[str]:
    config = Config(str(BASE_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BASE_DIR / "alembic"))
    script_dir = ScriptDirectory.from_config(config)
    return sorted(script_dir.get_heads())


def _current_revisions(connection) -> list[str]:
    try:
        rows = connection.execute(
            sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")
        ).fetchall()
    except DBAPIError as exc:
        detail = str(getattr(exc, "orig", exc)).lower()
        if "alembic_version" in detail and (
            "does not exist" in detail or "undefined table" in detail or "no such table" in detail
        ):
            return []
        raise
    return sorted(str(row[0]) for row in rows if row and row[0])


def main() -> None:
    endpoint = get_database_endpoint_info()
    try:
        with engine.connect() as connection:
            connection.execute(sa.text("select 1"))
            current = _current_revisions(connection)
    except OperationalError as exc:
        detail = str(getattr(exc, "orig", exc)).strip()
        print(f"ERRO: banco indisponivel para o backend dev. endpoint={endpoint}")
        print(detail)
        raise SystemExit(2)

    heads = _head_revisions()
    if current != heads:
        current_display = current or ["<sem alembic_version>"]
        print(f"ERRO: schema do banco esta defasado para o backend dev. endpoint={endpoint}")
        print(f"alembic_version atual={current_display} head={heads}")
        print("Rode as migrations antes de subir a API:")
        print("  cd backend")
        print("  python -m alembic -c alembic.ini upgrade head")
        print("Se usar Supabase, mantenha DATABASE_URL para runtime e DIRECT_URL para migrations.")
        print(
            "Se a migration f1d2c3b4a5e6 falhou antes por timeout, atualize o repo e rode de novo: "
            "ela foi ajustada para backfill em lotes."
        )
        raise SystemExit(3)

    print(f"Banco acessivel e schema atualizado. endpoint={endpoint} head={heads}")


if __name__ == "__main__":
    main()
