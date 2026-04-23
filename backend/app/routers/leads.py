"""Aggregador fino das rotas de leads."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.landing_public import LandingSubmitResponse
from app.schemas.lead_list import LeadListQuery, LeadListResponse
from app.services.imports.file_reader import read_raw_file_preview  # noqa: F401 - compatibilidade com testes
from app.services.lead_pipeline_service import (  # noqa: F401 - compatibilidade com harness legado de testes
    executar_pipeline_gold_em_thread,
    load_batch_without_bronze_for_update,
    queue_pipeline_batch,
)

from .leads_routes import _shared
from .leads_routes.batches import (
    disparar_pipeline,
    router as batches_router,
)
from .leads_routes.classic_import import router as classic_import_router
from .leads_routes.etl_import import _map_etl_import_error, router as etl_import_router
from .leads_routes.lead_records import (
    _configure_listar_leads_statement_timeout,
    listar_leads,
    router as lead_records_router,
)
from .leads_routes.public_intake import (
    criar_lead_publico,
    reconhecer_lead_publico,
    router as public_intake_router,
)
from .leads_routes.references import router as references_router

router = APIRouter(prefix="/leads", tags=["leads"])

# Rotas raiz adicionadas diretamente para evitar conflito entre prefixo e path vazio.
router.add_api_route(
    "",
    criar_lead_publico,
    methods=["POST"],
    response_model=LandingSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/",
    criar_lead_publico,
    methods=["POST"],
    response_model=LandingSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
router.add_api_route(
    "",
    listar_leads,
    methods=["GET"],
    response_model=LeadListResponse,
)
router.add_api_route(
    "/",
    listar_leads,
    methods=["GET"],
    response_model=LeadListResponse,
)

# Ordem mantida do router legado: captura publica, registros, referencias, importacao, ETL, batches.
router.include_router(public_intake_router, prefix="")
router.include_router(lead_records_router, prefix="")
router.include_router(references_router, prefix="")
router.include_router(classic_import_router, prefix="")
router.include_router(etl_import_router, prefix="")
router.include_router(batches_router, prefix="")

__all__ = [
    "LeadListQuery",
    "_configure_listar_leads_statement_timeout",
    "_map_etl_import_error",
    "_shared",
    "disparar_pipeline",
    "executar_pipeline_gold_em_thread",
    "load_batch_without_bronze_for_update",
    "queue_pipeline_batch",
    "read_raw_file_preview",
    "reconhecer_lead_publico",
    "router",
]
