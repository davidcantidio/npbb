from __future__ import annotations

import importlib.util
import sys
import types
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.exc import ArgumentError


BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_ENV_PATH = BACKEND_DIR / "alembic" / "env.py"


class FakeAlembicConfig:
    config_file_name = None
    config_ini_section = "alembic"

    def get_section(self, _section: str, default: dict[str, str] | None = None) -> dict[str, str]:
        return {} if default is None else default.copy()


class FakeAlembicContext:
    def __init__(self) -> None:
        self.config = FakeAlembicConfig()
        self.configure_calls: list[dict[str, object]] = []
        self.run_calls = 0
        self.migration_error: Exception | None = None

    def reset(self) -> None:
        self.configure_calls.clear()
        self.run_calls = 0
        self.migration_error = None

    def is_offline_mode(self) -> bool:
        return True

    def configure(self, **kwargs: object) -> None:
        self.configure_calls.append(kwargs)

    @contextmanager
    def begin_transaction(self):
        yield

    def run_migrations(self) -> None:
        self.run_calls += 1
        if self.migration_error is not None:
            raise self.migration_error


class FakeConnection:
    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class FakeConnectable:
    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


def _load_alembic_env_module(monkeypatch: pytest.MonkeyPatch) -> tuple[object, FakeAlembicContext]:
    fake_context = FakeAlembicContext()

    app_module = types.ModuleType("app")
    app_module.__path__ = []
    db_module = types.ModuleType("app.db")
    db_module.__path__ = []
    metadata_module = types.ModuleType("app.db.metadata")
    metadata_module.SQLModel = types.SimpleNamespace(metadata=object())
    models_package = types.ModuleType("app.models")
    models_package.__path__ = []
    models_module = types.ModuleType("app.models.models")
    lead_batch_module = types.ModuleType("app.models.lead_batch")
    alembic_module = types.ModuleType("alembic")

    app_module.db = db_module
    app_module.models = models_package
    db_module.metadata = metadata_module
    models_package.models = models_module
    models_package.lead_batch = lead_batch_module
    alembic_module.context = fake_context

    monkeypatch.setitem(sys.modules, "app", app_module)
    monkeypatch.setitem(sys.modules, "app.db", db_module)
    monkeypatch.setitem(sys.modules, "app.db.metadata", metadata_module)
    monkeypatch.setitem(sys.modules, "app.models", models_package)
    monkeypatch.setitem(sys.modules, "app.models.models", models_module)
    monkeypatch.setitem(sys.modules, "app.models.lead_batch", lead_batch_module)
    monkeypatch.setitem(sys.modules, "alembic", alembic_module)

    monkeypatch.setenv("TESTING", "true")
    monkeypatch.delenv("DIRECT_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ALEMBIC_STRICT_DIRECT_URL", raising=False)

    module_name = f"test_alembic_env_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, ALEMBIC_ENV_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    fake_context.reset()
    return module, fake_context


def test_run_migrations_online_prioritizes_direct_url_and_deduplicates_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, fake_context = _load_alembic_env_module(monkeypatch)
    attempted_urls: list[str] = []

    monkeypatch.setenv("DIRECT_URL", "postgresql://direct")
    monkeypatch.setenv("DATABASE_URL", "postgresql://database")

    def fake_open(_configuration: dict[str, str], url: str) -> tuple[FakeConnectable, FakeConnection]:
        attempted_urls.append(url)
        return FakeConnectable(), FakeConnection()

    monkeypatch.setattr(module, "_open_connection", fake_open)

    module.run_migrations_online()

    assert attempted_urls == ["postgresql://direct"]
    assert fake_context.run_calls == 1

    monkeypatch.setenv("DATABASE_URL", "postgresql://direct")
    assert module.get_urls() == ["postgresql://direct"]


def test_run_migrations_online_falls_back_to_database_url_on_pre_connection_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, fake_context = _load_alembic_env_module(monkeypatch)
    attempted_urls: list[str] = []

    monkeypatch.setenv("DIRECT_URL", "postgresql://direct")
    monkeypatch.setenv("DATABASE_URL", "postgresql://database")

    def fake_open(_configuration: dict[str, str], url: str) -> tuple[FakeConnectable, FakeConnection]:
        attempted_urls.append(url)
        if url == "postgresql://direct":
            raise ArgumentError("broken direct url")
        return FakeConnectable(), FakeConnection()

    monkeypatch.setattr(module, "_open_connection", fake_open)

    module.run_migrations_online()

    assert attempted_urls == ["postgresql://direct", "postgresql://database"]
    assert fake_context.run_calls == 1


def test_run_migrations_online_raises_clear_error_when_no_valid_url_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, _ = _load_alembic_env_module(monkeypatch)
    attempted_urls: list[str] = []

    monkeypatch.setenv("DIRECT_URL", "postgresql+missing://direct")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    def fake_open(_configuration: dict[str, str], url: str) -> tuple[FakeConnectable, FakeConnection]:
        attempted_urls.append(url)
        raise ArgumentError("driver missing")

    monkeypatch.setattr(module, "_open_connection", fake_open)

    with pytest.raises(RuntimeError, match="Nenhuma URL valida para rodar migrations") as excinfo:
        module.run_migrations_online()

    assert attempted_urls == ["postgresql+missing://direct"]
    assert isinstance(excinfo.value.__cause__, ArgumentError)


def test_run_migrations_online_propagates_migration_error_without_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, fake_context = _load_alembic_env_module(monkeypatch)
    attempted_urls: list[str] = []

    monkeypatch.setenv("DIRECT_URL", "postgresql://direct")
    monkeypatch.setenv("DATABASE_URL", "postgresql://database")
    fake_context.migration_error = RuntimeError("migration failed")

    def fake_open(_configuration: dict[str, str], url: str) -> tuple[FakeConnectable, FakeConnection]:
        attempted_urls.append(url)
        return FakeConnectable(), FakeConnection()

    monkeypatch.setattr(module, "_open_connection", fake_open)

    with pytest.raises(RuntimeError, match="migration failed"):
        module.run_migrations_online()

    assert attempted_urls == ["postgresql://direct"]
    assert fake_context.run_calls == 1


def test_get_urls_requires_explicit_urls_outside_test_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, _ = _load_alembic_env_module(monkeypatch)

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("DIRECT_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DIRECT_URL ou DATABASE_URL precisam estar configuradas"):
        module.get_urls()


def test_strict_mode_exposes_only_direct_url_ignores_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, fake_context = _load_alembic_env_module(monkeypatch)
    attempted_urls: list[str] = []

    monkeypatch.setenv("ALEMBIC_STRICT_DIRECT_URL", "true")
    monkeypatch.setenv("DIRECT_URL", "postgresql://direct")
    monkeypatch.setenv("DATABASE_URL", "postgresql://database")

    def fake_open(_configuration: dict[str, str], url: str) -> tuple[FakeConnectable, FakeConnection]:
        attempted_urls.append(url)
        return FakeConnectable(), FakeConnection()

    monkeypatch.setattr(module, "_open_connection", fake_open)

    module.run_migrations_online()

    assert attempted_urls == ["postgresql://direct"]
    assert fake_context.run_calls == 1
    assert module.get_urls() == ["postgresql://direct"]


def test_strict_mode_fails_early_when_direct_url_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, _ = _load_alembic_env_module(monkeypatch)

    monkeypatch.setenv("ALEMBIC_STRICT_DIRECT_URL", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql://database")
    monkeypatch.delenv("DIRECT_URL", raising=False)

    with pytest.raises(RuntimeError, match="ALEMBIC_STRICT_DIRECT_URL=true exige DIRECT_URL"):
        module.get_urls()
