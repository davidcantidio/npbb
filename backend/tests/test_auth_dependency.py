import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from app.core.auth import get_current_user
from app.models.models import Usuario
from app.utils.jwt import create_access_token


# test
def make_engine():
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})


@pytest.fixture
def session(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def user(session):
    usuario = Usuario(
        email="user@example.com",
        password_hash="hashed",
        tipo_usuario="bb",
        ativo=True,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def test_get_current_user_success(monkeypatch, session, user):
    token = create_access_token({"sub": user.id}, expires_minutes=5)

    def fake_get_session():
        yield session

    monkeypatch.setattr("app.core.auth.get_session", fake_get_session)
    result = get_current_user(token=token, session=session)
    assert result.id == user.id
    assert result.email == user.email


def test_get_current_user_invalid_token(monkeypatch, session):
    invalid_token = "invalid.token.value"

    def fake_get_session():
        yield session

    monkeypatch.setattr("app.core.auth.get_session", fake_get_session)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=invalid_token, session=session)
    assert exc.value.status_code == 401


def test_get_current_user_inactive_user(monkeypatch, session):
    usuario = Usuario(
        email="inactive@example.com",
        password_hash="hashed",
        tipo_usuario="bb",
        ativo=False,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    token = create_access_token({"sub": usuario.id}, expires_minutes=5)

    def fake_get_session():
        yield session

    monkeypatch.setattr("app.core.auth.get_session", fake_get_session)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, session=session)
    assert exc.value.status_code == 401


def test_get_current_user_missing_user(monkeypatch, session):
    token = create_access_token({"sub": 9999}, expires_minutes=5)

    def fake_get_session():
        yield session

    monkeypatch.setattr("app.core.auth.get_session", fake_get_session)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, session=session)
    assert exc.value.status_code == 401
