from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

from alembic import context

# Carrega .env se existir (para DATABASE_URL)
BASE_DIR = Path(__file__).resolve().parents[1]
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Ajusta path para importar app.*
sys.path.append(str(BASE_DIR))

# Importa metadata com naming_convention antes dos modelos
from app.db.metadata import SQLModel  # noqa: F401

# Importa os modelos para autogenerate
from app.models import models  # noqa: F401
from app.models import lead_batch  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata
MISSING_MIGRATION_URL_ERROR = (
    "DIRECT_URL ou DATABASE_URL precisam estar configuradas para rodar migrations."
)
INVALID_MIGRATION_URL_ERROR = (
    "Nenhuma URL valida para rodar migrations. Verifique DIRECT_URL e DATABASE_URL."
)
# Modo estrito (ALEMBIC_STRICT_DIRECT_URL=true): revalidacao Supabase usa somente
# DIRECT_URL; falha cedo se ausente. Ativado exclusivamente para provar rota usada.
# Comportamento padrao (flag ausente): prioridade DIRECT_URL -> DATABASE_URL (ISSUE-F1-01-003).
STRICT_DIRECT_URL_MISSING_ERROR = (
    "ALEMBIC_STRICT_DIRECT_URL=true exige DIRECT_URL. Configure DIRECT_URL."
)


def _is_strict_direct_url_mode() -> bool:
    return os.getenv("ALEMBIC_STRICT_DIRECT_URL", "").lower() in ("true", "1", "yes")


def get_url() -> str:
    if _is_strict_direct_url_mode():
        direct_url = os.getenv("DIRECT_URL")
        if not direct_url or not direct_url.strip():
            raise RuntimeError(STRICT_DIRECT_URL_MISSING_ERROR)
        return direct_url
    # Em Supabase, migrations/DDL devem usar conexao direta (DIRECT_URL),
    # pois o pooler pode bloquear/timeoutar em alguns ambientes.
    direct_url = os.getenv("DIRECT_URL")
    database_url = os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url
    if database_url:
        return database_url
    # Permite SQLite apenas em testes/override explicito
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING", "").lower() == "true":
        return "sqlite:///./app.db"
    raise RuntimeError(MISSING_MIGRATION_URL_ERROR)


def get_urls() -> list[str]:
    if _is_strict_direct_url_mode():
        direct_url = os.getenv("DIRECT_URL")
        if not direct_url or not direct_url.strip():
            raise RuntimeError(STRICT_DIRECT_URL_MISSING_ERROR)
        return [direct_url]
    urls: list[str] = []
    direct_url = os.getenv("DIRECT_URL")
    database_url = os.getenv("DATABASE_URL")
    if direct_url:
        urls.append(direct_url)
    if database_url and database_url not in urls:
        urls.append(database_url)
    if urls:
        return urls
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING", "").lower() == "true":
        return ["sqlite:///./app.db"]
    raise RuntimeError(MISSING_MIGRATION_URL_ERROR)


def _open_connection(configuration: dict[str, str], url: str) -> tuple[Engine, Connection]:
    configuration["sqlalchemy.url"] = url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    try:
        connection = connectable.connect()
    except Exception:
        connectable.dispose()
        raise
    return connectable, connection


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    last_error: Exception | None = None
    for url in get_urls():
        try:
            connectable, connection = _open_connection(configuration, url)
        except (ImportError, SQLAlchemyError) as e:
            last_error = e
            continue
        try:
            with connection:
                context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                )

                with context.begin_transaction():
                    context.run_migrations()
            return
        finally:
            connectable.dispose()

    if last_error:
        raise RuntimeError(INVALID_MIGRATION_URL_ERROR) from last_error


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
