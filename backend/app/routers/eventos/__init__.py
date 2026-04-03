"""Pacote de rotas de eventos (CRUD, dicionários, formulário, gamificação, ativações)."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.evento import EventoListItem, EventoRead

from . import _shared
from .ativacoes import router as ativacoes_router
from .crud import (
    atualizar_evento,
    criar_evento,
    excluir_evento,
    listar_eventos,
    obter_evento,
    router as crud_router,
)
from .csv import router as csv_router
from .dicionarios import router as dicionarios_router
from .form_config import router as form_config_router
from .gamificacoes import router as gamificacoes_router
from .landing import router as landing_router
from .questionario import router as questionario_router

router = APIRouter(prefix="/evento", tags=["evento"])

# Rotas raiz ("" e "/") adicionadas diretamente para evitar "Prefix and path cannot be both empty"
router.add_api_route("", listar_eventos, methods=["GET"], response_model=list[EventoListItem])
router.add_api_route("/", listar_eventos, methods=["GET"], response_model=list[EventoListItem])
router.add_api_route("", criar_evento, methods=["POST"], response_model=EventoRead, status_code=201)
router.add_api_route("/", criar_evento, methods=["POST"], response_model=EventoRead, status_code=201)

# Ordem: rotas mais específicas primeiro
router.include_router(csv_router, prefix="")
router.include_router(dicionarios_router, prefix="")
router.include_router(form_config_router, prefix="")
router.include_router(questionario_router, prefix="")
router.include_router(gamificacoes_router, prefix="")
router.include_router(ativacoes_router, prefix="")
router.include_router(landing_router, prefix="")
router.include_router(crud_router, prefix="")

__all__ = [
    "router",
    "_shared",
    "atualizar_evento",
    "excluir_evento",
    "obter_evento",
]
