"""Servicos de recuperacao de senha (forgot/reset).

- Gera token seguro e persiste apenas o hash no banco.
- Envia email com link contendo o token.
- Valida expiracao e uso unico do token.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from app.db.database import set_internal_service_db_context
from app.models.models import PasswordResetToken, Usuario
from app.services.email import send_email


def _now_utc() -> datetime:
    # Mantemos datas em UTC "naive" (sem tzinfo) para compatibilidade com colunas
    # DateTime sem timezone no banco (SQLite/Postgres).
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None) if getattr(dt, "tzinfo", None) is not None else dt


def _get_expire_minutes() -> int:
    raw = os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "60").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 60
    return max(5, value)


def _is_debug_enabled() -> bool:
    return os.getenv("PASSWORD_RESET_DEBUG", "false").lower() == "true"


def _hash_token(token: str) -> str:
    secret = os.getenv("PASSWORD_RESET_TOKEN_SECRET") or os.getenv("SECRET_KEY") or ""
    token_bytes = (token or "").encode("utf-8")
    if secret:
        return hmac.new(secret.encode("utf-8"), token_bytes, hashlib.sha256).hexdigest()
    return hashlib.sha256(token_bytes).hexdigest()


def _build_reset_url(token: str) -> str:
    base = os.getenv("PASSWORD_RESET_URL")
    if not base:
        frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        first_origin = (frontend_origin.split(",")[0] or "http://localhost:5173").strip()
        base = first_origin.rstrip("/") + "/reset-password"
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}token={token}"


def generate_token() -> str:
    return secrets.token_urlsafe(32)


@dataclass(frozen=True)
class PasswordResetRequestResult:
    user_found: bool
    debug_token: str | None = None
    debug_expires_at: datetime | None = None
    debug_reset_url: str | None = None


class PasswordResetError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def request_password_reset(session: Session, email: str) -> PasswordResetRequestResult:
    """Registra e envia token de recuperacao (se usuario existir/ativo).

    Por boas praticas, este metodo nao informa se o usuario existe.
    """
    set_internal_service_db_context(session)
    email_norm = (email or "").strip().lower()
    usuario = session.exec(select(Usuario).where(func.lower(Usuario.email) == email_norm)).first()
    if not usuario or not usuario.ativo:
        return PasswordResetRequestResult(user_found=False)

    token = generate_token()
    token_hash = _hash_token(token)
    now = _now_utc()
    expires_at = now + timedelta(minutes=_get_expire_minutes())

    record = PasswordResetToken(
        usuario_id=usuario.id,
        token_hash=token_hash,
        created_at=now,
        sent_at=now,
        expires_at=expires_at,
        used_at=None,
    )
    session.add(record)
    session.commit()

    reset_url = _build_reset_url(token)
    body = (
        "Voce solicitou a recuperacao de senha.\n\n"
        f"Use o link para redefinir sua senha:\n{reset_url}\n\n"
        f"Este link expira em {_get_expire_minutes()} minutos."
    )
    send_email(to=usuario.email, subject="Recuperacao de senha", body=body)

    if _is_debug_enabled():
        return PasswordResetRequestResult(
            user_found=True,
            debug_token=token,
            debug_expires_at=expires_at,
            debug_reset_url=reset_url,
        )
    return PasswordResetRequestResult(user_found=True)


def reset_password(session: Session, token: str, new_password_hash: str) -> None:
    """Consome um token valido e atualiza a senha do usuario."""
    set_internal_service_db_context(session)
    token_norm = (token or "").strip()
    if not token_norm:
        raise PasswordResetError("TOKEN_INVALID", "Token invalido")

    token_hash = _hash_token(token_norm)
    record = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    ).first()
    if not record:
        raise PasswordResetError("TOKEN_INVALID", "Token invalido")

    now = _now_utc()
    if record.used_at is not None:
        raise PasswordResetError("TOKEN_USED", "Token ja utilizado")
    if _as_naive(record.expires_at) <= now:
        raise PasswordResetError("TOKEN_EXPIRED", "Token expirado")

    usuario = session.get(Usuario, record.usuario_id)
    if not usuario or not usuario.ativo:
        raise PasswordResetError("USER_NOT_FOUND", "Usuario invalido")

    usuario.password_hash = new_password_hash
    usuario.updated_at = now

    record.used_at = now
    session.add(record)

    # Invalida outros tokens pendentes do mesmo usuario (boa pratica).
    others = session.exec(
        select(PasswordResetToken).where(
            (PasswordResetToken.usuario_id == usuario.id)
            & (PasswordResetToken.used_at.is_(None))
            & (PasswordResetToken.id != record.id)
        )
    ).all()
    for other in others:
        other.used_at = now
        session.add(other)

    session.add(usuario)
    session.commit()
