"""Sprint 1, Sprint 2, Sprint 3 and Sprint 4 smart-ingestion endpoints.

This router exposes traceable contracts for incremental delivery:
- Sprint 1: scaffold validation (`/s1/scaffold`) and upload intake (`/s1/upload`);
- Sprint 2: scaffold validation (`/s2/scaffold`) and batch upload intake
  (`/s2/lote/upload`).
- Sprint 3: scaffold validation and main monitoring/reprocessing flow
  (`/s3/scaffold`, `/s3/status`, `/s3/reprocessar`).
- Sprint 4: final UX scaffold for actionable messages and accessibility
  (`/s4/scaffold`, `/s4/ux`).
"""

from __future__ import annotations

import importlib
import logging
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Evento, Usuario, UsuarioTipo
from app.utils.log_sanitize import sanitize_exception


router = APIRouter(prefix="/internal/ingestao-inteligente", tags=["internal"])
telemetry_logger = logging.getLogger("app.telemetry")
s1_telemetry = importlib.import_module(
    "app.services.interface-de-ingest-o-inteligente-frontend-_telemetry"
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_BATCH_FILES = 100
MAX_BATCH_BYTES = 300 * 1024 * 1024
MAX_REPROCESS_ATTEMPTS = 5
DEFAULT_STATUS_POLL_INTERVAL_SECONDS = 30
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
S2_BATCH_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,79}$")
S3_LOTE_UPLOAD_ID_RE = re.compile(r"^lot-[a-z0-9]{6,64}$")
S3_ALLOWED_PROCESSING_STATUSES = (
    "queued",
    "processing",
    "completed",
    "failed",
    "partial_success",
    "cancelled",
)
S3_REPROCESSABLE_STATUSES = {"failed", "partial_success"}
S3_TERMINAL_STATUSES = {"completed", "failed", "partial_success", "cancelled"}
S4_ALLOWED_NEXT_ACTIONS = (
    "monitorar_status_lote",
    "avaliar_reprocessamento_lote",
    "consultar_resultado_final_lote",
)

EXPECTED_CONTENT_TYPE_BY_EXTENSION: dict[str, str] = {
    ".csv": "text/csv",
    ".pdf": "application/pdf",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
ACCEPTED_CONTENT_TYPES = tuple(sorted(EXPECTED_CONTENT_TYPE_BY_EXTENSION.values()))


class S1PayloadBase(BaseModel):
    """Base input contract for Sprint 1 upload metadata."""

    evento_id: int = Field(gt=0)
    nome_arquivo: str = Field(min_length=1, max_length=255)
    tamanho_arquivo_bytes: int = Field(gt=0)
    content_type: str = Field(min_length=3, max_length=120)
    correlation_id: str | None = Field(default=None, min_length=6, max_length=64)


class S1ScaffoldRequest(S1PayloadBase):
    """Input contract for Sprint 1 scaffold endpoint."""


class S1UploadRequest(S1PayloadBase):
    """Input contract for Sprint 1 upload endpoint."""

    checksum_sha256: str | None = Field(default=None, min_length=1, max_length=128)


class S2FileMetadataWrite(BaseModel):
    """Input file metadata for Sprint 2 batch scaffold endpoint."""

    nome_arquivo: str = Field(min_length=1, max_length=255)
    tamanho_arquivo_bytes: int = Field(gt=0)
    content_type: str = Field(min_length=3, max_length=120)
    checksum_sha256: str | None = Field(default=None, min_length=1, max_length=128)


class S2ScaffoldRequest(BaseModel):
    """Input contract for Sprint 2 scaffold endpoint."""

    evento_id: int = Field(gt=0)
    lote_id: str = Field(min_length=3, max_length=80)
    lote_nome: str = Field(min_length=3, max_length=120)
    origem_lote: str = Field(min_length=3, max_length=120)
    total_arquivos_lote: int = Field(gt=0, le=MAX_BATCH_FILES)
    total_bytes_lote: int = Field(gt=0, le=MAX_BATCH_BYTES)
    total_registros_estimados: int = Field(ge=0)
    arquivos: list[S2FileMetadataWrite] = Field(min_length=1, max_length=MAX_BATCH_FILES)
    correlation_id: str | None = Field(default=None, min_length=6, max_length=64)


class S2LoteUploadRequest(S2ScaffoldRequest):
    """Input contract for Sprint 2 batch upload intake endpoint."""


class S3ScaffoldRequest(BaseModel):
    """Input contract for Sprint 3 scaffold endpoint."""

    evento_id: int = Field(gt=0)
    lote_id: str = Field(min_length=3, max_length=80)
    lote_upload_id: str = Field(min_length=6, max_length=80)
    status_processamento: str = Field(min_length=3, max_length=40)
    tentativas_reprocessamento: int = Field(ge=0)
    reprocessamento_habilitado: bool = True
    correlation_id: str | None = Field(default=None, min_length=6, max_length=64)


class S3StatusRequest(S3ScaffoldRequest):
    """Input contract for Sprint 3 status monitoring endpoint."""


class S3ReprocessRequest(S3ScaffoldRequest):
    """Input contract for Sprint 3 reprocessing endpoint."""

    motivo_reprocessamento: str = Field(min_length=3, max_length=240)


class S4ScaffoldRequest(S3ScaffoldRequest):
    """Input contract for Sprint 4 final UX scaffold endpoint."""

    proxima_acao: str = Field(min_length=3, max_length=80)
    leitor_tela_ativo: bool = False
    alto_contraste_ativo: bool = False
    reduzir_movimento: bool = False


class S4UXRequest(S4ScaffoldRequest):
    """Input contract for Sprint 4 final UX endpoint."""


class UploadLimitsRead(BaseModel):
    """Read model with upload limits consumed by UI."""

    tamanho_maximo_bytes: int
    content_types_aceitos: list[str]


class S1ScaffoldResponse(BaseModel):
    """Output contract for Sprint 1 scaffold endpoint."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    limites_upload: UploadLimitsRead
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


class BatchLimitsRead(BaseModel):
    """Read model with batch limits consumed by Sprint 2 UI flow."""

    max_arquivos_lote: int
    max_bytes_lote: int
    max_upload_bytes_por_arquivo: int
    content_types_aceitos: list[str]


class BatchReceptionRead(BaseModel):
    """Read model with received batch metadata summary."""

    total_arquivos_lote: int
    total_bytes_lote: int
    total_registros_estimados: int


class S2ScaffoldResponse(BaseModel):
    """Output contract for Sprint 2 scaffold endpoint."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    proxima_acao: str
    limites_lote: BatchLimitsRead
    pontos_integracao: dict[str, str]
    recepcao_lote: BatchReceptionRead
    observabilidade: dict[str, str]


class S2LoteUploadResponse(BaseModel):
    """Output contract for Sprint 2 batch upload intake endpoint."""

    contrato_versao: str
    correlation_id: str
    lote_upload_id: str
    status: str
    evento_id: int
    lote_id: str
    recepcao_lote: BatchReceptionRead
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


class ReprocessingLimitsRead(BaseModel):
    """Read model with reprocessing limits consumed by Sprint 3 UI flow."""

    max_tentativas_reprocessamento: int
    status_reprocessaveis: list[str]


class StatusMonitoringRead(BaseModel):
    """Read model with current status and monitoring instructions."""

    status_atual: str
    status_terminal: list[str]
    polling_interval_seconds: int
    tentativas_reprocessamento: int
    reprocessamento_habilitado: bool


class S3ScaffoldResponse(BaseModel):
    """Output contract for Sprint 3 scaffold endpoint."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    limites_reprocessamento: ReprocessingLimitsRead
    monitoramento_status: StatusMonitoringRead
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


class S3StatusResponse(BaseModel):
    """Output contract for Sprint 3 status monitoring endpoint."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    monitoramento_status: StatusMonitoringRead
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


class S3ReprocessResponse(BaseModel):
    """Output contract for Sprint 3 reprocessing endpoint."""

    contrato_versao: str
    correlation_id: str
    reprocessamento_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_anterior: str
    status_reprocessamento: str
    tentativas_reprocessamento: int
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


class S4ActionableMessageRead(BaseModel):
    """Read model with actionable UX message for Sprint 4."""

    codigo_mensagem: str
    titulo: str
    mensagem: str
    acao_recomendada: str
    severidade: str


class S4AccessibilityRead(BaseModel):
    """Read model with accessibility hints for Sprint 4 UX."""

    leitor_tela_ativo: bool
    alto_contraste_ativo: bool
    reduzir_movimento: bool
    aria_live: str
    foco_inicial: str


class S4ScaffoldResponse(BaseModel):
    """Output contract for Sprint 4 final UX scaffold endpoint."""

    contrato_versao: str
    correlation_id: str
    status: str
    evento_id: int
    lote_id: str
    lote_upload_id: str
    status_processamento: str
    proxima_acao: str
    mensagem_acionavel: S4ActionableMessageRead
    acessibilidade: S4AccessibilityRead
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


class S4UXExperienceRead(BaseModel):
    """Read model with final UX rendering hints for Sprint 4."""

    exibir_banner_acao: bool
    destino_acao_principal: str
    prioridade_exibicao: str


class S4UXResponse(S4ScaffoldResponse):
    """Output contract for Sprint 4 final UX endpoint."""

    experiencia_usuario: S4UXExperienceRead


class UploadFileRead(BaseModel):
    """Read model that echoes accepted upload metadata."""

    nome_arquivo: str
    tamanho_arquivo_bytes: int
    content_type: str
    checksum_sha256: str | None = None


class S1UploadResponse(BaseModel):
    """Output contract for Sprint 1 upload endpoint."""

    contrato_versao: str
    correlation_id: str
    upload_id: str
    status: str
    evento_id: int
    arquivo: UploadFileRead
    proxima_acao: str
    pontos_integracao: dict[str, str]
    observabilidade: dict[str, str]


def require_npbb_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Allow access only to NPBB users."""
    if current_user.tipo_usuario != UsuarioTipo.NPBB:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Acesso restrito a usuarios NPBB"},
        )
    return current_user


@router.post("/s1/scaffold", response_model=S1ScaffoldResponse)
def build_s1_scaffold(
    payload: S1ScaffoldRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Validate metadata contract and return Sprint 1 scaffold integration hints.

    Args:
        payload: Upload metadata selected by the frontend flow.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Stable scaffold contract with limits and integration endpoints.

    Raises:
        HTTPException: For forbidden access, invalid contract input, or
            internal errors while handling scaffold generation.
    """

    correlation_id = payload.correlation_id or f"s1-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s1_scaffold_received",
        correlation_id=correlation_id,
        event_message="Requisicao de scaffold recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "nome_arquivo": payload.nome_arquivo,
            "tamanho_arquivo_bytes": payload.tamanho_arquivo_bytes,
            "content_type": payload.content_type,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        _validate_payload(payload=payload, correlation_id=correlation_id)
        ready_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s1_scaffold_ready",
            correlation_id=correlation_id,
            event_message="Contrato de scaffold validado com sucesso",
            evento_id=payload.evento_id,
            severity="info",
        )
        response = S1ScaffoldResponse(
            contrato_versao="s1.v1",
            correlation_id=correlation_id,
            status="ready",
            evento_id=payload.evento_id,
            limites_upload=UploadLimitsRead(
                tamanho_maximo_bytes=MAX_UPLOAD_BYTES,
                content_types_aceitos=list(ACCEPTED_CONTENT_TYPES),
            ),
            proxima_acao="upload_arquivo",
            pontos_integracao={
                "scaffold_endpoint": "/internal/ingestao-inteligente/s1/scaffold",
                "eventos_endpoint": "/evento",
                "upload_endpoint": "/internal/ingestao-inteligente/s1/upload",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "ready_event_id": ready_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s1_scaffold_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S1_SCAFFOLD_INTERNAL_ERROR",
            message="Falha interna ao preparar scaffold da sprint",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post("/s2/scaffold", response_model=S2ScaffoldResponse)
def build_s2_scaffold(
    payload: S2ScaffoldRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Validate Sprint 2 batch contract and return scaffold integration hints.

    Args:
        payload: Batch metadata selected by the frontend Sprint 2 flow.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Stable batch scaffold contract with limits and integration endpoints.

    Raises:
        HTTPException: For forbidden access, invalid contract input, or
            internal errors while handling scaffold generation.
    """

    correlation_id = payload.correlation_id or f"s2-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s2_scaffold_received",
        correlation_id=correlation_id,
        event_message="Requisicao de scaffold da Sprint 2 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "total_arquivos_lote": payload.total_arquivos_lote,
            "total_bytes_lote": payload.total_bytes_lote,
            "total_registros_estimados": payload.total_registros_estimados,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        _validate_s2_payload(payload=payload, correlation_id=correlation_id)
        ready_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s2_scaffold_ready",
            correlation_id=correlation_id,
            event_message="Contrato de scaffold da Sprint 2 validado com sucesso",
            evento_id=payload.evento_id,
            severity="info",
            context={"lote_id": payload.lote_id.strip()},
        )
        response = S2ScaffoldResponse(
            contrato_versao="s2.v1",
            correlation_id=correlation_id,
            status="ready",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            proxima_acao="receber_arquivos_lote",
            limites_lote=BatchLimitsRead(
                max_arquivos_lote=MAX_BATCH_FILES,
                max_bytes_lote=MAX_BATCH_BYTES,
                max_upload_bytes_por_arquivo=MAX_UPLOAD_BYTES,
                content_types_aceitos=list(ACCEPTED_CONTENT_TYPES),
            ),
            pontos_integracao={
                "s2_scaffold_endpoint": "/internal/ingestao-inteligente/s2/scaffold",
                "s2_lote_upload_endpoint": "/internal/ingestao-inteligente/s2/lote/upload",
                "s1_upload_endpoint": "/internal/ingestao-inteligente/s1/upload",
            },
            recepcao_lote=BatchReceptionRead(
                total_arquivos_lote=payload.total_arquivos_lote,
                total_bytes_lote=payload.total_bytes_lote,
                total_registros_estimados=payload.total_registros_estimados,
            ),
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "ready_event_id": ready_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s2_scaffold_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S2_SCAFFOLD_INTERNAL_ERROR",
            message="Falha interna ao preparar scaffold da sprint 2",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post("/s3/scaffold", response_model=S3ScaffoldResponse)
def build_s3_scaffold(
    payload: S3ScaffoldRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Validate Sprint 3 contract and return monitoring scaffold hints.

    Args:
        payload: Status monitoring metadata selected by Sprint 3 frontend flow.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Stable monitoring scaffold contract with reprocessing integrations.

    Raises:
        HTTPException: For forbidden access, invalid contract input, or
            internal errors while handling scaffold generation.
    """

    correlation_id = payload.correlation_id or f"s3-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s3_scaffold_received",
        correlation_id=correlation_id,
        event_message="Requisicao de scaffold da Sprint 3 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "status_processamento": payload.status_processamento,
            "tentativas_reprocessamento": payload.tentativas_reprocessamento,
            "reprocessamento_habilitado": payload.reprocessamento_habilitado,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        status_processamento = _validate_s3_payload(payload=payload, correlation_id=correlation_id)
        proxima_acao = _resolve_s3_next_action(
            status_processamento=status_processamento,
            tentativas_reprocessamento=payload.tentativas_reprocessamento,
            reprocessamento_habilitado=payload.reprocessamento_habilitado,
        )
        ready_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s3_scaffold_ready",
            correlation_id=correlation_id,
            event_message="Contrato de scaffold da Sprint 3 validado com sucesso",
            evento_id=payload.evento_id,
            severity="info",
            context={
                "lote_id": payload.lote_id.strip(),
                "lote_upload_id": payload.lote_upload_id.strip().lower(),
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
            },
        )
        response = S3ScaffoldResponse(
            contrato_versao="s3.v1",
            correlation_id=correlation_id,
            status="ready",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            lote_upload_id=payload.lote_upload_id.strip().lower(),
            status_processamento=status_processamento,
            proxima_acao=proxima_acao,
            limites_reprocessamento=ReprocessingLimitsRead(
                max_tentativas_reprocessamento=MAX_REPROCESS_ATTEMPTS,
                status_reprocessaveis=sorted(S3_REPROCESSABLE_STATUSES),
            ),
            monitoramento_status=StatusMonitoringRead(
                status_atual=status_processamento,
                status_terminal=sorted(S3_TERMINAL_STATUSES),
                polling_interval_seconds=DEFAULT_STATUS_POLL_INTERVAL_SECONDS,
                tentativas_reprocessamento=payload.tentativas_reprocessamento,
                reprocessamento_habilitado=payload.reprocessamento_habilitado,
            ),
            pontos_integracao={
                "s3_scaffold_endpoint": "/internal/ingestao-inteligente/s3/scaffold",
                "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
                "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
                "s2_lote_upload_endpoint": "/internal/ingestao-inteligente/s2/lote/upload",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "ready_event_id": ready_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s3_scaffold_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S3_SCAFFOLD_INTERNAL_ERROR",
            message="Falha interna ao preparar scaffold da sprint 3",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post("/s4/scaffold", response_model=S4ScaffoldResponse)
def build_s4_scaffold(
    payload: S4ScaffoldRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Validate Sprint 4 contract and return final UX scaffold hints.

    Args:
        payload: UX metadata selected by Sprint 4 frontend flow.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Stable UX scaffold contract with actionable message and accessibility.

    Raises:
        HTTPException: For forbidden access, invalid contract input, or
            internal errors while handling scaffold generation.
    """

    correlation_id = payload.correlation_id or f"s4-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s4_scaffold_received",
        correlation_id=correlation_id,
        event_message="Requisicao de scaffold da Sprint 4 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "status_processamento": payload.status_processamento,
            "proxima_acao": payload.proxima_acao,
            "leitor_tela_ativo": payload.leitor_tela_ativo,
            "alto_contraste_ativo": payload.alto_contraste_ativo,
            "reduzir_movimento": payload.reduzir_movimento,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        status_processamento, proxima_acao = _validate_s4_payload(
            payload=payload,
            correlation_id=correlation_id,
        )
        mensagem_acionavel = _build_s4_actionable_message(
            status_processamento=status_processamento,
            proxima_acao=proxima_acao,
        )
        acessibilidade = _build_s4_accessibility_hints(
            leitor_tela_ativo=payload.leitor_tela_ativo,
            alto_contraste_ativo=payload.alto_contraste_ativo,
            reduzir_movimento=payload.reduzir_movimento,
            severidade_mensagem=mensagem_acionavel["severidade"],
        )
        ready_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s4_scaffold_ready",
            correlation_id=correlation_id,
            event_message="Contrato de scaffold da Sprint 4 validado com sucesso",
            evento_id=payload.evento_id,
            severity="info",
            context={
                "lote_id": payload.lote_id.strip(),
                "lote_upload_id": payload.lote_upload_id.strip().lower(),
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
                "codigo_mensagem": mensagem_acionavel["codigo_mensagem"],
            },
        )
        response = S4ScaffoldResponse(
            contrato_versao="s4.v1",
            correlation_id=correlation_id,
            status="ready",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            lote_upload_id=payload.lote_upload_id.strip().lower(),
            status_processamento=status_processamento,
            proxima_acao=proxima_acao,
            mensagem_acionavel=S4ActionableMessageRead(**mensagem_acionavel),
            acessibilidade=S4AccessibilityRead(**acessibilidade),
            pontos_integracao={
                "s4_scaffold_endpoint": "/internal/ingestao-inteligente/s4/scaffold",
                "s4_ux_endpoint": "/internal/ingestao-inteligente/s4/ux",
                "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
                "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
                "s3_scaffold_endpoint": "/internal/ingestao-inteligente/s3/scaffold",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "ready_event_id": ready_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s4_scaffold_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S4_SCAFFOLD_INTERNAL_ERROR",
            message="Falha interna ao preparar scaffold da sprint 4",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post("/s4/ux", response_model=S4UXResponse)
def build_s4_ux(
    payload: S4UXRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Build Sprint 4 final UX payload with actionable message and a11y hints.

    Args:
        payload: UX metadata selected by Sprint 4 frontend flow.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Stable UX contract with rendering hints and integration endpoints.

    Raises:
        HTTPException: For forbidden access, invalid contract input, or
            internal errors while preparing final UX payload.
    """

    correlation_id = payload.correlation_id or f"s4-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s4_ux_received",
        correlation_id=correlation_id,
        event_message="Requisicao de UX final da Sprint 4 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "status_processamento": payload.status_processamento,
            "proxima_acao": payload.proxima_acao,
            "leitor_tela_ativo": payload.leitor_tela_ativo,
            "alto_contraste_ativo": payload.alto_contraste_ativo,
            "reduzir_movimento": payload.reduzir_movimento,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        status_processamento, proxima_acao = _validate_s4_payload(
            payload=payload,
            correlation_id=correlation_id,
        )
        mensagem_acionavel = _build_s4_actionable_message(
            status_processamento=status_processamento,
            proxima_acao=proxima_acao,
        )
        acessibilidade = _build_s4_accessibility_hints(
            leitor_tela_ativo=payload.leitor_tela_ativo,
            alto_contraste_ativo=payload.alto_contraste_ativo,
            reduzir_movimento=payload.reduzir_movimento,
            severidade_mensagem=mensagem_acionavel["severidade"],
        )
        experiencia_usuario = _build_s4_ux_experience(
            proxima_acao=proxima_acao,
            severidade_mensagem=mensagem_acionavel["severidade"],
        )
        ready_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s4_ux_ready",
            correlation_id=correlation_id,
            event_message="Payload de UX final da Sprint 4 preparado com sucesso",
            evento_id=payload.evento_id,
            severity="info",
            context={
                "lote_id": payload.lote_id.strip(),
                "lote_upload_id": payload.lote_upload_id.strip().lower(),
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
                "codigo_mensagem": mensagem_acionavel["codigo_mensagem"],
                "destino_acao_principal": experiencia_usuario["destino_acao_principal"],
            },
        )
        response = S4UXResponse(
            contrato_versao="s4.v1",
            correlation_id=correlation_id,
            status="ready",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            lote_upload_id=payload.lote_upload_id.strip().lower(),
            status_processamento=status_processamento,
            proxima_acao=proxima_acao,
            mensagem_acionavel=S4ActionableMessageRead(**mensagem_acionavel),
            acessibilidade=S4AccessibilityRead(**acessibilidade),
            experiencia_usuario=S4UXExperienceRead(**experiencia_usuario),
            pontos_integracao={
                "s4_ux_endpoint": "/internal/ingestao-inteligente/s4/ux",
                "s4_scaffold_endpoint": "/internal/ingestao-inteligente/s4/scaffold",
                "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
                "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "ready_event_id": ready_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s4_ux_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S4_UX_INTERNAL_ERROR",
            message="Falha interna ao preparar payload de UX da sprint 4",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post("/s3/status", response_model=S3StatusResponse)
def monitor_s3_status(
    payload: S3StatusRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Monitor Sprint 3 lote processing status with actionable diagnostics.

    Args:
        payload: Monitoring payload with lote/upload identifiers and status.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Current status contract with next action and monitoring hints.

    Raises:
        HTTPException: For forbidden access, invalid contract input, or
            internal failures during status monitoring.
    """

    correlation_id = payload.correlation_id or f"s3-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s3_status_received",
        correlation_id=correlation_id,
        event_message="Requisicao de monitoramento de status da Sprint 3 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "status_processamento": payload.status_processamento,
            "tentativas_reprocessamento": payload.tentativas_reprocessamento,
            "reprocessamento_habilitado": payload.reprocessamento_habilitado,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        status_processamento = _validate_s3_payload(payload=payload, correlation_id=correlation_id)
        proxima_acao = _resolve_s3_next_action(
            status_processamento=status_processamento,
            tentativas_reprocessamento=payload.tentativas_reprocessamento,
            reprocessamento_habilitado=payload.reprocessamento_habilitado,
        )
        ready_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s3_status_ready",
            correlation_id=correlation_id,
            event_message="Status da Sprint 3 monitorado com sucesso",
            evento_id=payload.evento_id,
            severity="info",
            context={
                "lote_id": payload.lote_id.strip(),
                "lote_upload_id": payload.lote_upload_id.strip().lower(),
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
            },
        )
        response = S3StatusResponse(
            contrato_versao="s3.v1",
            correlation_id=correlation_id,
            status="ready",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            lote_upload_id=payload.lote_upload_id.strip().lower(),
            status_processamento=status_processamento,
            proxima_acao=proxima_acao,
            monitoramento_status=StatusMonitoringRead(
                status_atual=status_processamento,
                status_terminal=sorted(S3_TERMINAL_STATUSES),
                polling_interval_seconds=DEFAULT_STATUS_POLL_INTERVAL_SECONDS,
                tentativas_reprocessamento=payload.tentativas_reprocessamento,
                reprocessamento_habilitado=payload.reprocessamento_habilitado,
            ),
            pontos_integracao={
                "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
                "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
                "s3_scaffold_endpoint": "/internal/ingestao-inteligente/s3/scaffold",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "ready_event_id": ready_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s3_status_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S3_STATUS_INTERNAL_ERROR",
            message="Falha interna ao monitorar status da sprint 3",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post(
    "/s3/reprocessar",
    response_model=S3ReprocessResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_s3_reprocess(
    payload: S3ReprocessRequest,
    current_user: Usuario = Depends(require_npbb_user),
):
    """Trigger Sprint 3 lote reprocessing when business rules allow it.

    Args:
        payload: Reprocessing payload with lote status and reprocess reason.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Accepted reprocessing contract with reprocessing identifier.

    Raises:
        HTTPException: For forbidden access, invalid contract input, rule
            violations for reprocessing, or unexpected internal failures.
    """

    correlation_id = payload.correlation_id or f"s3-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s3_reprocess_received",
        correlation_id=correlation_id,
        event_message="Requisicao de reprocessamento da Sprint 3 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "status_processamento": payload.status_processamento,
            "tentativas_reprocessamento": payload.tentativas_reprocessamento,
            "reprocessamento_habilitado": payload.reprocessamento_habilitado,
            "motivo_reprocessamento": payload.motivo_reprocessamento,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        status_processamento = _validate_s3_payload(payload=payload, correlation_id=correlation_id)
        _validate_s3_reprocess_eligibility(
            status_processamento=status_processamento,
            tentativas_reprocessamento=payload.tentativas_reprocessamento,
            reprocessamento_habilitado=payload.reprocessamento_habilitado,
            correlation_id=correlation_id,
            lote_id=payload.lote_id,
            lote_upload_id=payload.lote_upload_id,
        )

        reprocessamento_id = f"rep-{uuid4().hex[:12]}"
        tentativas_atualizadas = payload.tentativas_reprocessamento + 1
        accepted_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s3_reprocess_accepted",
            correlation_id=correlation_id,
            event_message="Reprocessamento de lote aceito",
            evento_id=payload.evento_id,
            upload_id=reprocessamento_id,
            severity="info",
            context={
                "lote_id": payload.lote_id.strip(),
                "lote_upload_id": payload.lote_upload_id.strip().lower(),
                "status_anterior": status_processamento,
                "tentativas_reprocessamento": tentativas_atualizadas,
            },
        )
        response = S3ReprocessResponse(
            contrato_versao="s3.v1",
            correlation_id=correlation_id,
            reprocessamento_id=reprocessamento_id,
            status="accepted",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            lote_upload_id=payload.lote_upload_id.strip().lower(),
            status_anterior=status_processamento,
            status_reprocessamento="queued",
            tentativas_reprocessamento=tentativas_atualizadas,
            proxima_acao="monitorar_status_lote",
            pontos_integracao={
                "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
                "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
                "s3_scaffold_endpoint": "/internal/ingestao-inteligente/s3/scaffold",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "accepted_event_id": accepted_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s3_reprocess_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S3_REPROCESS_INTERNAL_ERROR",
            message="Falha interna ao solicitar reprocessamento da sprint 3",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post(
    "/s2/lote/upload",
    response_model=S2LoteUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def intake_s2_lote_upload(
    payload: S2LoteUploadRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    """Execute Sprint 2 batch upload intake with minimal integration checks.

    Args:
        payload: Batch metadata and file list received from Sprint 2 flow.
        session: Open database session for event existence validation.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Accepted batch contract with lot upload identifier and next action.

    Raises:
        HTTPException: For forbidden access, invalid input contracts,
            unknown event IDs, or unexpected internal failures.
    """

    correlation_id = payload.correlation_id or f"s2-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s2_lote_upload_received",
        correlation_id=correlation_id,
        event_message="Requisicao de recepcao de lote da Sprint 2 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "lote_id": payload.lote_id,
            "total_arquivos_lote": payload.total_arquivos_lote,
            "total_bytes_lote": payload.total_bytes_lote,
            "total_registros_estimados": payload.total_registros_estimados,
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        _validate_s2_payload(payload=payload, correlation_id=correlation_id)
        _ensure_event_exists_for_s2(
            session=session,
            evento_id=payload.evento_id,
            lote_id=payload.lote_id,
            correlation_id=correlation_id,
        )

        lote_upload_id = f"lot-{uuid4().hex[:12]}"
        accepted_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s2_lote_upload_accepted",
            correlation_id=correlation_id,
            event_message="Lote aceito para processamento",
            evento_id=payload.evento_id,
            upload_id=lote_upload_id,
            severity="info",
            context={
                "lote_id": payload.lote_id.strip(),
                "status": "accepted",
                "total_arquivos_lote": payload.total_arquivos_lote,
            },
        )
        response = S2LoteUploadResponse(
            contrato_versao="s2.v1",
            correlation_id=correlation_id,
            lote_upload_id=lote_upload_id,
            status="accepted",
            evento_id=payload.evento_id,
            lote_id=payload.lote_id.strip(),
            recepcao_lote=BatchReceptionRead(
                total_arquivos_lote=payload.total_arquivos_lote,
                total_bytes_lote=payload.total_bytes_lote,
                total_registros_estimados=payload.total_registros_estimados,
            ),
            proxima_acao="aguardar_processamento_lote",
            pontos_integracao={
                "s2_scaffold_endpoint": "/internal/ingestao-inteligente/s2/scaffold",
                "s2_lote_upload_endpoint": "/internal/ingestao-inteligente/s2/lote/upload",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "accepted_event_id": accepted_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s2_lote_upload_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
            context={"lote_id": payload.lote_id.strip()},
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S2_LOTE_UPLOAD_INTERNAL_ERROR",
            message="Falha interna ao processar recepcao de lote da sprint 2",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
            context={"lote_id": payload.lote_id.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


@router.post("/s1/upload", response_model=S1UploadResponse, status_code=status.HTTP_202_ACCEPTED)
def intake_s1_upload(
    payload: S1UploadRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    """Execute Sprint 1 main upload intake with minimal integration checks.

    Args:
        payload: Upload metadata and optional SHA-256 checksum.
        session: Open database session for event existence validation.
        current_user: Authenticated NPBB user from authorization dependency.

    Returns:
        Accepted upload contract with upload identifier and next action.

    Raises:
        HTTPException: For forbidden access, invalid input contracts,
            unknown event IDs, or unexpected internal failures.
    """

    correlation_id = payload.correlation_id or f"s1-{uuid4().hex[:12]}"
    received_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s1_upload_received",
        correlation_id=correlation_id,
        event_message="Requisicao de upload da Sprint 1 recebida",
        evento_id=payload.evento_id,
        severity="info",
        context={
            "nome_arquivo": payload.nome_arquivo,
            "tamanho_arquivo_bytes": payload.tamanho_arquivo_bytes,
            "content_type": payload.content_type,
            "checksum_sha256_present": bool(payload.checksum_sha256),
            "user_id": getattr(current_user, "id", None),
        },
    )

    try:
        _validate_payload(payload=payload, correlation_id=correlation_id)
        _validate_checksum(payload=payload, correlation_id=correlation_id)
        _ensure_event_exists(session=session, evento_id=payload.evento_id, correlation_id=correlation_id)

        upload_id = f"upl-{uuid4().hex[:12]}"
        accepted_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s1_upload_accepted",
            correlation_id=correlation_id,
            event_message="Upload aceito para processamento",
            evento_id=payload.evento_id,
            upload_id=upload_id,
            severity="info",
            context={"status": "accepted"},
        )
        response = S1UploadResponse(
            contrato_versao="s1.v1",
            correlation_id=correlation_id,
            upload_id=upload_id,
            status="accepted",
            evento_id=payload.evento_id,
            arquivo=UploadFileRead(
                nome_arquivo=payload.nome_arquivo,
                tamanho_arquivo_bytes=payload.tamanho_arquivo_bytes,
                content_type=payload.content_type.strip().lower(),
                checksum_sha256=(payload.checksum_sha256 or None),
            ),
            proxima_acao="aguardar_processamento_upload",
            pontos_integracao={
                "scaffold_endpoint": "/internal/ingestao-inteligente/s1/scaffold",
                "eventos_endpoint": "/evento",
                "upload_endpoint": "/internal/ingestao-inteligente/s1/upload",
            },
            observabilidade={
                "received_event_id": received_event.telemetry_event_id,
                "accepted_event_id": accepted_event.telemetry_event_id,
            },
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        failed_event = _emit_telemetry_event(
            event_name="ingestao_inteligente_s1_upload_unexpected_error",
            correlation_id=correlation_id,
            event_message=sanitize_exception(exc),
            evento_id=payload.evento_id,
            severity="error",
        )
        detail = s1_telemetry.build_s1_error_detail(
            code="S1_UPLOAD_INTERNAL_ERROR",
            message="Falha interna ao processar upload da sprint",
            action="Consultar logs operacionais com o correlation_id informado.",
            correlation_id=correlation_id,
            telemetry_event_id=failed_event.telemetry_event_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from exc


def _validate_payload(*, payload: S1PayloadBase, correlation_id: str) -> None:
    nome_arquivo = payload.nome_arquivo.strip()
    file_extension = Path(nome_arquivo).suffix.lower()
    if file_extension not in EXPECTED_CONTENT_TYPE_BY_EXTENSION:
        _raise_bad_request(
            correlation_id=correlation_id,
            code="UNSUPPORTED_FILE_EXTENSION",
            message=f"Extensao de arquivo nao suportada: {file_extension or '<sem_extensao>'}",
            action="Use arquivos .pdf, .xlsx ou .csv para o upload da sprint.",
            context={"nome_arquivo": nome_arquivo},
        )

    if payload.tamanho_arquivo_bytes > MAX_UPLOAD_BYTES:
        _raise_bad_request(
            correlation_id=correlation_id,
            code="FILE_TOO_LARGE",
            message=f"Arquivo excede o limite de {MAX_UPLOAD_BYTES} bytes",
            action="Reduza o tamanho do arquivo ou divida o lote em arquivos menores.",
            context={"tamanho_arquivo_bytes": payload.tamanho_arquivo_bytes},
        )

    content_type = payload.content_type.strip().lower()
    if content_type not in ACCEPTED_CONTENT_TYPES:
        _raise_bad_request(
            correlation_id=correlation_id,
            code="UNSUPPORTED_CONTENT_TYPE",
            message=f"content_type nao suportado: {payload.content_type}",
            action="Use um content_type valido para .pdf, .xlsx ou .csv.",
            context={"content_type": payload.content_type},
        )

    expected_content_type = EXPECTED_CONTENT_TYPE_BY_EXTENSION[file_extension]
    if content_type != expected_content_type:
        _raise_bad_request(
            correlation_id=correlation_id,
            code="FILE_EXTENSION_CONTENT_TYPE_MISMATCH",
            message=(
                f"Arquivo {file_extension} deve usar content_type "
                f"{expected_content_type}, recebido {payload.content_type}"
            ),
            action="Ajuste o content_type enviado pelo cliente para combinar com a extensao.",
            context={
                "file_extension": file_extension,
                "expected_content_type": expected_content_type,
                "received_content_type": payload.content_type,
            },
        )


def _validate_checksum(*, payload: S1UploadRequest, correlation_id: str) -> None:
    checksum = payload.checksum_sha256
    if checksum is None:
        return
    normalized = checksum.strip().lower()
    if not SHA256_RE.match(normalized):
        _raise_bad_request(
            correlation_id=correlation_id,
            code="INVALID_CHECKSUM_SHA256",
            message="checksum_sha256 invalido: esperado hash hexadecimal com 64 caracteres",
            action="Recalcule o checksum SHA-256 no frontend antes de reenviar.",
            context={"checksum_sha256": checksum},
        )


def _validate_s2_payload(*, payload: S2ScaffoldRequest, correlation_id: str) -> None:
    lote_id = payload.lote_id.strip()
    if not S2_BATCH_ID_RE.match(lote_id):
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="INVALID_LOTE_ID",
            message="lote_id invalido: use 3-80 chars [a-zA-Z0-9._-]",
            action="Defina um identificador de lote estavel para rastreabilidade.",
            context={"lote_id": payload.lote_id},
        )

    lote_nome = payload.lote_nome.strip()
    if len(lote_nome) < 3:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="INVALID_LOTE_NOME",
            message="lote_nome deve ter ao menos 3 caracteres validos",
            action="Informe um nome de lote descritivo para operacao.",
            context={"lote_nome": payload.lote_nome},
        )

    origem_lote = payload.origem_lote.strip()
    if len(origem_lote) < 3:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="INVALID_ORIGEM_LOTE",
            message="origem_lote deve ter ao menos 3 caracteres validos",
            action="Informe origem operacional do lote (ex: upload_manual).",
            context={"origem_lote": payload.origem_lote},
        )

    if len(payload.arquivos) != payload.total_arquivos_lote:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="BATCH_FILE_COUNT_MISMATCH",
            message=(
                "total_arquivos_lote diverge da lista de arquivos: "
                f"esperado {payload.total_arquivos_lote}, recebido {len(payload.arquivos)}"
            ),
            action="Sincronize contagem de arquivos e metadados do lote.",
            context={
                "total_arquivos_lote": payload.total_arquivos_lote,
                "arquivos_recebidos": len(payload.arquivos),
            },
        )

    total_bytes_calculado = 0
    for index, arquivo in enumerate(payload.arquivos):
        _validate_s2_file_payload(
            arquivo=arquivo,
            item_index=index,
            correlation_id=correlation_id,
        )
        total_bytes_calculado += arquivo.tamanho_arquivo_bytes

    if payload.total_bytes_lote != total_bytes_calculado:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="BATCH_TOTAL_BYTES_MISMATCH",
            message=(
                "total_bytes_lote diverge da soma dos arquivos: "
                f"esperado {total_bytes_calculado}, recebido {payload.total_bytes_lote}"
            ),
            action="Recalcule total_bytes_lote para refletir os arquivos enviados.",
            context={
                "total_bytes_lote": payload.total_bytes_lote,
                "total_bytes_calculado": total_bytes_calculado,
            },
        )


def _validate_s3_payload(*, payload: S3ScaffoldRequest, correlation_id: str) -> str:
    lote_id = payload.lote_id.strip()
    if not S2_BATCH_ID_RE.match(lote_id):
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="INVALID_LOTE_ID",
            message="lote_id invalido: use 3-80 chars [a-zA-Z0-9._-]",
            action="Defina um identificador de lote estavel para rastreabilidade.",
            context={"lote_id": payload.lote_id},
        )

    lote_upload_id = payload.lote_upload_id.strip().lower()
    if not S3_LOTE_UPLOAD_ID_RE.match(lote_upload_id):
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="INVALID_LOTE_UPLOAD_ID",
            message="lote_upload_id invalido: use prefixo lot- com sufixo alfanumerico",
            action="Use o identificador retornado pelo endpoint /s2/lote/upload.",
            context={"lote_upload_id": payload.lote_upload_id},
        )

    status_processamento = payload.status_processamento.strip().lower()
    if status_processamento not in S3_ALLOWED_PROCESSING_STATUSES:
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="INVALID_STATUS_PROCESSAMENTO",
            message=f"status_processamento invalido: {payload.status_processamento}",
            action=(
                "Use status aceitos: " + ", ".join(S3_ALLOWED_PROCESSING_STATUSES) + "."
            ),
            context={"status_processamento": payload.status_processamento},
        )

    if payload.tentativas_reprocessamento > MAX_REPROCESS_ATTEMPTS:
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="REPROCESS_ATTEMPTS_EXCEEDED",
            message=(
                f"tentativas_reprocessamento excede limite de {MAX_REPROCESS_ATTEMPTS}: "
                f"{payload.tentativas_reprocessamento}"
            ),
            action="Encaminhe para analise manual ou ajuste limite operacional do fluxo.",
            context={"tentativas_reprocessamento": payload.tentativas_reprocessamento},
        )

    return status_processamento


def _resolve_s3_next_action(
    *,
    status_processamento: str,
    tentativas_reprocessamento: int,
    reprocessamento_habilitado: bool,
) -> str:
    if (
        status_processamento in S3_REPROCESSABLE_STATUSES
        and reprocessamento_habilitado
        and tentativas_reprocessamento < MAX_REPROCESS_ATTEMPTS
    ):
        return "avaliar_reprocessamento_lote"
    if status_processamento in S3_TERMINAL_STATUSES:
        return "consultar_resultado_final_lote"
    return "monitorar_status_lote"


def _validate_s4_payload(*, payload: S4ScaffoldRequest, correlation_id: str) -> tuple[str, str]:
    status_processamento = _validate_s3_payload(payload=payload, correlation_id=correlation_id)
    proxima_acao = payload.proxima_acao.strip()

    if proxima_acao not in S4_ALLOWED_NEXT_ACTIONS:
        _raise_s4_bad_request(
            correlation_id=correlation_id,
            code="INVALID_PROXIMA_ACAO",
            message=f"proxima_acao invalida para UX final: {payload.proxima_acao}",
            action=(
                "Use proxima_acao valida: "
                + ", ".join(S4_ALLOWED_NEXT_ACTIONS)
                + "."
            ),
            context={"proxima_acao": payload.proxima_acao},
        )

    if (
        proxima_acao == "avaliar_reprocessamento_lote"
        and status_processamento not in S3_REPROCESSABLE_STATUSES
    ):
        _raise_s4_bad_request(
            correlation_id=correlation_id,
            code="INVALID_STATUS_FOR_REPROCESS_ACTION",
            message="proxima_acao de reprocessamento exige status failed ou partial_success",
            action="Ajuste proxima_acao para refletir o status real retornado pela Sprint 3.",
            context={
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
            },
        )

    if (
        proxima_acao == "consultar_resultado_final_lote"
        and status_processamento not in S3_TERMINAL_STATUSES
    ):
        _raise_s4_bad_request(
            correlation_id=correlation_id,
            code="INVALID_STATUS_FOR_FINAL_RESULT_ACTION",
            message="proxima_acao de resultado final exige status terminal do lote",
            action="Use consultar_resultado_final_lote apenas com status terminal.",
            context={
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
            },
        )

    return status_processamento, proxima_acao


def _build_s4_actionable_message(*, status_processamento: str, proxima_acao: str) -> dict[str, str]:
    if proxima_acao == "avaliar_reprocessamento_lote":
        return {
            "codigo_mensagem": "S4_REPROCESS_RECOMMENDED",
            "titulo": "Reprocessamento recomendado",
            "mensagem": (
                "O lote apresentou falha parcial ou total. Revise o contexto e confirme "
                "um novo reprocessamento."
            ),
            "acao_recomendada": "Abrir painel de reprocessamento e confirmar tentativa.",
            "severidade": "warning",
        }

    if proxima_acao == "consultar_resultado_final_lote":
        if status_processamento == "completed":
            return {
                "codigo_mensagem": "S4_FINAL_RESULT_COMPLETED",
                "titulo": "Processamento concluido",
                "mensagem": (
                    "O lote foi processado com sucesso e esta pronto para consulta final."
                ),
                "acao_recomendada": "Abrir resumo final e validar indicadores de conclusao.",
                "severidade": "success",
            }
        if status_processamento == "cancelled":
            return {
                "codigo_mensagem": "S4_FINAL_RESULT_CANCELLED",
                "titulo": "Processamento cancelado",
                "mensagem": (
                    "O lote foi encerrado como cancelado e requer avaliacao operacional."
                ),
                "acao_recomendada": "Registrar justificativa e decidir novo envio do lote.",
                "severidade": "warning",
            }
        return {
            "codigo_mensagem": "S4_FINAL_RESULT_WITH_ISSUES",
            "titulo": "Processamento finalizado com alertas",
            "mensagem": "O lote finalizou com inconsistencias e precisa de tratamento.",
            "acao_recomendada": "Consultar detalhes de erro e planejar reprocessamento manual.",
            "severidade": "warning",
        }

    return {
        "codigo_mensagem": "S4_MONITORING_IN_PROGRESS",
        "titulo": "Monitoramento em andamento",
        "mensagem": (
            "O lote segue em processamento. Continue acompanhando atualizacoes de status."
        ),
        "acao_recomendada": "Manter polling de status ate o lote atingir estado terminal.",
        "severidade": "info",
    }


def _build_s4_accessibility_hints(
    *,
    leitor_tela_ativo: bool,
    alto_contraste_ativo: bool,
    reduzir_movimento: bool,
    severidade_mensagem: str,
) -> dict[str, str | bool]:
    aria_live = "assertive" if severidade_mensagem in {"warning", "error"} else "polite"
    foco_inicial = "banner_mensagem_acionavel" if leitor_tela_ativo else "acao_recomendada"
    return {
        "leitor_tela_ativo": leitor_tela_ativo,
        "alto_contraste_ativo": alto_contraste_ativo,
        "reduzir_movimento": reduzir_movimento,
        "aria_live": aria_live,
        "foco_inicial": foco_inicial,
    }


def _build_s4_ux_experience(*, proxima_acao: str, severidade_mensagem: str) -> dict[str, str | bool]:
    if proxima_acao == "avaliar_reprocessamento_lote":
        return {
            "exibir_banner_acao": True,
            "destino_acao_principal": "abrir_modal_reprocessamento",
            "prioridade_exibicao": "high",
        }

    if proxima_acao == "consultar_resultado_final_lote":
        return {
            "exibir_banner_acao": severidade_mensagem in {"warning", "error"},
            "destino_acao_principal": "abrir_resumo_final_lote",
            "prioridade_exibicao": "medium",
        }

    return {
        "exibir_banner_acao": severidade_mensagem in {"warning", "error"},
        "destino_acao_principal": "manter_monitoramento_status",
        "prioridade_exibicao": "low",
    }


def _validate_s3_reprocess_eligibility(
    *,
    status_processamento: str,
    tentativas_reprocessamento: int,
    reprocessamento_habilitado: bool,
    correlation_id: str,
    lote_id: str,
    lote_upload_id: str,
) -> None:
    if not reprocessamento_habilitado:
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="REPROCESS_DISABLED",
            message="Reprocessamento desabilitado para este lote",
            action="Habilite reprocessamento ou siga com monitoramento do status.",
            context={
                "lote_id": lote_id.strip(),
                "lote_upload_id": lote_upload_id.strip().lower(),
                "status_processamento": status_processamento,
            },
        )

    if status_processamento not in S3_REPROCESSABLE_STATUSES:
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="STATUS_NOT_REPROCESSABLE",
            message=(
                f"Status atual nao permite reprocessamento: {status_processamento}"
            ),
            action=(
                "Solicite reprocessamento apenas para status: "
                + ", ".join(sorted(S3_REPROCESSABLE_STATUSES))
                + "."
            ),
            context={
                "lote_id": lote_id.strip(),
                "lote_upload_id": lote_upload_id.strip().lower(),
                "status_processamento": status_processamento,
            },
        )

    if tentativas_reprocessamento >= MAX_REPROCESS_ATTEMPTS:
        _raise_s3_bad_request(
            correlation_id=correlation_id,
            code="REPROCESS_ATTEMPTS_EXCEEDED",
            message=(
                f"Limite de tentativas de reprocessamento atingido: {tentativas_reprocessamento}"
            ),
            action="Encaminhe para analise manual apos exceder o limite operacional.",
            context={
                "lote_id": lote_id.strip(),
                "lote_upload_id": lote_upload_id.strip().lower(),
                "tentativas_reprocessamento": tentativas_reprocessamento,
            },
        )


def _validate_s2_file_payload(
    *,
    arquivo: S2FileMetadataWrite,
    item_index: int,
    correlation_id: str,
) -> None:
    nome_arquivo = arquivo.nome_arquivo.strip()
    if not nome_arquivo:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="EMPTY_FILE_NAME",
            message=f"nome_arquivo vazio no item {item_index}",
            action="Preencha nome_arquivo para todos os itens do lote.",
            context={"item_index": item_index},
        )

    file_extension = Path(nome_arquivo).suffix.lower()
    if file_extension not in EXPECTED_CONTENT_TYPE_BY_EXTENSION:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="UNSUPPORTED_FILE_EXTENSION",
            message=(
                f"Extensao nao suportada no item {item_index}: "
                f"{file_extension or '<sem_extensao>'}"
            ),
            action="Use arquivos .pdf, .xlsx ou .csv no lote.",
            context={
                "item_index": item_index,
                "nome_arquivo": nome_arquivo,
                "file_extension": file_extension or "<sem_extensao>",
            },
        )

    if arquivo.tamanho_arquivo_bytes > MAX_UPLOAD_BYTES:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="FILE_TOO_LARGE",
            message=(
                f"Arquivo no item {item_index} excede limite de {MAX_UPLOAD_BYTES} bytes "
                f"({arquivo.tamanho_arquivo_bytes})"
            ),
            action="Divida ou compacte o arquivo para respeitar limite por item.",
            context={
                "item_index": item_index,
                "tamanho_arquivo_bytes": arquivo.tamanho_arquivo_bytes,
            },
        )

    content_type = arquivo.content_type.strip().lower()
    if content_type not in ACCEPTED_CONTENT_TYPES:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="UNSUPPORTED_CONTENT_TYPE",
            message=f"content_type nao suportado no item {item_index}: {arquivo.content_type}",
            action="Ajuste content_type para .pdf, .xlsx ou .csv.",
            context={
                "item_index": item_index,
                "content_type": arquivo.content_type,
            },
        )

    expected_content_type = EXPECTED_CONTENT_TYPE_BY_EXTENSION[file_extension]
    if content_type != expected_content_type:
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="FILE_EXTENSION_CONTENT_TYPE_MISMATCH",
            message=(
                f"Item {item_index}: arquivo {file_extension} deve usar content_type "
                f"{expected_content_type}, recebido {arquivo.content_type}"
            ),
            action="Corrija metadados para manter consistencia extensao/content_type.",
            context={
                "item_index": item_index,
                "file_extension": file_extension,
                "expected_content_type": expected_content_type,
                "received_content_type": arquivo.content_type,
            },
        )

    checksum = (arquivo.checksum_sha256 or "").strip().lower()
    if checksum and not SHA256_RE.match(checksum):
        _raise_s2_bad_request(
            correlation_id=correlation_id,
            code="INVALID_CHECKSUM_SHA256",
            message=(
                f"checksum_sha256 invalido no item {item_index}: "
                "esperado hash hexadecimal com 64 caracteres"
            ),
            action="Recalcule o checksum SHA-256 antes de reenviar o lote.",
            context={
                "item_index": item_index,
                "checksum_sha256": arquivo.checksum_sha256 or "",
            },
        )


def _ensure_event_exists_for_s2(
    *,
    session: Session,
    evento_id: int,
    lote_id: str,
    correlation_id: str,
) -> None:
    event_row = session.get(Evento, evento_id)
    if event_row is not None:
        return
    missing_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s2_event_not_found",
        correlation_id=correlation_id,
        event_message="Evento nao encontrado para recepcao de lote da Sprint 2",
        evento_id=evento_id,
        severity="warning",
        context={"lote_id": lote_id.strip()},
    )
    detail = s1_telemetry.build_s1_error_detail(
        code="EVENTO_NOT_FOUND",
        message="Evento nao encontrado para recepcao de lote da sprint 2",
        action="Selecione um evento existente antes de enviar o lote.",
        correlation_id=correlation_id,
        telemetry_event_id=missing_event.telemetry_event_id,
        context={"evento_id": evento_id, "lote_id": lote_id.strip()},
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def _ensure_event_exists(*, session: Session, evento_id: int, correlation_id: str) -> None:
    event_row = session.get(Evento, evento_id)
    if event_row is not None:
        return
    missing_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s1_event_not_found",
        correlation_id=correlation_id,
        event_message="Evento nao encontrado para upload da Sprint 1",
        evento_id=evento_id,
        severity="warning",
    )
    detail = s1_telemetry.build_s1_error_detail(
        code="EVENTO_NOT_FOUND",
        message="Evento nao encontrado para upload da sprint",
        action="Selecione um evento existente antes de enviar o arquivo.",
        correlation_id=correlation_id,
        telemetry_event_id=missing_event.telemetry_event_id,
        context={"evento_id": evento_id},
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def _raise_s2_bad_request(
    *,
    correlation_id: str,
    code: str,
    message: str,
    action: str,
    context: dict[str, str | int],
) -> None:
    failed_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s2_invalid_payload",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={
            "error_code": code,
            "recommended_action": action,
            **context,
        },
    )
    detail = s1_telemetry.build_s1_error_detail(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        telemetry_event_id=failed_event.telemetry_event_id,
        context=context,
    )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def _raise_s3_bad_request(
    *,
    correlation_id: str,
    code: str,
    message: str,
    action: str,
    context: dict[str, str | int | bool],
) -> None:
    failed_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s3_invalid_payload",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={
            "error_code": code,
            "recommended_action": action,
            **context,
        },
    )
    detail = s1_telemetry.build_s1_error_detail(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        telemetry_event_id=failed_event.telemetry_event_id,
        context=context,
    )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def _raise_s4_bad_request(
    *,
    correlation_id: str,
    code: str,
    message: str,
    action: str,
    context: dict[str, str | int | bool],
) -> None:
    failed_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s4_invalid_payload",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={
            "error_code": code,
            "recommended_action": action,
            **context,
        },
    )
    detail = s1_telemetry.build_s1_error_detail(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        telemetry_event_id=failed_event.telemetry_event_id,
        context=context,
    )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def _raise_bad_request(
    *,
    correlation_id: str,
    code: str,
    message: str,
    action: str,
    context: dict[str, str | int],
) -> None:
    failed_event = _emit_telemetry_event(
        event_name="ingestao_inteligente_s1_invalid_payload",
        correlation_id=correlation_id,
        event_message=message,
        severity="warning",
        context={
            "error_code": code,
            "recommended_action": action,
            **context,
        },
    )
    detail = s1_telemetry.build_s1_error_detail(
        code=code,
        message=message,
        action=action,
        correlation_id=correlation_id,
        telemetry_event_id=failed_event.telemetry_event_id,
        context=context,
    )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def _emit_telemetry_event(
    *,
    event_name: str,
    correlation_id: str,
    event_message: str,
    severity: str,
    evento_id: int | None = None,
    upload_id: str | None = None,
    context: dict[str, object] | None = None,
):
    payload = s1_telemetry.S1TelemetryInput(
        event_name=event_name,
        correlation_id=correlation_id,
        event_message=event_message,
        evento_id=evento_id,
        upload_id=upload_id,
        severity=severity,
        context=context,
    )
    event = s1_telemetry.build_s1_telemetry_event(payload)
    s1_telemetry.emit_s1_telemetry_event(telemetry_logger, event)
    return event
