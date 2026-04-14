"""Regressão: pool resiliente com Postgres (Supabase / PgBouncer)."""

from app.db.database import _pool_kwargs_for_url


def test_pool_kwargs_sqlite_empty():
    assert _pool_kwargs_for_url("sqlite:///./x.db") == {}


def test_pool_kwargs_postgres_has_pre_ping_and_recycle(monkeypatch):
    monkeypatch.setenv("DB_POOL_RECYCLE", "120")
    got = _pool_kwargs_for_url("postgresql+psycopg2://u:p@h:6543/db")
    assert got["pool_pre_ping"] is True
    assert got["pool_recycle"] == 120
