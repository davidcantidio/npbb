"""Validation tests for Sprint 2 smart-ingestion contracts."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s2_core import (  # noqa: E402
    S2CoreFlowError,
    S2CoreInput,
    execute_s2_main_flow,
)
from frontend.src.features.ingestao_inteligente.s2_scaffold import S2FileMetadata  # noqa: E402
from frontend.src.features.ingestao_inteligente.s2_validation import (  # noqa: E402
    S2ValidationError,
    S2ValidationInput,
    validate_s2_flow_output_contract,
    validate_s2_input_contract,
)


def _valid_s2_files() -> tuple[S2FileMetadata, ...]:
    return (
        S2FileMetadata(
            nome_arquivo="tmj_eventos.csv",
            tamanho_arquivo_bytes=1024,
            content_type="text/csv",
        ),
        S2FileMetadata(
            nome_arquivo="tmj_eventos.xlsx",
            tamanho_arquivo_bytes=2048,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    )


def _valid_s2_validation_input() -> S2ValidationInput:
    return S2ValidationInput(
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_nome="Lote TMJ 2025 001",
        origem_lote="upload_manual",
        total_registros_estimados=500,
        arquivos=_valid_s2_files(),
        correlation_id="s2-validation-2025",
    )


def _valid_s2_core_input() -> S2CoreInput:
    return S2CoreInput(
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_nome="Lote TMJ 2025 001",
        origem_lote="upload_manual",
        total_registros_estimados=500,
        arquivos=_valid_s2_files(),
        correlation_id="s2-core-2025",
    )


def test_s2_validation_input_success_returns_contract() -> None:
    payload = _valid_s2_validation_input()
    result = validate_s2_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "s2.validation.v1"
    assert result.correlation_id == "s2-validation-2025"
    assert "evento_id" in result.checks
    assert "lote_id" in result.checks
    assert result.resumo_lote["total_arquivos_lote"] == 2
    assert result.resumo_lote["total_bytes_lote"] == 3072
    assert result.observabilidade["validation_started_event_id"].startswith("obs-")
    assert result.observabilidade["validation_completed_event_id"].startswith("obs-")


def test_s2_validation_input_rejects_invalid_lote_id() -> None:
    payload = _valid_s2_validation_input()
    payload = S2ValidationInput(
        evento_id=payload.evento_id,
        lote_id="lote@invalido",
        lote_nome=payload.lote_nome,
        origem_lote=payload.origem_lote,
        total_registros_estimados=payload.total_registros_estimados,
        arquivos=payload.arquivos,
        correlation_id="s2-validation-invalid-lote",
    )

    with pytest.raises(S2ValidationError) as exc:
        validate_s2_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_LOTE_ID"
    assert "identificador de lote estavel" in error.action
    assert error.correlation_id == "s2-validation-invalid-lote"
    assert (error.observability_event_id or "").startswith("obs-")


def test_s2_validation_input_rejects_invalid_checksum() -> None:
    payload = _valid_s2_validation_input()
    payload = S2ValidationInput(
        evento_id=payload.evento_id,
        lote_id=payload.lote_id,
        lote_nome=payload.lote_nome,
        origem_lote=payload.origem_lote,
        total_registros_estimados=payload.total_registros_estimados,
        arquivos=(
            S2FileMetadata(
                nome_arquivo=payload.arquivos[0].nome_arquivo,
                tamanho_arquivo_bytes=payload.arquivos[0].tamanho_arquivo_bytes,
                content_type=payload.arquivos[0].content_type,
                checksum_sha256="invalido",
            ),
            payload.arquivos[1],
        ),
        correlation_id="s2-validation-invalid-checksum",
    )

    with pytest.raises(S2ValidationError) as exc:
        validate_s2_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_CHECKSUM_SHA256"
    assert "Recalcule o checksum SHA-256" in error.action
    assert (error.observability_event_id or "").startswith("obs-")


def test_s2_validation_logs_actionable_warning_on_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.ingestao_inteligente.s2")
    payload = _valid_s2_validation_input()
    payload = S2ValidationInput(
        evento_id=0,
        lote_id=payload.lote_id,
        lote_nome=payload.lote_nome,
        origem_lote=payload.origem_lote,
        total_registros_estimados=payload.total_registros_estimados,
        arquivos=payload.arquivos,
        correlation_id="s2-validation-log-error",
    )

    with pytest.raises(S2ValidationError):
        validate_s2_input_contract(payload)

    assert any(
        record.message == "ingestao_inteligente_s2_validation_error"
        and getattr(record, "error_code", "") == "INVALID_EVENTO_ID"
        for record in caplog.records
    )


def test_s2_validation_and_core_flow_contract_integration() -> None:
    payload = _valid_s2_validation_input()
    validation_result = validate_s2_input_contract(payload)

    def fake_send_backend(endpoint: str, upload_payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s2/lote/upload"
        return {
            "status": "accepted",
            "lote_upload_id": "lot-integration-001",
            "evento_id": int(upload_payload["evento_id"]),
            "lote_id": str(upload_payload["lote_id"]),
            "proxima_acao": "aguardar_processamento_lote",
        }

    core_output = execute_s2_main_flow(
        payload.to_core_input(),
        send_backend=fake_send_backend,
    ).to_dict()

    output_validation = validate_s2_flow_output_contract(
        core_output,
        correlation_id=validation_result.correlation_id,
    )

    assert output_validation.status == "valid"
    assert "lote_upload_id" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("s2evt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("s2evt-")


def test_s2_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S2ValidationError) as exc:
        validate_s2_flow_output_contract(
            {"status": "accepted"},
            correlation_id="s2-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint 2" in error.action
    assert (error.observability_event_id or "").startswith("obs-")


def test_s2_core_main_flow_success_returns_contract() -> None:
    flow_input = _valid_s2_core_input()

    def fake_send_backend(endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s2/lote/upload"
        assert payload["total_arquivos_lote"] == 2
        assert payload["total_bytes_lote"] == 3072
        return {
            "status": "accepted",
            "lote_upload_id": "lot-integration-001",
            "evento_id": int(payload["evento_id"]),
            "lote_id": str(payload["lote_id"]),
            "proxima_acao": "aguardar_processamento_lote",
        }

    output = execute_s2_main_flow(flow_input, send_backend=fake_send_backend).to_dict()

    assert output["contrato_versao"] == "s2.v1"
    assert output["correlation_id"] == "s2-core-2025"
    assert output["status"] == "accepted"
    assert output["evento_id"] == 2025
    assert output["lote_id"] == "lote_tmj_2025_001"
    assert output["lote_upload_id"] == "lot-integration-001"
    assert output["proxima_acao"] == "aguardar_processamento_lote"
    assert output["pontos_integracao"]["s2_scaffold_endpoint"] == "/internal/ingestao-inteligente/s2/scaffold"
    assert output["pontos_integracao"]["s2_lote_upload_endpoint"] == "/internal/ingestao-inteligente/s2/lote/upload"
    assert output["observabilidade"]["flow_started_event_id"].startswith("s2evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("s2evt-")


def test_s2_core_main_flow_raises_actionable_error_for_invalid_scaffold_input() -> None:
    flow_input = _valid_s2_core_input()
    flow_input = S2CoreInput(
        evento_id=flow_input.evento_id,
        lote_id="lote@invalido",
        lote_nome=flow_input.lote_nome,
        origem_lote=flow_input.origem_lote,
        total_registros_estimados=flow_input.total_registros_estimados,
        arquivos=flow_input.arquivos,
        correlation_id="s2-core-invalid-scaffold",
    )

    with pytest.raises(S2CoreFlowError) as exc:
        execute_s2_main_flow(flow_input, send_backend=lambda _endpoint, _payload: {})

    error = exc.value
    assert error.code == "INVALID_LOTE_ID"
    assert "identificador de lote estavel" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("s2evt-")


def test_s2_core_main_flow_rejects_incomplete_backend_response() -> None:
    flow_input = _valid_s2_core_input()

    def fake_send_backend(_endpoint: str, _payload: dict[str, object]) -> dict[str, object]:
        return {"status": "accepted"}

    with pytest.raises(S2CoreFlowError) as exc:
        execute_s2_main_flow(flow_input, send_backend=fake_send_backend)

    error = exc.value
    assert error.code == "INCOMPLETE_S2_LOTE_UPLOAD_RESPONSE"
    assert "contrato s2.v1" in error.action
    assert error.stage == "response_validation"


def test_s2_core_main_flow_rejects_backend_lote_id_mismatch() -> None:
    flow_input = _valid_s2_core_input()

    def fake_send_backend(_endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        return {
            "status": "accepted",
            "lote_upload_id": "lot-mismatch-001",
            "evento_id": int(payload["evento_id"]),
            "lote_id": "lote_diferente",
            "proxima_acao": "aguardar_processamento_lote",
        }

    with pytest.raises(S2CoreFlowError) as exc:
        execute_s2_main_flow(flow_input, send_backend=fake_send_backend)

    error = exc.value
    assert error.code == "S2_LOTE_ID_MISMATCH"
    assert "Alinhar lote_id de resposta" in error.action
    assert error.stage == "response_validation"
