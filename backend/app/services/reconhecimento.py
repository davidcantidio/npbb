"""Servicos para reconhecimento de leads por token opaco."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Response
from sqlmodel import Session, select

from app.models.models import LeadReconhecimentoToken, now_utc

LEAD_RECOGNITION_COOKIE_NAME = "lp_lead_token"
LEAD_RECOGNITION_TTL_DAYS = 7
LEAD_RECOGNITION_COOKIE_MAX_AGE_SECONDS = LEAD_RECOGNITION_TTL_DAYS * 24 * 60 * 60


def _cookie_secure() -> bool:
    env = os.getenv("COOKIE_SECURE")
    if env is not None:
        return env.lower() in {"1", "true", "yes"}
    return os.getenv("ENV", "").lower() in {"prod", "production"}


def _normalize_utc(dt: datetime) -> datetime:
    if getattr(dt, "tzinfo", None) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _hash_token(token: str) -> str:
    secret = os.getenv("SECRET_KEY") or ""
    token_bytes = (token or "").strip().encode("utf-8")
    if secret:
        return hmac.new(secret.encode("utf-8"), token_bytes, hashlib.sha256).hexdigest()
    return hashlib.sha256(token_bytes).hexdigest()


@dataclass(frozen=True)
class LeadRecognitionResult:
    lead_id: int
    evento_id: int
    expires_at: datetime


def gerar_token(session: Session, *, lead_id: int, evento_id: int) -> str:
    token = secrets.token_urlsafe(32)
    session.add(
        LeadReconhecimentoToken(
            token_hash=_hash_token(token),
            lead_id=lead_id,
            evento_id=evento_id,
            expires_at=now_utc() + timedelta(days=LEAD_RECOGNITION_TTL_DAYS),
        )
    )
    session.flush()
    return token


def validar_token(
    session: Session,
    *,
    token: str,
    evento_id: int,
) -> LeadRecognitionResult | None:
    token_norm = (token or "").strip()
    if not token_norm:
        return None

    record = session.exec(
        select(LeadReconhecimentoToken).where(
            LeadReconhecimentoToken.token_hash == _hash_token(token_norm)
        )
    ).first()
    if record is None:
        return None
    if record.evento_id != evento_id:
        return None
    if _normalize_utc(record.expires_at) <= _normalize_utc(now_utc()):
        return None

    return LeadRecognitionResult(
        lead_id=record.lead_id,
        evento_id=record.evento_id,
        expires_at=record.expires_at,
    )


def set_lead_recognition_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=LEAD_RECOGNITION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=LEAD_RECOGNITION_COOKIE_MAX_AGE_SECONDS,
        path="/",
    )
