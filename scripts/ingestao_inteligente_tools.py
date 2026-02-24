"""Operational tools for Sprint 1, Sprint 2, Sprint 3 and Sprint 4 interface flows.

This script offers small, verifiable commands for runbook operations:
1. Validate Sprint 1, Sprint 2, Sprint 3 and Sprint 4 input contracts.
2. Simulate main flow execution with backend integration modes.
3. Execute end-to-end runbook checks using stable sample inputs.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Any, Callable
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from frontend.src.features.ingestao_inteligente.s1_core import (  # noqa: E402
    S1CoreFlowError,
    execute_s1_main_flow,
)
from frontend.src.features.ingestao_inteligente.s1_validation import (  # noqa: E402
    S1ValidationError,
    S1ValidationInput,
    validate_s1_flow_output_contract,
    validate_s1_input_contract,
)
from frontend.src.features.ingestao_inteligente.s2_core import (  # noqa: E402
    S2CoreFlowError,
    execute_s2_main_flow,
)
from frontend.src.features.ingestao_inteligente.s2_scaffold import S2FileMetadata  # noqa: E402
from frontend.src.features.ingestao_inteligente.s2_validation import (  # noqa: E402
    S2ValidationError,
    S2ValidationInput,
    validate_s2_flow_output_contract,
    validate_s2_input_contract,
)
from frontend.src.features.ingestao_inteligente.s3_core import (  # noqa: E402
    S3CoreFlowError,
    execute_s3_main_flow,
)
from frontend.src.features.ingestao_inteligente.s3_validation import (  # noqa: E402
    S3ValidationError,
    S3ValidationInput,
    validate_s3_flow_output_contract,
    validate_s3_input_contract,
)
from frontend.src.features.ingestao_inteligente.s4_core import (  # noqa: E402
    S4CoreFlowError,
    execute_s4_main_flow,
)
from frontend.src.features.ingestao_inteligente.s4_validation import (  # noqa: E402
    S4ValidationError,
    S4ValidationInput,
    validate_s4_flow_output_contract,
    validate_s4_input_contract,
)


logger = logging.getLogger("npbb.ingestao_inteligente.tools")

DEFAULT_S2_ARQUIVOS = (
    "tmj_eventos.csv|1024|text/csv",
    "tmj_eventos.xlsx|2048|application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
S3_STATUS_CHOICES = (
    "queued",
    "processing",
    "completed",
    "failed",
    "partial_success",
    "cancelled",
)
S4_NEXT_ACTION_CHOICES = (
    "monitorar_status_lote",
    "avaliar_reprocessamento_lote",
    "consultar_resultado_final_lote",
)


class ToolExecutionError(RuntimeError):
    """Raised when a runbook command fails with actionable context."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        action: str,
        correlation_id: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.action = action
        self.correlation_id = correlation_id
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Return serializable payload for CLI output."""

        return {
            "code": self.code,
            "message": self.message,
            "action": self.action,
            "correlation_id": self.correlation_id,
            "context": self.context,
        }


def _build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for Sprint 1/Sprint 2/Sprint 3/Sprint 4 commands."""

    parser = argparse.ArgumentParser(prog="ingestao_inteligente_tools")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logger level for operational traces.",
    )
    parser.add_argument(
        "--output-format",
        default="pretty",
        choices=("pretty", "json"),
        help="Command output format.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    s1_validate_parser = sub.add_parser("s1:validate-input", help="Validate Sprint 1 input contract.")
    _add_s1_common_input_args(s1_validate_parser)

    s1_simulate_parser = sub.add_parser(
        "s1:simulate-flow",
        help="Simulate Sprint 1 main flow with controllable backend behavior.",
    )
    _add_s1_common_input_args(s1_simulate_parser)
    s1_simulate_parser.add_argument(
        "--backend-mode",
        default="ok",
        choices=("ok", "incomplete", "invalid-status", "raise-error"),
        help="Backend behavior used during flow simulation.",
    )

    s1_runbook_parser = sub.add_parser(
        "s1:runbook-check",
        help="Run one complete local check for Sprint 1 runbook.",
    )
    _add_s1_runbook_defaults(s1_runbook_parser)

    s2_validate_parser = sub.add_parser("s2:validate-input", help="Validate Sprint 2 input contract.")
    _add_s2_common_input_args(s2_validate_parser, required_files=True)

    s2_simulate_parser = sub.add_parser(
        "s2:simulate-flow",
        help="Simulate Sprint 2 main flow with controllable backend behavior.",
    )
    _add_s2_common_input_args(s2_simulate_parser, required_files=True)
    s2_simulate_parser.add_argument(
        "--backend-mode",
        default="ok",
        choices=("ok", "incomplete", "invalid-status", "raise-error"),
        help="Backend behavior used during flow simulation.",
    )

    s2_runbook_parser = sub.add_parser(
        "s2:runbook-check",
        help="Run one complete local check for Sprint 2 runbook.",
    )
    _add_s2_common_input_args(s2_runbook_parser, required_files=False)
    s2_runbook_parser.set_defaults(arquivo=[])

    s3_validate_parser = sub.add_parser("s3:validate-input", help="Validate Sprint 3 input contract.")
    _add_s3_common_input_args(s3_validate_parser)

    s3_simulate_parser = sub.add_parser(
        "s3:simulate-flow",
        help="Simulate Sprint 3 main flow with controllable backend behavior.",
    )
    _add_s3_common_input_args(s3_simulate_parser)
    s3_simulate_parser.add_argument(
        "--backend-mode",
        default="ok",
        choices=(
            "ok",
            "monitor-only",
            "incomplete-status",
            "incomplete-reprocess",
            "invalid-next-action",
            "raise-error",
        ),
        help="Backend behavior used during flow simulation.",
    )

    s3_runbook_parser = sub.add_parser(
        "s3:runbook-check",
        help="Run one complete local check for Sprint 3 runbook.",
    )
    _add_s3_runbook_defaults(s3_runbook_parser)

    s4_validate_parser = sub.add_parser("s4:validate-input", help="Validate Sprint 4 input contract.")
    _add_s4_common_input_args(s4_validate_parser)

    s4_simulate_parser = sub.add_parser(
        "s4:simulate-flow",
        help="Simulate Sprint 4 main flow with controllable backend behavior.",
    )
    _add_s4_common_input_args(s4_simulate_parser)
    s4_simulate_parser.add_argument(
        "--backend-mode",
        default="ok",
        choices=(
            "ok",
            "incomplete",
            "invalid-status",
            "invalid-next-action",
            "invalid-ux-priority",
            "raise-error",
        ),
        help="Backend behavior used during flow simulation.",
    )

    s4_runbook_parser = sub.add_parser(
        "s4:runbook-check",
        help="Run one complete local check for Sprint 4 runbook.",
    )
    _add_s4_runbook_defaults(s4_runbook_parser)
    return parser


def _add_s1_common_input_args(parser: argparse.ArgumentParser) -> None:
    """Register common Sprint 1 input arguments in one parser."""

    parser.add_argument("--evento-id", type=int, required=True, help="Selected event id.")
    parser.add_argument("--nome-arquivo", required=True, help="Upload file name.")
    parser.add_argument(
        "--tamanho-arquivo-bytes",
        type=int,
        required=True,
        help="Upload file size in bytes.",
    )
    parser.add_argument("--content-type", required=True, help="Upload file content type.")
    parser.add_argument("--checksum-sha256", default=None, help="Optional SHA-256 hash.")
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s1_runbook_defaults(parser: argparse.ArgumentParser) -> None:
    """Register Sprint 1 runbook sample defaults in one parser."""

    parser.add_argument(
        "--correlation-id",
        default=None,
        help="Optional correlation id for the runbook check.",
    )
    parser.add_argument(
        "--evento-id",
        type=int,
        default=2025,
        help="Event id used by runbook check sample.",
    )
    parser.add_argument(
        "--nome-arquivo",
        default="tmj_eventos.xlsx",
        help="File name used by runbook check sample.",
    )
    parser.add_argument(
        "--tamanho-arquivo-bytes",
        type=int,
        default=2048,
        help="File size used by runbook check sample.",
    )
    parser.add_argument(
        "--content-type",
        default="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Content type used by runbook check sample.",
    )
    parser.add_argument(
        "--checksum-sha256",
        default=None,
        help="Optional SHA-256 hash used by runbook check sample.",
    )


def _add_s2_common_input_args(parser: argparse.ArgumentParser, *, required_files: bool) -> None:
    """Register common Sprint 2 input arguments in one parser."""

    parser.add_argument("--evento-id", type=int, default=2025, help="Selected event id.")
    parser.add_argument(
        "--lote-id",
        default="lote_tmj_2025_001",
        help="Stable lote identifier used for traceability.",
    )
    parser.add_argument(
        "--lote-nome",
        default="Lote TMJ 2025 001",
        help="Operational lote name.",
    )
    parser.add_argument(
        "--origem-lote",
        default="upload_manual",
        help="Operational lote source.",
    )
    parser.add_argument(
        "--total-registros-estimados",
        type=int,
        default=500,
        help="Estimated row count for the lote.",
    )
    parser.add_argument(
        "--arquivo",
        action="append",
        required=required_files,
        help=(
            "Arquivo no formato nome|tamanho_bytes|content_type|checksum(opcional). "
            "Repita --arquivo para cada item do lote."
        ),
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s3_common_input_args(parser: argparse.ArgumentParser) -> None:
    """Register common Sprint 3 input arguments in one parser."""

    parser.add_argument("--evento-id", type=int, required=True, help="Selected event id.")
    parser.add_argument(
        "--lote-id",
        required=True,
        help="Stable lote identifier used for traceability.",
    )
    parser.add_argument(
        "--lote-upload-id",
        required=True,
        help="Lote upload identifier returned by Sprint 2 flow.",
    )
    parser.add_argument(
        "--status-processamento",
        required=True,
        choices=S3_STATUS_CHOICES,
        help="Current lote processing status.",
    )
    parser.add_argument(
        "--tentativas-reprocessamento",
        type=int,
        default=0,
        help="Current reprocessing attempts for this lote.",
    )
    parser.add_argument(
        "--reprocessamento-habilitado",
        default="true",
        choices=("true", "false"),
        help="Whether reprocessing is enabled for this lote.",
    )
    parser.add_argument(
        "--motivo-reprocessamento",
        default=None,
        help="Optional reprocess reason used by Sprint 3 endpoint.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s3_runbook_defaults(parser: argparse.ArgumentParser) -> None:
    """Register Sprint 3 runbook sample defaults in one parser."""

    parser.add_argument(
        "--correlation-id",
        default=None,
        help="Optional correlation id for the runbook check.",
    )
    parser.add_argument(
        "--evento-id",
        type=int,
        default=2025,
        help="Event id used by runbook check sample.",
    )
    parser.add_argument(
        "--lote-id",
        default="lote_tmj_2025_001",
        help="Lote id used by runbook check sample.",
    )
    parser.add_argument(
        "--lote-upload-id",
        default="lot-abc123def456",
        help="Lote upload id used by runbook check sample.",
    )
    parser.add_argument(
        "--status-processamento",
        default="failed",
        choices=S3_STATUS_CHOICES,
        help="Initial status used by runbook check sample.",
    )
    parser.add_argument(
        "--tentativas-reprocessamento",
        type=int,
        default=1,
        help="Reprocess attempts used by runbook check sample.",
    )
    parser.add_argument(
        "--reprocessamento-habilitado",
        default="true",
        choices=("true", "false"),
        help="Whether reprocessing is enabled in runbook sample.",
    )
    parser.add_argument(
        "--motivo-reprocessamento",
        default="Falha de processamento detectada no lote",
        help="Reprocess reason used by runbook check sample.",
    )


def _add_s4_common_input_args(parser: argparse.ArgumentParser) -> None:
    """Register common Sprint 4 input arguments in one parser."""

    parser.add_argument("--evento-id", type=int, required=True, help="Selected event id.")
    parser.add_argument(
        "--lote-id",
        required=True,
        help="Stable lote identifier used for traceability.",
    )
    parser.add_argument(
        "--lote-upload-id",
        required=True,
        help="Lote upload identifier returned by Sprint 2 flow.",
    )
    parser.add_argument(
        "--status-processamento",
        required=True,
        choices=S3_STATUS_CHOICES,
        help="Current lote processing status.",
    )
    parser.add_argument(
        "--proxima-acao",
        required=True,
        choices=S4_NEXT_ACTION_CHOICES,
        help="Next action expected for final UX rendering.",
    )
    parser.add_argument(
        "--leitor-tela-ativo",
        default="false",
        choices=("true", "false"),
        help="Whether screen reader mode is active.",
    )
    parser.add_argument(
        "--alto-contraste-ativo",
        default="false",
        choices=("true", "false"),
        help="Whether high contrast mode is active.",
    )
    parser.add_argument(
        "--reduzir-movimento",
        default="false",
        choices=("true", "false"),
        help="Whether reduced motion mode is active.",
    )
    parser.add_argument("--correlation-id", default=None, help="Optional flow correlation id.")


def _add_s4_runbook_defaults(parser: argparse.ArgumentParser) -> None:
    """Register Sprint 4 runbook sample defaults in one parser."""

    parser.add_argument(
        "--correlation-id",
        default=None,
        help="Optional correlation id for the runbook check.",
    )
    parser.add_argument(
        "--evento-id",
        type=int,
        default=2025,
        help="Event id used by runbook check sample.",
    )
    parser.add_argument(
        "--lote-id",
        default="lote_tmj_2025_001",
        help="Lote id used by runbook check sample.",
    )
    parser.add_argument(
        "--lote-upload-id",
        default="lot-abc123def456",
        help="Lote upload id used by runbook check sample.",
    )
    parser.add_argument(
        "--status-processamento",
        default="processing",
        choices=S3_STATUS_CHOICES,
        help="Initial status used by runbook check sample.",
    )
    parser.add_argument(
        "--proxima-acao",
        default="monitorar_status_lote",
        choices=S4_NEXT_ACTION_CHOICES,
        help="Next action used by runbook check sample.",
    )
    parser.add_argument(
        "--leitor-tela-ativo",
        default="true",
        choices=("true", "false"),
        help="Whether screen reader mode is active in runbook sample.",
    )
    parser.add_argument(
        "--alto-contraste-ativo",
        default="false",
        choices=("true", "false"),
        help="Whether high contrast mode is active in runbook sample.",
    )
    parser.add_argument(
        "--reduzir-movimento",
        default="true",
        choices=("true", "false"),
        help="Whether reduced motion mode is active in runbook sample.",
    )


def _build_s1_input_from_args(args: argparse.Namespace) -> S1ValidationInput:
    """Build Sprint 1 validation input payload from parsed CLI args."""

    return S1ValidationInput(
        evento_id=int(args.evento_id),
        nome_arquivo=str(args.nome_arquivo),
        tamanho_arquivo_bytes=int(args.tamanho_arquivo_bytes),
        content_type=str(args.content_type),
        checksum_sha256=(str(args.checksum_sha256).strip() if args.checksum_sha256 else None),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _with_s1_correlation_id(payload: S1ValidationInput, *, correlation_id: str) -> S1ValidationInput:
    """Return Sprint 1 input payload with enforced correlation id."""

    return S1ValidationInput(
        evento_id=payload.evento_id,
        nome_arquivo=payload.nome_arquivo,
        tamanho_arquivo_bytes=payload.tamanho_arquivo_bytes,
        content_type=payload.content_type,
        checksum_sha256=payload.checksum_sha256,
        correlation_id=correlation_id,
    )


def _build_s2_input_from_args(
    args: argparse.Namespace,
    *,
    allow_default_files: bool,
) -> S2ValidationInput:
    """Build Sprint 2 validation input payload from parsed CLI args."""

    correlation_id = str(args.correlation_id).strip() if args.correlation_id else f"s2-tool-{uuid4().hex[:12]}"
    arquivos_specs = list(args.arquivo or [])
    if not arquivos_specs and allow_default_files:
        arquivos_specs = list(DEFAULT_S2_ARQUIVOS)
    arquivos = _parse_s2_arquivos(arquivos_specs, correlation_id=correlation_id)
    return S2ValidationInput(
        evento_id=int(args.evento_id),
        lote_id=str(args.lote_id),
        lote_nome=str(args.lote_nome),
        origem_lote=str(args.origem_lote),
        total_registros_estimados=int(args.total_registros_estimados),
        arquivos=arquivos,
        correlation_id=correlation_id,
    )


def _with_s2_correlation_id(payload: S2ValidationInput, *, correlation_id: str) -> S2ValidationInput:
    """Return Sprint 2 input payload with enforced correlation id."""

    return S2ValidationInput(
        evento_id=payload.evento_id,
        lote_id=payload.lote_id,
        lote_nome=payload.lote_nome,
        origem_lote=payload.origem_lote,
        total_registros_estimados=payload.total_registros_estimados,
        arquivos=payload.arquivos,
        correlation_id=correlation_id,
    )


def _build_s3_input_from_args(args: argparse.Namespace) -> S3ValidationInput:
    """Build Sprint 3 validation input payload from parsed CLI args."""

    reprocessamento_habilitado = str(args.reprocessamento_habilitado).strip().lower() == "true"
    return S3ValidationInput(
        evento_id=int(args.evento_id),
        lote_id=str(args.lote_id),
        lote_upload_id=str(args.lote_upload_id),
        status_processamento=str(args.status_processamento),
        tentativas_reprocessamento=int(args.tentativas_reprocessamento),
        reprocessamento_habilitado=reprocessamento_habilitado,
        motivo_reprocessamento=(
            str(args.motivo_reprocessamento).strip() if args.motivo_reprocessamento else None
        ),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _with_s3_correlation_id(payload: S3ValidationInput, *, correlation_id: str) -> S3ValidationInput:
    """Return Sprint 3 input payload with enforced correlation id."""

    return S3ValidationInput(
        evento_id=payload.evento_id,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        tentativas_reprocessamento=payload.tentativas_reprocessamento,
        reprocessamento_habilitado=payload.reprocessamento_habilitado,
        motivo_reprocessamento=payload.motivo_reprocessamento,
        correlation_id=correlation_id,
    )


def _build_s4_input_from_args(args: argparse.Namespace) -> S4ValidationInput:
    """Build Sprint 4 validation input payload from parsed CLI args."""

    return S4ValidationInput(
        evento_id=int(args.evento_id),
        lote_id=str(args.lote_id),
        lote_upload_id=str(args.lote_upload_id),
        status_processamento=str(args.status_processamento),
        proxima_acao=str(args.proxima_acao),
        leitor_tela_ativo=str(args.leitor_tela_ativo).strip().lower() == "true",
        alto_contraste_ativo=str(args.alto_contraste_ativo).strip().lower() == "true",
        reduzir_movimento=str(args.reduzir_movimento).strip().lower() == "true",
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )


def _with_s4_correlation_id(payload: S4ValidationInput, *, correlation_id: str) -> S4ValidationInput:
    """Return Sprint 4 input payload with enforced correlation id."""

    return S4ValidationInput(
        evento_id=payload.evento_id,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        proxima_acao=payload.proxima_acao,
        leitor_tela_ativo=payload.leitor_tela_ativo,
        alto_contraste_ativo=payload.alto_contraste_ativo,
        reduzir_movimento=payload.reduzir_movimento,
        correlation_id=correlation_id,
    )


def _parse_s2_arquivos(
    specs: list[str],
    *,
    correlation_id: str,
) -> tuple[S2FileMetadata, ...]:
    """Parse CLI lote file specs into Sprint 2 file metadata contracts."""

    if not specs:
        raise ToolExecutionError(
            code="S2_FILES_REQUIRED",
            message="Nenhum arquivo informado para o lote da Sprint 2",
            action="Informe ao menos um --arquivo no formato nome|tamanho|content_type.",
            correlation_id=correlation_id,
        )

    parsed: list[S2FileMetadata] = []
    for index, raw in enumerate(specs):
        parts = [part.strip() for part in str(raw).split("|")]
        if len(parts) not in {3, 4}:
            raise ToolExecutionError(
                code="INVALID_S2_ARQUIVO_FORMAT",
                message=f"Formato invalido para --arquivo no item {index}: {raw}",
                action="Use nome|tamanho_bytes|content_type|checksum(opcional).",
                correlation_id=correlation_id,
                context={"item_index": index, "arquivo": raw},
            )
        nome_arquivo = parts[0]
        tamanho_raw = parts[1]
        content_type = parts[2]
        checksum_sha256 = parts[3] if len(parts) == 4 else None
        try:
            tamanho_arquivo_bytes = int(tamanho_raw)
        except ValueError as exc:
            raise ToolExecutionError(
                code="INVALID_S2_ARQUIVO_SIZE",
                message=f"tamanho_bytes invalido no item {index}: {tamanho_raw}",
                action="Use um inteiro positivo no segundo campo de --arquivo.",
                correlation_id=correlation_id,
                context={"item_index": index, "arquivo": raw},
            ) from exc
        parsed.append(
            S2FileMetadata(
                nome_arquivo=nome_arquivo,
                tamanho_arquivo_bytes=tamanho_arquivo_bytes,
                content_type=content_type,
                checksum_sha256=(checksum_sha256 or None),
            )
        )
    return tuple(parsed)


def _simulate_s1_backend(mode: str) -> Callable[[str, dict[str, Any]], dict[str, Any]]:
    """Return Sprint 1 backend callback with deterministic simulation behavior."""

    def sender(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        if endpoint != "/internal/ingestao-inteligente/s1/upload":
            raise RuntimeError(f"Endpoint inesperado na simulacao: {endpoint}")

        if mode == "raise-error":
            raise RuntimeError("Falha de comunicacao simulada com backend")
        if mode == "incomplete":
            return {"status": "accepted"}
        if mode == "invalid-status":
            return {
                "status": "done",
                "upload_id": "upl-sim-invalid",
                "evento_id": int(payload["evento_id"]),
                "proxima_acao": "aguardar_processamento_upload",
            }
        return {
            "status": "accepted",
            "upload_id": f"upl-sim-{uuid4().hex[:12]}",
            "evento_id": int(payload["evento_id"]),
            "proxima_acao": "aguardar_processamento_upload",
        }

    return sender


def _simulate_s2_backend(mode: str) -> Callable[[str, dict[str, Any]], dict[str, Any]]:
    """Return Sprint 2 backend callback with deterministic simulation behavior."""

    def sender(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        if endpoint != "/internal/ingestao-inteligente/s2/lote/upload":
            raise RuntimeError(f"Endpoint inesperado na simulacao: {endpoint}")

        if mode == "raise-error":
            raise RuntimeError("Falha de comunicacao simulada com backend")
        if mode == "incomplete":
            return {"status": "accepted"}
        if mode == "invalid-status":
            return {
                "status": "done",
                "lote_upload_id": "lot-sim-invalid",
                "evento_id": int(payload["evento_id"]),
                "lote_id": str(payload["lote_id"]),
                "proxima_acao": "aguardar_processamento_lote",
            }
        return {
            "status": "accepted",
            "lote_upload_id": f"lot-sim-{uuid4().hex[:12]}",
            "evento_id": int(payload["evento_id"]),
            "lote_id": str(payload["lote_id"]),
            "proxima_acao": "aguardar_processamento_lote",
        }

    return sender


def _simulate_s3_backend(mode: str) -> Callable[[str, dict[str, Any]], dict[str, Any]]:
    """Return Sprint 3 backend callback with deterministic simulation behavior."""

    def sender(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        evento_id = int(payload["evento_id"])
        lote_id = str(payload["lote_id"]).strip()
        lote_upload_id = str(payload["lote_upload_id"]).strip().lower()
        status_processamento = str(payload["status_processamento"]).strip().lower()
        tentativas_reprocessamento = int(payload.get("tentativas_reprocessamento", 0))
        reprocessamento_habilitado = bool(payload.get("reprocessamento_habilitado", True))

        if mode == "raise-error":
            raise RuntimeError("Falha de comunicacao simulada com backend")

        if endpoint == "/internal/ingestao-inteligente/s3/status":
            if mode == "incomplete-status":
                return {"status": "ready"}
            if mode == "invalid-next-action":
                return {
                    "status": "ready",
                    "evento_id": evento_id,
                    "lote_id": lote_id,
                    "lote_upload_id": lote_upload_id,
                    "status_processamento": status_processamento,
                    "proxima_acao": "acao_desconhecida",
                }

            if mode == "monitor-only":
                proxima_acao = "monitorar_status_lote"
                if status_processamento in {"completed", "cancelled"}:
                    proxima_acao = "consultar_resultado_final_lote"
            elif (
                status_processamento in {"failed", "partial_success"}
                and reprocessamento_habilitado
                and tentativas_reprocessamento < 5
            ):
                proxima_acao = "avaliar_reprocessamento_lote"
            elif status_processamento in {"completed", "cancelled"}:
                proxima_acao = "consultar_resultado_final_lote"
            else:
                proxima_acao = "monitorar_status_lote"

            return {
                "status": "ready",
                "evento_id": evento_id,
                "lote_id": lote_id,
                "lote_upload_id": lote_upload_id,
                "status_processamento": status_processamento,
                "proxima_acao": proxima_acao,
            }

        if endpoint == "/internal/ingestao-inteligente/s3/reprocessar":
            if mode == "incomplete-reprocess":
                return {"status": "accepted"}
            return {
                "status": "accepted",
                "reprocessamento_id": f"rep-sim-{uuid4().hex[:12]}",
                "evento_id": evento_id,
                "lote_id": lote_id,
                "lote_upload_id": lote_upload_id,
                "status_anterior": status_processamento,
                "status_reprocessamento": "queued",
                "tentativas_reprocessamento": tentativas_reprocessamento + 1,
                "proxima_acao": "monitorar_status_lote",
            }

        raise RuntimeError(f"Endpoint inesperado na simulacao: {endpoint}")

    return sender


def _simulate_s4_backend(mode: str) -> Callable[[str, dict[str, Any]], dict[str, Any]]:
    """Return Sprint 4 backend callback with deterministic simulation behavior."""

    def sender(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        if endpoint != "/internal/ingestao-inteligente/s4/ux":
            raise RuntimeError(f"Endpoint inesperado na simulacao: {endpoint}")

        if mode == "raise-error":
            raise RuntimeError("Falha de comunicacao simulada com backend")
        if mode == "incomplete":
            return {"status": "ok"}

        response = _build_s4_backend_response(payload)
        if mode == "invalid-status":
            response["status"] = "done"
        elif mode == "invalid-next-action":
            response["proxima_acao"] = "acao_desconhecida"
        elif mode == "invalid-ux-priority":
            response["experiencia_usuario"]["prioridade_exibicao"] = "urgent"
        return response

    return sender


def _build_s4_backend_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Build one valid simulated backend response for Sprint 4 UX endpoint."""

    evento_id = int(payload["evento_id"])
    lote_id = str(payload["lote_id"]).strip()
    lote_upload_id = str(payload["lote_upload_id"]).strip().lower()
    status_processamento = str(payload["status_processamento"]).strip().lower()
    proxima_acao = str(payload["proxima_acao"]).strip()
    leitor_tela_ativo = bool(payload.get("leitor_tela_ativo", False))
    alto_contraste_ativo = bool(payload.get("alto_contraste_ativo", False))
    reduzir_movimento = bool(payload.get("reduzir_movimento", False))

    mensagem = _resolve_s4_actionable_message(
        status_processamento=status_processamento,
        proxima_acao=proxima_acao,
    )
    severidade = str(mensagem["severidade"]).lower()
    return {
        "status": "ok",
        "evento_id": evento_id,
        "lote_id": lote_id,
        "lote_upload_id": lote_upload_id,
        "status_processamento": status_processamento,
        "proxima_acao": proxima_acao,
        "mensagem_acionavel": mensagem,
        "acessibilidade": {
            "leitor_tela_ativo": leitor_tela_ativo,
            "alto_contraste_ativo": alto_contraste_ativo,
            "reduzir_movimento": reduzir_movimento,
            "aria_live": "assertive" if severidade in {"warning", "error"} else "polite",
            "foco_inicial": "banner_mensagem_acionavel" if leitor_tela_ativo else "acao_recomendada",
        },
        "experiencia_usuario": {
            "exibir_banner_acao": True,
            "destino_acao_principal": _resolve_s4_primary_action_destination(proxima_acao),
            "prioridade_exibicao": "high" if severidade in {"warning", "error"} else "medium",
        },
        "pontos_integracao": {
            "s4_scaffold_endpoint": "/internal/ingestao-inteligente/s4/scaffold",
            "s4_ux_endpoint": "/internal/ingestao-inteligente/s4/ux",
            "s3_status_endpoint": "/internal/ingestao-inteligente/s3/status",
            "s3_reprocess_endpoint": "/internal/ingestao-inteligente/s3/reprocessar",
        },
    }


def _resolve_s4_actionable_message(
    *,
    status_processamento: str,
    proxima_acao: str,
) -> dict[str, str]:
    """Resolve Sprint 4 actionable message for simulated UX responses."""

    if proxima_acao == "avaliar_reprocessamento_lote":
        return {
            "codigo_mensagem": "S4_REPROCESS_RECOMMENDED",
            "titulo": "Reprocessamento recomendado",
            "mensagem": "O lote apresentou falha e requer nova tentativa assistida.",
            "acao_recomendada": "Abrir painel de reprocessamento e confirmar tentativa.",
            "severidade": "warning",
        }
    if proxima_acao == "consultar_resultado_final_lote":
        if status_processamento == "completed":
            return {
                "codigo_mensagem": "S4_FINAL_RESULT_COMPLETED",
                "titulo": "Processamento concluido",
                "mensagem": "O lote foi processado com sucesso e esta pronto para consulta final.",
                "acao_recomendada": "Abrir resumo final e validar indicadores de conclusao.",
                "severidade": "success",
            }
        if status_processamento == "cancelled":
            return {
                "codigo_mensagem": "S4_FINAL_RESULT_CANCELLED",
                "titulo": "Processamento cancelado",
                "mensagem": "O lote foi encerrado como cancelado e requer avaliacao operacional.",
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
        "mensagem": "O lote segue em processamento. Continue acompanhando atualizacoes de status.",
        "acao_recomendada": "Manter polling de status ate o lote atingir estado terminal.",
        "severidade": "info",
    }


def _resolve_s4_primary_action_destination(proxima_acao: str) -> str:
    """Resolve Sprint 4 main CTA destination for simulated UX responses."""

    if proxima_acao == "avaliar_reprocessamento_lote":
        return "abrir_painel_reprocessamento"
    if proxima_acao == "consultar_resultado_final_lote":
        return "abrir_resumo_final_lote"
    return "manter_monitoramento_status"


def _log_event(
    *,
    level: int,
    event_name: str,
    correlation_id: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Emit one structured log line with event name and correlation id."""

    logger.log(
        level,
        "%s correlation_id=%s context=%s",
        event_name,
        correlation_id,
        json.dumps(context or {}, ensure_ascii=False, sort_keys=True),
    )


def _run_s1_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:validate-input` command and return output payload."""

    payload = _build_s1_input_from_args(args)
    correlation_id = payload.correlation_id or f"s1-tool-{uuid4().hex[:12]}"
    payload = _with_s1_correlation_id(payload, correlation_id=correlation_id)
    _log_event(
        level=logging.INFO,
        event_name="s1_validate_input_started",
        correlation_id=correlation_id,
        context={"evento_id": payload.evento_id, "nome_arquivo": payload.nome_arquivo},
    )
    result = validate_s1_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s1_validate_input_completed",
        correlation_id=result.correlation_id,
        context={"status": result.status, "checks": list(result.checks)},
    )
    return {"command": "s1:validate-input", "result": result.to_dict()}


def _run_s1_simulate_flow(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:simulate-flow` command and return output payload."""

    payload = _build_s1_input_from_args(args)
    correlation_id = payload.correlation_id or f"s1-tool-{uuid4().hex[:12]}"
    payload = _with_s1_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s1_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s1_simulate_flow_started",
        correlation_id=validation.correlation_id,
        context={"backend_mode": args.backend_mode},
    )

    flow_output = execute_s1_main_flow(
        _with_s1_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s1_backend(str(args.backend_mode)),
    ).to_dict()
    output_validation = validate_s1_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s1_simulate_flow_completed",
        correlation_id=validation.correlation_id,
        context={"status": output_validation.status, "upload_id": flow_output["upload_id"]},
    )
    return {
        "command": "s1:simulate-flow",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s1_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s1:runbook-check` command and return output payload."""

    payload = S1ValidationInput(
        evento_id=int(args.evento_id),
        nome_arquivo=str(args.nome_arquivo),
        tamanho_arquivo_bytes=int(args.tamanho_arquivo_bytes),
        content_type=str(args.content_type),
        checksum_sha256=(str(args.checksum_sha256).strip() if args.checksum_sha256 else None),
        correlation_id=(str(args.correlation_id).strip() if args.correlation_id else None),
    )
    correlation_id = payload.correlation_id or f"s1-tool-{uuid4().hex[:12]}"
    payload = _with_s1_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s1_input_contract(payload)
    flow_output = execute_s1_main_flow(
        _with_s1_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s1_backend("ok"),
    ).to_dict()
    output_validation = validate_s1_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s1_runbook_check_completed",
        correlation_id=validation.correlation_id,
        context={"status": output_validation.status, "upload_id": flow_output["upload_id"]},
    )
    return {
        "command": "s1:runbook-check",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s2_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:validate-input` command and return output payload."""

    payload = _build_s2_input_from_args(args, allow_default_files=False)
    _log_event(
        level=logging.INFO,
        event_name="s2_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={"evento_id": payload.evento_id, "lote_id": payload.lote_id},
    )
    result = validate_s2_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s2_validate_input_completed",
        correlation_id=result.correlation_id,
        context={
            "status": result.status,
            "total_arquivos_lote": result.resumo_lote["total_arquivos_lote"],
        },
    )
    return {"command": "s2:validate-input", "result": result.to_dict()}


def _run_s2_simulate_flow(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:simulate-flow` command and return output payload."""

    payload = _build_s2_input_from_args(args, allow_default_files=False)
    correlation_id = payload.correlation_id or f"s2-tool-{uuid4().hex[:12]}"
    payload = _with_s2_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s2_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s2_simulate_flow_started",
        correlation_id=validation.correlation_id,
        context={"backend_mode": args.backend_mode, "lote_id": payload.lote_id},
    )

    flow_output = execute_s2_main_flow(
        _with_s2_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s2_backend(str(args.backend_mode)),
    ).to_dict()
    output_validation = validate_s2_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s2_simulate_flow_completed",
        correlation_id=validation.correlation_id,
        context={
            "status": output_validation.status,
            "lote_upload_id": flow_output["lote_upload_id"],
        },
    )
    return {
        "command": "s2:simulate-flow",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s2_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s2:runbook-check` command and return output payload."""

    payload = _build_s2_input_from_args(args, allow_default_files=True)
    correlation_id = payload.correlation_id or f"s2-tool-{uuid4().hex[:12]}"
    payload = _with_s2_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s2_input_contract(payload)
    flow_output = execute_s2_main_flow(
        _with_s2_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s2_backend("ok"),
    ).to_dict()
    output_validation = validate_s2_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s2_runbook_check_completed",
        correlation_id=validation.correlation_id,
        context={
            "status": output_validation.status,
            "lote_upload_id": flow_output["lote_upload_id"],
        },
    )
    return {
        "command": "s2:runbook-check",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s3_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:validate-input` command and return output payload."""

    payload = _build_s3_input_from_args(args)
    correlation_id = payload.correlation_id or f"s3-tool-{uuid4().hex[:12]}"
    payload = _with_s3_correlation_id(payload, correlation_id=correlation_id)
    _log_event(
        level=logging.INFO,
        event_name="s3_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "evento_id": payload.evento_id,
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
        },
    )
    result = validate_s3_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s3_validate_input_completed",
        correlation_id=result.correlation_id,
        context={
            "status": result.status,
            "status_processamento": result.resumo_monitoramento["status_processamento"],
        },
    )
    return {"command": "s3:validate-input", "result": result.to_dict()}


def _run_s3_simulate_flow(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:simulate-flow` command and return output payload."""

    payload = _build_s3_input_from_args(args)
    correlation_id = payload.correlation_id or f"s3-tool-{uuid4().hex[:12]}"
    payload = _with_s3_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s3_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s3_simulate_flow_started",
        correlation_id=validation.correlation_id,
        context={
            "backend_mode": args.backend_mode,
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
        },
    )

    flow_output = execute_s3_main_flow(
        _with_s3_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s3_backend(str(args.backend_mode)),
    ).to_dict()
    output_validation = validate_s3_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s3_simulate_flow_completed",
        correlation_id=validation.correlation_id,
        context={
            "status": output_validation.status,
            "lote_upload_id": flow_output["lote_upload_id"],
            "proxima_acao": flow_output["proxima_acao"],
            "reprocess_triggered": flow_output.get("reprocessamento") is not None,
        },
    )
    return {
        "command": "s3:simulate-flow",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s3_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s3:runbook-check` command and return output payload."""

    payload = _build_s3_input_from_args(args)
    correlation_id = payload.correlation_id or f"s3-tool-{uuid4().hex[:12]}"
    payload = _with_s3_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s3_input_contract(payload)
    flow_output = execute_s3_main_flow(
        _with_s3_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s3_backend("ok"),
    ).to_dict()
    output_validation = validate_s3_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s3_runbook_check_completed",
        correlation_id=validation.correlation_id,
        context={
            "status": output_validation.status,
            "lote_upload_id": flow_output["lote_upload_id"],
            "proxima_acao": flow_output["proxima_acao"],
            "reprocess_triggered": flow_output.get("reprocessamento") is not None,
        },
    )
    return {
        "command": "s3:runbook-check",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s4_validate_input(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:validate-input` command and return output payload."""

    payload = _build_s4_input_from_args(args)
    correlation_id = payload.correlation_id or f"s4-tool-{uuid4().hex[:12]}"
    payload = _with_s4_correlation_id(payload, correlation_id=correlation_id)
    _log_event(
        level=logging.INFO,
        event_name="s4_validate_input_started",
        correlation_id=payload.correlation_id or "",
        context={
            "evento_id": payload.evento_id,
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "proxima_acao": payload.proxima_acao,
        },
    )
    result = validate_s4_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s4_validate_input_completed",
        correlation_id=result.correlation_id,
        context={
            "status": result.status,
            "status_processamento": result.resumo_ux["status_processamento"],
            "proxima_acao": result.resumo_ux["proxima_acao"],
        },
    )
    return {"command": "s4:validate-input", "result": result.to_dict()}


def _run_s4_simulate_flow(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:simulate-flow` command and return output payload."""

    payload = _build_s4_input_from_args(args)
    correlation_id = payload.correlation_id or f"s4-tool-{uuid4().hex[:12]}"
    payload = _with_s4_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s4_input_contract(payload)
    _log_event(
        level=logging.INFO,
        event_name="s4_simulate_flow_started",
        correlation_id=validation.correlation_id,
        context={
            "backend_mode": args.backend_mode,
            "lote_id": payload.lote_id,
            "lote_upload_id": payload.lote_upload_id,
            "proxima_acao": payload.proxima_acao,
        },
    )

    flow_output = execute_s4_main_flow(
        _with_s4_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s4_backend(str(args.backend_mode)),
    ).to_dict()
    output_validation = validate_s4_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s4_simulate_flow_completed",
        correlation_id=validation.correlation_id,
        context={
            "status": output_validation.status,
            "lote_upload_id": flow_output["lote_upload_id"],
            "proxima_acao": flow_output["proxima_acao"],
            "codigo_mensagem": flow_output["mensagem_acionavel"]["codigo_mensagem"],
        },
    )
    return {
        "command": "s4:simulate-flow",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _run_s4_runbook_check(args: argparse.Namespace) -> dict[str, Any]:
    """Run `s4:runbook-check` command and return output payload."""

    payload = _build_s4_input_from_args(args)
    correlation_id = payload.correlation_id or f"s4-tool-{uuid4().hex[:12]}"
    payload = _with_s4_correlation_id(payload, correlation_id=correlation_id)
    validation = validate_s4_input_contract(payload)
    flow_output = execute_s4_main_flow(
        _with_s4_correlation_id(payload, correlation_id=validation.correlation_id).to_core_input(),
        send_backend=_simulate_s4_backend("ok"),
    ).to_dict()
    output_validation = validate_s4_flow_output_contract(
        flow_output,
        correlation_id=validation.correlation_id,
    )
    _log_event(
        level=logging.INFO,
        event_name="s4_runbook_check_completed",
        correlation_id=validation.correlation_id,
        context={
            "status": output_validation.status,
            "lote_upload_id": flow_output["lote_upload_id"],
            "proxima_acao": flow_output["proxima_acao"],
            "codigo_mensagem": flow_output["mensagem_acionavel"]["codigo_mensagem"],
        },
    )
    return {
        "command": "s4:runbook-check",
        "input_validation": validation.to_dict(),
        "flow_output": flow_output,
        "output_validation": output_validation.to_dict(),
    }


def _render_output(payload: dict[str, Any], *, output_format: str) -> None:
    """Render command result payload in selected output format."""

    if output_format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return

    command = payload.get("command", "unknown")
    print(f"[OK] {command}")
    if "result" in payload:
        result = payload["result"]
        print(f" - correlation_id: {result.get('correlation_id')}")
        print(f" - status: {result.get('status')}")
        print(f" - checks: {result.get('checks')}")
        return

    input_validation = payload.get("input_validation", {})
    output_validation = payload.get("output_validation", {})
    flow_output = payload.get("flow_output", {})
    flow_id_key = "lote_upload_id" if "lote_upload_id" in flow_output else "upload_id"
    print(f" - correlation_id: {input_validation.get('correlation_id')}")
    print(f" - input_status: {input_validation.get('status')}")
    print(f" - flow_status: {flow_output.get('status')}")
    print(f" - {flow_id_key}: {flow_output.get(flow_id_key)}")
    if isinstance(flow_output.get("reprocessamento"), dict):
        print(f" - reprocessamento_id: {flow_output['reprocessamento'].get('reprocessamento_id')}")
    print(f" - output_status: {output_validation.get('status')}")


def _render_error(error: ToolExecutionError, *, output_format: str) -> None:
    """Render actionable command failure in selected output format."""

    payload = error.to_dict()
    if output_format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return
    print(f"[ERROR] {payload['code']}: {payload['message']}")
    print(f" - action: {payload['action']}")
    print(f" - correlation_id: {payload['correlation_id']}")
    if payload["context"]:
        print(f" - context: {payload['context']}")


def _context_from_flow_error(error: Exception) -> dict[str, Any]:
    """Return consistent error context for Sprint flow exceptions."""

    context: dict[str, Any] = {}
    if hasattr(error, "observability_event_id") and getattr(error, "observability_event_id"):
        context["observability_event_id"] = str(getattr(error, "observability_event_id"))
    if hasattr(error, "event_id") and getattr(error, "event_id"):
        context["event_id"] = str(getattr(error, "event_id"))
    if hasattr(error, "stage") and getattr(error, "stage"):
        context["stage"] = str(getattr(error, "stage"))
    return context


def main(argv: list[str] | None = None) -> int:
    """Run operational tool commands for Sprint 1, Sprint 2, Sprint 3 and Sprint 4.

    Args:
        argv: Optional CLI argument list.

    Returns:
        Exit code: `0` on success, `1` on expected operational failures.

    Raises:
        SystemExit: Propagated by argparse for invalid CLI usage.
    """

    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper()),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        if args.command == "s1:validate-input":
            payload = _run_s1_validate_input(args)
        elif args.command == "s1:simulate-flow":
            payload = _run_s1_simulate_flow(args)
        elif args.command == "s1:runbook-check":
            payload = _run_s1_runbook_check(args)
        elif args.command == "s2:validate-input":
            payload = _run_s2_validate_input(args)
        elif args.command == "s2:simulate-flow":
            payload = _run_s2_simulate_flow(args)
        elif args.command == "s2:runbook-check":
            payload = _run_s2_runbook_check(args)
        elif args.command == "s3:validate-input":
            payload = _run_s3_validate_input(args)
        elif args.command == "s3:simulate-flow":
            payload = _run_s3_simulate_flow(args)
        elif args.command == "s3:runbook-check":
            payload = _run_s3_runbook_check(args)
        elif args.command == "s4:validate-input":
            payload = _run_s4_validate_input(args)
        elif args.command == "s4:simulate-flow":
            payload = _run_s4_simulate_flow(args)
        elif args.command == "s4:runbook-check":
            payload = _run_s4_runbook_check(args)
        else:
            raise ToolExecutionError(
                code="UNKNOWN_COMMAND",
                message=f"Comando nao suportado: {args.command}",
                action="Use --help para listar comandos disponiveis.",
                correlation_id=f"ingestao-tool-{uuid4().hex[:12]}",
            )
        _render_output(payload, output_format=str(args.output_format))
        return 0
    except (S1ValidationError, S2ValidationError, S3ValidationError, S4ValidationError) as exc:
        correlation_id = exc.correlation_id
        _log_event(
            level=logging.WARNING,
            event_name="ingestao_tool_validation_failed",
            correlation_id=correlation_id,
            context={"error_code": exc.code},
        )
        error = ToolExecutionError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=correlation_id,
            context=(
                {"observability_event_id": exc.observability_event_id}
                if exc.observability_event_id
                else {}
            ),
        )
        _render_error(error, output_format=str(args.output_format))
        return 1
    except (S1CoreFlowError, S2CoreFlowError, S3CoreFlowError, S4CoreFlowError) as exc:
        _log_event(
            level=logging.ERROR,
            event_name="ingestao_tool_flow_failed",
            correlation_id=exc.correlation_id,
            context={"error_code": exc.code},
        )
        error = ToolExecutionError(
            code=exc.code,
            message=exc.message,
            action=exc.action,
            correlation_id=exc.correlation_id,
            context=_context_from_flow_error(exc),
        )
        _render_error(error, output_format=str(args.output_format))
        return 1
    except ToolExecutionError as exc:
        _render_error(exc, output_format=str(args.output_format))
        return 1
    except Exception as exc:  # noqa: BLE001
        correlation_id = f"ingestao-tool-{uuid4().hex[:12]}"
        _log_event(
            level=logging.ERROR,
            event_name="ingestao_tool_unexpected_error",
            correlation_id=correlation_id,
            context={"error_type": type(exc).__name__},
        )
        error = ToolExecutionError(
            code="INGESTAO_TOOL_UNEXPECTED_ERROR",
            message=f"Falha inesperada ao executar ferramenta operacional: {type(exc).__name__}",
            action="Reexecutar com --log-level DEBUG e revisar stacktrace local.",
            correlation_id=correlation_id,
        )
        _render_error(error, output_format=str(args.output_format))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
