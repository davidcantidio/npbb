"""Helpers de URL publicas (frontend e docs) para o sistema.

Objetivo:
- Centralizar a geracao de URLs "publicas" para o modulo de eventos.
- Evitar hardcodes em routers/servicos.
"""

from __future__ import annotations

import os
from urllib.parse import urlparse


def _first_origin(value: str | None, *, fallback: str) -> str:
    if not value:
        return fallback
    # Suporta lista separada por virgula (mesmo padrao do FRONTEND_ORIGIN).
    origin = (value.split(",")[0] or fallback).strip()
    return origin or fallback


def _normalize_base_url(raw: str) -> str:
    return (raw or "").strip().rstrip("/")


def _normalize_environment(value: str | None) -> str:
    return (value or "").strip().lower()


def is_local_hostname(hostname: str | None) -> bool:
    normalized = (hostname or "").strip().lower()
    return normalized in {"localhost", "127.0.0.1"}


def is_local_url(url: str | None) -> bool:
    parsed = urlparse((url or "").strip())
    return is_local_hostname(parsed.hostname)


def is_production_environment() -> bool:
    environment = _normalize_environment(os.getenv("ENVIRONMENT"))
    if environment == "production":
        return True

    public_app_base_url = os.getenv("PUBLIC_APP_BASE_URL")
    return bool(public_app_base_url) and not is_local_url(public_app_base_url)


def get_public_app_base_url() -> str:
    """URL base publica do app (frontend).

    Preferencia:
    1) PUBLIC_APP_BASE_URL
    2) FRONTEND_ORIGIN (primeiro origin)
    3) http://localhost:5173
    """
    base = os.getenv("PUBLIC_APP_BASE_URL")
    if base:
        return _normalize_base_url(base)

    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    return _normalize_base_url(_first_origin(frontend_origin, fallback="http://localhost:5173"))


def get_public_landing_base_url(*, backend_base_url: str | None = None) -> str:
    """URL base publica para as landings do backend.

    Preferencia:
    1) PUBLIC_LANDING_BASE_URL
    2) backend_base_url (request.base_url)
    3) PUBLIC_APP_BASE_URL (fallback tecnico)
    """
    base = os.getenv("PUBLIC_LANDING_BASE_URL")
    if base:
        return _normalize_base_url(base)
    if backend_base_url:
        return _normalize_base_url(backend_base_url)
    return get_public_app_base_url()


def build_evento_public_urls(
    evento_id: int, *, backend_base_url: str | None = None
) -> dict[str, str]:
    """Gera URLs publicas relacionadas a um evento.

    Padroes MVP:
    - landing:      {PUBLIC_APP_BASE_URL}/landing/eventos/{evento_id}
    - check-in sem QR: {PUBLIC_LANDING_BASE_URL}/checkin-sem-qr/eventos/{evento_id}
    - questionario: {PUBLIC_LANDING_BASE_URL}/questionario/eventos/{evento_id}
    - api-doc:      {backend_base_url}/docs (fallback: {PUBLIC_APP_BASE_URL}/docs)
    """
    app_base = get_public_app_base_url()
    landing_base = get_public_landing_base_url(backend_base_url=backend_base_url)

    url_landing = f"{app_base}/landing/eventos/{evento_id}"
    url_checkin_sem_qr = f"{landing_base}/checkin-sem-qr/eventos/{evento_id}"
    url_questionario = f"{landing_base}/questionario/eventos/{evento_id}"

    api_doc_override = os.getenv("PUBLIC_API_DOC_URL")
    if api_doc_override:
        url_api = api_doc_override.strip()
    else:
        base = _normalize_base_url(backend_base_url) if backend_base_url else app_base
        url_api = f"{base}/docs"

    return {
        "url_landing": url_landing,
        "url_checkin_sem_qr": url_checkin_sem_qr,
        "url_questionario": url_questionario,
        "url_api": url_api,
    }


def build_ativacao_public_urls(
    ativacao_id: int, *, backend_base_url: str | None = None
) -> dict[str, str]:
    """Gera URLs publicas relacionadas a uma ativacao.

    Padroes MVP:
    - landing/publica-promotor: {PUBLIC_APP_BASE_URL}/landing/ativacoes/{ativacao_id}
    - check-in sem QR: {PUBLIC_LANDING_BASE_URL}/checkin-sem-qr/ativacoes/{ativacao_id}
    """
    app_base = get_public_app_base_url()
    landing_base = get_public_landing_base_url(backend_base_url=backend_base_url)
    landing_url = f"{app_base}/landing/ativacoes/{ativacao_id}"
    return {
        "landing_url": landing_url,
        "url_promotor": landing_url,
        "url_checkin_sem_qr": f"{landing_base}/checkin-sem-qr/ativacoes/{ativacao_id}",
    }
