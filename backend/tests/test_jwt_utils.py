import os
import time

import jwt
import pytest

from app.utils.jwt import create_access_token, decode_token


def test_create_and_decode_access_token(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1")

    payload = {"sub": "user@example.com"}
    token = create_access_token(payload)

    decoded = decode_token(token)
    assert decoded["sub"] == payload["sub"]
    assert "exp" in decoded


def test_expired_token_raises(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    token = create_access_token({"sub": "x"}, expires_minutes=-1)

    time.sleep(1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)


def test_missing_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValueError):
        create_access_token({"sub": "x"})
