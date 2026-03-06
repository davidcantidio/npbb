"""Rotas alternativas para acesso via promotor sem leitura de QR."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.utils.urls import build_ativacao_public_urls, build_evento_public_urls

router = APIRouter(tags=["landing-public"])


@router.get("/checkin-sem-qr/eventos/{evento_id}")
def redirect_evento_checkin_sem_qr(evento_id: int, request: Request):
    urls = build_evento_public_urls(evento_id, backend_base_url=str(request.base_url))
    return RedirectResponse(url=urls["url_landing"], status_code=307)


@router.get("/checkin-sem-qr/ativacoes/{ativacao_id}")
def redirect_ativacao_checkin_sem_qr(ativacao_id: int, request: Request):
    urls = build_ativacao_public_urls(ativacao_id, backend_base_url=str(request.base_url))
    return RedirectResponse(url=urls["landing_url"], status_code=307)
