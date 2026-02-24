"""Validation and core-flow tests for Sprint 4 smart-ingestion contracts."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

import pytest


NPBB_ROOT = Path(__file__).resolve().parents[1]
if str(NPBB_ROOT) not in sys.path:
    sys.path.insert(0, str(NPBB_ROOT))

from frontend.src.features.ingestao_inteligente.s4_core import (  # noqa: E402
    S4CoreFlowError,
    S4CoreInput,
    execute_s4_main_flow,
)
from frontend.src.features.ingestao_inteligente.s4_validation import (  # noqa: E402
    S4ValidationError,
    S4ValidationInput,
    validate_s4_flow_output_contract,
    validate_s4_input_contract,
)


def _valid_s4_core_input() -> S4CoreInput:
    return S4CoreInput(
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123def456",
        status_processamento="processing",
        proxima_acao="monitorar_status_lote",
        leitor_tela_ativo=True,
        alto_contraste_ativo=False,
        reduzir_movimento=True,
        correlation_id="s4-core-2025",
    )


def _valid_s4_validation_input() -> S4ValidationInput:
    return S4ValidationInput(
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123def456",
        status_processamento="processing",
        proxima_acao="monitorar_status_lote",
        leitor_tela_ativo=True,
        alto_contraste_ativo=False,
        reduzir_movimento=True,
        correlation_id="s4-validation-2025",
    )


def _build_valid_s4_ux_response(payload: dict[str, object], *, status: str = "ok") -> dict[str, object]:
    return {
        "status": status,
        "evento_id": int(payload["evento_id"]),
        "lote_id": str(payload["lote_id"]),
        "lote_upload_id": str(payload["lote_upload_id"]),
        "status_processamento": "processing",
        "proxima_acao": "monitorar_status_lote",
        "mensagem_acionavel": {
            "codigo_mensagem": "S4_MONITORING_IN_PROGRESS",
            "titulo": "Monitoramento em andamento",
            "mensagem": "O lote segue em processamento.",
            "acao_recomendada": "Manter polling de status ate o estado terminal.",
            "severidade": "info",
        },
        "acessibilidade": {
            "leitor_tela_ativo": True,
            "alto_contraste_ativo": False,
            "reduzir_movimento": True,
            "aria_live": "polite",
            "foco_inicial": "banner_mensagem_acionavel",
        },
        "experiencia_usuario": {
            "exibir_banner_acao": True,
            "destino_acao_principal": "manter_monitoramento_status",
            "prioridade_exibicao": "medium",
        },
    }


def test_s4_validation_input_success_returns_contract() -> None:
    payload = _valid_s4_validation_input()
    result = validate_s4_input_contract(payload)

    assert result.status == "valid"
    assert result.validation_version == "s4.validation.v1"
    assert result.correlation_id == "s4-validation-2025"
    assert "evento_id" in result.checks
    assert "proxima_acao" in result.checks
    assert result.resumo_ux["status_processamento"] == "processing"
    assert result.resumo_ux["codigo_mensagem_esperado"] == "S4_MONITORING_IN_PROGRESS"
    assert result.observabilidade["validation_started_event_id"].startswith("obs-")
    assert result.observabilidade["validation_completed_event_id"].startswith("obs-")


def test_s4_validation_input_rejects_invalid_proxima_acao() -> None:
    payload = _valid_s4_validation_input()
    payload = S4ValidationInput(
        evento_id=payload.evento_id,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        proxima_acao="acao_invalida",
        leitor_tela_ativo=payload.leitor_tela_ativo,
        alto_contraste_ativo=payload.alto_contraste_ativo,
        reduzir_movimento=payload.reduzir_movimento,
        correlation_id="s4-validation-invalid-action",
    )

    with pytest.raises(S4ValidationError) as exc:
        validate_s4_input_contract(payload)

    error = exc.value
    assert error.code == "INVALID_PROXIMA_ACAO"
    assert "proxima_acao valida" in error.action
    assert error.correlation_id == "s4-validation-invalid-action"
    assert (error.observability_event_id or "").startswith("obs-")


def test_s4_validation_logs_actionable_warning_on_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="npbb.ingestao_inteligente.s4")
    payload = _valid_s4_validation_input()
    payload = S4ValidationInput(
        evento_id=0,
        lote_id=payload.lote_id,
        lote_upload_id=payload.lote_upload_id,
        status_processamento=payload.status_processamento,
        proxima_acao=payload.proxima_acao,
        leitor_tela_ativo=payload.leitor_tela_ativo,
        alto_contraste_ativo=payload.alto_contraste_ativo,
        reduzir_movimento=payload.reduzir_movimento,
        correlation_id="s4-validation-log-error",
    )

    with pytest.raises(S4ValidationError):
        validate_s4_input_contract(payload)

    assert any(
        record.message == "ingestao_inteligente_s4_validation_error"
        and getattr(record, "error_code", "") == "INVALID_EVENTO_ID"
        for record in caplog.records
    )


def test_s4_validation_and_core_flow_contract_integration() -> None:
    payload = _valid_s4_validation_input()
    validation_result = validate_s4_input_contract(payload)

    def fake_send_backend(endpoint: str, ux_payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s4/ux"
        assert ux_payload["lote_upload_id"] == "lot-abc123def456"
        return _build_valid_s4_ux_response(ux_payload)

    core_output = execute_s4_main_flow(
        payload.to_core_input(),
        send_backend=fake_send_backend,
    ).to_dict()

    output_validation = validate_s4_flow_output_contract(
        core_output,
        correlation_id=validation_result.correlation_id,
    )

    assert output_validation.status == "valid"
    assert "mensagem_acionavel" in output_validation.checked_fields
    assert output_validation.observabilidade["flow_started_event_id"].startswith("s4evt-")
    assert output_validation.observabilidade["flow_completed_event_id"].startswith("s4evt-")


def test_s4_validation_flow_output_rejects_missing_required_fields() -> None:
    with pytest.raises(S4ValidationError) as exc:
        validate_s4_flow_output_contract(
            {"status": "ok"},
            correlation_id="s4-output-invalid",
        )

    error = exc.value
    assert error.code == "INCOMPLETE_FLOW_OUTPUT"
    assert "contrato completo da sprint 4" in error.action
    assert (error.observability_event_id or "").startswith("obs-")


def test_s4_core_main_flow_success_returns_contract() -> None:
    flow_input = _valid_s4_core_input()

    def fake_send_backend(endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        assert endpoint == "/internal/ingestao-inteligente/s4/ux"
        assert payload["lote_upload_id"] == "lot-abc123def456"
        return _build_valid_s4_ux_response(payload, status="ready")

    output = execute_s4_main_flow(flow_input, send_backend=fake_send_backend).to_dict()

    assert output["contrato_versao"] == "s4.v1"
    assert output["correlation_id"] == "s4-core-2025"
    assert output["status"] == "ready"
    assert output["evento_id"] == 2025
    assert output["lote_id"] == "lote_tmj_2025_001"
    assert output["lote_upload_id"] == "lot-abc123def456"
    assert output["status_processamento"] == "processing"
    assert output["proxima_acao"] == "monitorar_status_lote"
    assert output["mensagem_acionavel"]["codigo_mensagem"] == "S4_MONITORING_IN_PROGRESS"
    assert output["acessibilidade"]["aria_live"] == "polite"
    assert output["experiencia_usuario"]["prioridade_exibicao"] == "medium"
    assert output["observabilidade"]["flow_started_event_id"].startswith("s4evt-")
    assert output["observabilidade"]["ux_dispatch_event_id"].startswith("s4evt-")
    assert output["observabilidade"]["flow_completed_event_id"].startswith("s4evt-")


def test_s4_core_main_flow_rejects_incomplete_backend_response() -> None:
    flow_input = _valid_s4_core_input()

    def fake_send_backend(_endpoint: str, _payload: dict[str, object]) -> dict[str, object]:
        return {"status": "ok"}

    with pytest.raises(S4CoreFlowError) as exc:
        execute_s4_main_flow(flow_input, send_backend=fake_send_backend)

    error = exc.value
    assert error.code == "INCOMPLETE_S4_UX_RESPONSE"
    assert "endpoint /s4/ux" in error.action
    assert error.stage == "ux_response_validation"


def test_s4_core_main_flow_raises_actionable_error_for_invalid_scaffold_input() -> None:
    flow_input = _valid_s4_core_input()
    flow_input = S4CoreInput(
        evento_id=flow_input.evento_id,
        lote_id=flow_input.lote_id,
        lote_upload_id="id-invalido",
        status_processamento=flow_input.status_processamento,
        proxima_acao=flow_input.proxima_acao,
        leitor_tela_ativo=flow_input.leitor_tela_ativo,
        alto_contraste_ativo=flow_input.alto_contraste_ativo,
        reduzir_movimento=flow_input.reduzir_movimento,
        correlation_id="s4-core-invalid-scaffold",
    )

    with pytest.raises(S4CoreFlowError) as exc:
        execute_s4_main_flow(flow_input, send_backend=lambda _endpoint, _payload: {})

    error = exc.value
    assert error.code == "INVALID_LOTE_UPLOAD_ID"
    assert "identificador retornado pelo endpoint /s2/lote/upload" in error.action
    assert error.stage == "scaffold"
    assert (error.event_id or "").startswith("s4evt-")
