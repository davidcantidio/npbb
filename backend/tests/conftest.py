"""Shared backend test fixtures."""

from __future__ import annotations

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture
def test_engine(monkeypatch):
    """Provide isolated in-memory engine and auth secret."""
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_engine):
    """Yield database session bound to shared isolated test engine."""
    with Session(test_engine) as session:
        yield session
