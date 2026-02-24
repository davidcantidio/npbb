from __future__ import annotations

import importlib

import pytest


telemetry = importlib.import_module("app.services.interface-de-ingest-o-inteligente-frontend-_telemetry")


def test_build_s1_telemetry_event_success() -> None:
    payload = telemetry.S1TelemetryInput(
        event_name="s1_upload_received",
        correlation_id="s1-correlation-001",
        event_message="Upload recebido",
        severity="info",
        evento_id=2025,
        context={"field": "value"},
    )
    event = telemetry.build_s1_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("tel-")
    assert event.correlation_id == "s1-correlation-001"
    assert event.event_name == "s1_upload_received"
    assert event.severity == "info"
    assert event.evento_id == 2025
    assert event.context == {"field": "value"}
    assert event.to_response_dict()["telemetry_event_id"].startswith("tel-")


def test_build_s1_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S1TelemetryInput(
        event_name="s1_upload_received",
        correlation_id="s1-correlation-001",
        event_message="Upload recebido",
        severity="debug",
    )

    with pytest.raises(telemetry.S1TelemetryContractError) as exc:
        telemetry.build_s1_telemetry_event(payload)

    assert exc.value.code == "INVALID_TELEMETRY_SEVERITY"


def test_build_s1_error_detail_includes_telemetry_reference() -> None:
    detail = telemetry.build_s1_error_detail(
        code="FILE_TOO_LARGE",
        message="Arquivo excede limite",
        action="Reduza o tamanho do arquivo",
        correlation_id="s1-correlation-001",
        telemetry_event_id="tel-abc123",
        context={"tamanho_arquivo_bytes": 99999999},
    )

    assert detail["code"] == "FILE_TOO_LARGE"
    assert detail["correlation_id"] == "s1-correlation-001"
    assert detail["telemetry_event_id"] == "tel-abc123"
    assert detail["context"]["tamanho_arquivo_bytes"] == 99999999


def test_build_s2_telemetry_event_success() -> None:
    payload = telemetry.S2TelemetryInput(
        event_name="s2_lote_upload_received",
        correlation_id="s2-correlation-001",
        event_message="Lote recebido",
        severity="info",
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123",
        context={"total_arquivos_lote": 2},
    )
    event = telemetry.build_s2_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("tel-")
    assert event.correlation_id == "s2-correlation-001"
    assert event.event_name == "s2_lote_upload_received"
    assert event.severity == "info"
    assert event.evento_id == 2025
    assert event.lote_id == "lote_tmj_2025_001"
    assert event.lote_upload_id == "lot-abc123"
    assert event.context == {"total_arquivos_lote": 2}
    assert event.to_response_dict()["telemetry_event_id"].startswith("tel-")


def test_build_s2_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S2TelemetryInput(
        event_name="s2_lote_upload_received",
        correlation_id="s2-correlation-001",
        event_message="Lote recebido",
        severity="debug",
    )

    with pytest.raises(telemetry.S2TelemetryContractError) as exc:
        telemetry.build_s2_telemetry_event(payload)

    assert exc.value.code == "INVALID_S2_TELEMETRY_SEVERITY"


def test_build_s2_error_detail_includes_lot_context() -> None:
    detail = telemetry.build_s2_error_detail(
        code="BATCH_TOTAL_BYTES_MISMATCH",
        message="Total de bytes divergente",
        action="Recalcular total_bytes_lote",
        correlation_id="s2-correlation-001",
        telemetry_event_id="tel-s2-abc123",
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123",
        context={"total_bytes_lote": 999, "total_bytes_calculado": 3072},
    )

    assert detail["code"] == "BATCH_TOTAL_BYTES_MISMATCH"
    assert detail["correlation_id"] == "s2-correlation-001"
    assert detail["telemetry_event_id"] == "tel-s2-abc123"
    assert detail["context"]["lote_id"] == "lote_tmj_2025_001"
    assert detail["context"]["lote_upload_id"] == "lot-abc123"
    assert detail["context"]["total_bytes_lote"] == 999


def test_build_s3_telemetry_event_success() -> None:
    payload = telemetry.S3TelemetryInput(
        event_name="s3_status_received",
        correlation_id="s3-correlation-001",
        event_message="Monitoramento recebido",
        severity="info",
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="LOT-ABC123",
        reprocessamento_id="rep-xyz123",
        context={"status_processamento": "failed"},
    )
    event = telemetry.build_s3_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("tel-")
    assert event.correlation_id == "s3-correlation-001"
    assert event.event_name == "s3_status_received"
    assert event.severity == "info"
    assert event.evento_id == 2025
    assert event.lote_id == "lote_tmj_2025_001"
    assert event.lote_upload_id == "lot-abc123"
    assert event.reprocessamento_id == "rep-xyz123"
    assert event.context == {"status_processamento": "failed"}
    assert event.to_response_dict()["telemetry_event_id"].startswith("tel-")


def test_build_s3_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S3TelemetryInput(
        event_name="s3_status_received",
        correlation_id="s3-correlation-001",
        event_message="Monitoramento recebido",
        severity="debug",
    )

    with pytest.raises(telemetry.S3TelemetryContractError) as exc:
        telemetry.build_s3_telemetry_event(payload)

    assert exc.value.code == "INVALID_S3_TELEMETRY_SEVERITY"


def test_build_s3_error_detail_includes_reprocess_context() -> None:
    detail = telemetry.build_s3_error_detail(
        code="S3_REPROCESS_INTERNAL_ERROR",
        message="Falha no reprocessamento",
        action="Consultar logs de reprocessamento",
        correlation_id="s3-correlation-001",
        telemetry_event_id="tel-s3-abc123",
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123",
        reprocessamento_id="rep-xyz123",
        context={"status_processamento": "failed"},
    )

    assert detail["code"] == "S3_REPROCESS_INTERNAL_ERROR"
    assert detail["correlation_id"] == "s3-correlation-001"
    assert detail["telemetry_event_id"] == "tel-s3-abc123"
    assert detail["context"]["lote_id"] == "lote_tmj_2025_001"
    assert detail["context"]["lote_upload_id"] == "lot-abc123"
    assert detail["context"]["reprocessamento_id"] == "rep-xyz123"
    assert detail["context"]["status_processamento"] == "failed"


def test_build_s4_telemetry_event_success() -> None:
    payload = telemetry.S4TelemetryInput(
        event_name="s4_ux_payload_ready",
        correlation_id="s4-correlation-001",
        event_message="Payload de UX final preparado",
        severity="info",
        evento_id=2025,
        lote_id="lote_tmj_2025_001",
        lote_upload_id="LOT-ABC123",
        codigo_mensagem="S4_REPROCESS_RECOMMENDED",
        destino_acao_principal="abrir_modal_reprocessamento",
        context={"prioridade_exibicao": "high"},
    )
    event = telemetry.build_s4_telemetry_event(payload)

    assert event.telemetry_event_id.startswith("tel-")
    assert event.correlation_id == "s4-correlation-001"
    assert event.event_name == "s4_ux_payload_ready"
    assert event.severity == "info"
    assert event.evento_id == 2025
    assert event.lote_id == "lote_tmj_2025_001"
    assert event.lote_upload_id == "lot-abc123"
    assert event.codigo_mensagem == "S4_REPROCESS_RECOMMENDED"
    assert event.destino_acao_principal == "abrir_modal_reprocessamento"
    assert event.context == {"prioridade_exibicao": "high"}
    assert event.to_response_dict()["telemetry_event_id"].startswith("tel-")


def test_build_s4_telemetry_event_rejects_invalid_severity() -> None:
    payload = telemetry.S4TelemetryInput(
        event_name="s4_ux_payload_ready",
        correlation_id="s4-correlation-001",
        event_message="Payload de UX final preparado",
        severity="debug",
    )

    with pytest.raises(telemetry.S4TelemetryContractError) as exc:
        telemetry.build_s4_telemetry_event(payload)

    assert exc.value.code == "INVALID_S4_TELEMETRY_SEVERITY"


def test_build_s4_error_detail_includes_ux_context() -> None:
    detail = telemetry.build_s4_error_detail(
        code="S4_UX_INTERNAL_ERROR",
        message="Falha ao preparar UX final",
        action="Consultar logs de UX final",
        correlation_id="s4-correlation-001",
        telemetry_event_id="tel-s4-abc123",
        lote_id="lote_tmj_2025_001",
        lote_upload_id="lot-abc123",
        codigo_mensagem="S4_REPROCESS_RECOMMENDED",
        destino_acao_principal="abrir_modal_reprocessamento",
        context={"status_processamento": "failed"},
    )

    assert detail["code"] == "S4_UX_INTERNAL_ERROR"
    assert detail["correlation_id"] == "s4-correlation-001"
    assert detail["telemetry_event_id"] == "tel-s4-abc123"
    assert detail["context"]["lote_id"] == "lote_tmj_2025_001"
    assert detail["context"]["lote_upload_id"] == "lot-abc123"
    assert detail["context"]["codigo_mensagem"] == "S4_REPROCESS_RECOMMENDED"
    assert detail["context"]["destino_acao_principal"] == "abrir_modal_reprocessamento"
    assert detail["context"]["status_processamento"] == "failed"
