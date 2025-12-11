"""Utilitários para geração e validação de tokens JWT (HS256)."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt


def _get_secret_key() -> str:
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise ValueError("SECRET_KEY não configurada no ambiente.")
    return secret


def _get_default_exp_minutes() -> int:
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(data: Dict[str, Any], expires_minutes: int | None = None) -> str:
    """Cria um JWT assinado com HS256.

    Args:
        data: payload a ser incluído (será copiado para evitar mutação externa).
        expires_minutes: tempo de expiração; se None, usa ACCESS_TOKEN_EXPIRE_MINUTES do ambiente.
    """
    to_encode = data.copy()
    exp_minutes = expires_minutes or _get_default_exp_minutes()
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _get_secret_key(), algorithm="HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica e valida um JWT assinado com HS256, retornando o payload."""
    return jwt.decode(token, _get_secret_key(), algorithms=["HS256"])
