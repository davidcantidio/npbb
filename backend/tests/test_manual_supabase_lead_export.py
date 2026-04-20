from __future__ import annotations

import csv
from datetime import date, datetime, time, timezone
import json
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.services import manual_supabase_lead_export as manual_export
from app.services.manual_supabase_lead_export import (
    FrozenBatchSpec,
    MaterializedBatch,
    build_rejected_audit_rows,
    build_ticketing_key,
    normalize_ticketing_value,
    run_manual_supabase_lead_export,
    serialize_lead_value,
)
from lead_pipeline.pipeline import PipelineResult


def _make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return Session(engine)


def _make_batch(file_name: str, batch_id: int = 188) -> MaterializedBatch:
    ts = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)
    batch = LeadBatch(
        id=batch_id,
        enviado_por=1,
        plataforma_origem="drive",
        data_envio=ts,
        data_upload=ts,
        nome_arquivo_original=file_name,
        arquivo_sha256="sha256",
        stage=BatchStage.GOLD,
        evento_id=99,
        pipeline_status=PipelineStatus.PASS_WITH_WARNINGS,
    )
    return MaterializedBatch(
        spec=FrozenBatchSpec(file_name=file_name, arquivo_sha256="sha256", batch_id=batch_id),
        batch=batch,
        silver_csv_path=Path("unused.csv"),
        silver_rows=3,
    )


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_pipeline_fixture(
    root: Path,
    *,
    file_name: str,
    raw_rows: list[dict[str, str]],
    consolidated_rows: list[dict[str, str]],
    invalid_records: list[dict[str, object]],
) -> PipelineResult:
    output_dir = root / "pipeline-output"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw.csv"
    consolidated_path = output_dir / "leads_multieventos_2025.csv"
    report_path = output_dir / "report.json"
    summary_path = output_dir / "validation-summary.md"

    _write_csv(
        raw_path,
        ["source_file", "source_sheet", "source_row"],
        raw_rows,
    )
    _write_csv(
        consolidated_path,
        [
            "nome",
            "cpf",
            "data_nascimento",
            "email",
            "telefone",
            "evento",
            "local",
            "id_salesforce",
            "sobrenome",
            "sessao",
            "data_compra",
            "data_compra_data",
            "data_compra_hora",
            "opt_in",
            "opt_in_id",
            "opt_in_flag",
            "metodo_entrega",
            "rg",
            "endereco_rua",
            "endereco_numero",
            "complemento",
            "bairro",
            "cep",
            "cidade",
            "estado",
            "genero",
            "codigo_promocional",
            "ingresso_tipo",
            "ingresso_qtd",
            "fonte_origem",
            "is_cliente_bb",
            "is_cliente_estilo",
        ],
        consolidated_rows,
    )
    report_path.write_text(
        json.dumps(
            {
                "invalid_records": invalid_records,
                "totals": {
                    "raw_rows": len(raw_rows),
                    "valid_rows": len(consolidated_rows),
                    "discarded_rows": len(invalid_records),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    summary_path.write_text("ok\n", encoding="utf-8")

    return PipelineResult(
        lote_id="manual_supabase_import_2026-04-20",
        status="PASS_WITH_WARNINGS",
        decision="promote",
        output_dir=output_dir,
        report_path=report_path,
        summary_path=summary_path,
        consolidated_path=consolidated_path,
        exit_code=0,
    )


def test_build_ticketing_key_requires_cpf() -> None:
    assert build_ticketing_key(
        email="lead@example.com",
        cpf="",
        evento_nome="Evento",
        sessao="Sessao",
    ) is None


def test_build_ticketing_key_normalizes_whitespace() -> None:
    assert build_ticketing_key(
        email=" lead@example.com ",
        cpf=" 123 ",
        evento_nome=" Evento ",
        sessao=" Sessao ",
    ) == "lead@example.com|123|Evento|Sessao"


def test_normalize_ticketing_value_handles_none() -> None:
    assert normalize_ticketing_value(None) == ""


def test_serialize_lead_value_formats_supported_types() -> None:
    aware = datetime(2026, 4, 20, 13, 45, 59, tzinfo=timezone.utc)
    with_microseconds = datetime(2026, 4, 20, 13, 45, 59, 123456, tzinfo=timezone.utc)
    assert serialize_lead_value(True) == "true"
    assert serialize_lead_value(False) == "false"
    assert serialize_lead_value(date(2026, 4, 20)) == "2026-04-20"
    assert serialize_lead_value(time(13, 45, 59)) == "13:45:59"
    assert serialize_lead_value(aware) == "2026-04-20 13:45:59"
    assert serialize_lead_value(with_microseconds) == "2026-04-20 13:45:59.123456"


@pytest.mark.parametrize(
    ("mode", "expect_delta", "expect_full"),
    [
        ("delta", True, False),
        ("full", False, True),
        ("both", True, True),
    ],
)
def test_run_manual_supabase_lead_export_respects_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    mode: str,
    expect_delta: bool,
    expect_full: bool,
) -> None:
    file_name = "Arquivo.xlsx"
    materialized_batch = _make_batch(file_name)
    pipeline_result = _write_pipeline_fixture(
        tmp_path,
        file_name=file_name,
        raw_rows=[
            {"source_file": file_name, "source_sheet": "Sheet1", "source_row": "2"},
        ],
        consolidated_rows=[
            {
                "nome": "Lead New",
                "cpf": "12345678901",
                "data_nascimento": "1990-01-01",
                "email": "new@example.com",
                "telefone": "11999999999",
                "evento": "Evento A",
                "local": "Sessao A",
                "id_salesforce": "",
                "sobrenome": "",
                "sessao": "Sessao A",
                "data_compra": "",
                "data_compra_data": "",
                "data_compra_hora": "",
                "opt_in": "",
                "opt_in_id": "",
                "opt_in_flag": "",
                "metodo_entrega": "",
                "rg": "",
                "endereco_rua": "",
                "endereco_numero": "",
                "complemento": "",
                "bairro": "",
                "cep": "",
                "cidade": "",
                "estado": "",
                "genero": "",
                "codigo_promocional": "",
                "ingresso_tipo": "",
                "ingresso_qtd": "",
                "fonte_origem": "drive",
                "is_cliente_bb": "",
                "is_cliente_estilo": "",
            },
        ],
        invalid_records=[],
    )

    monkeypatch.setattr(
        manual_export,
        "materialize_frozen_batches",
        lambda db: [materialized_batch],
    )
    monkeypatch.setattr(manual_export, "run_pipeline", lambda config: pipeline_result)
    monkeypatch.setattr(
        manual_export,
        "fetch_existing_conflicts",
        lambda db, candidates: (set(), set()),
    )

    with _make_session() as session:
        artifacts = run_manual_supabase_lead_export(
            db=session,
            output_dir=tmp_path / f"out-{mode}",
            export_date="2026-04-20",
            lote_id="manual_supabase_import_2026-04-20",
            mode=mode,
        )

    assert (artifacts.import_csv_path is not None) is expect_delta
    assert (artifacts.full_import_csv_path is not None) is expect_full
    if expect_delta:
        assert artifacts.import_csv_path is not None and artifacts.import_csv_path.exists()
    if expect_full:
        assert artifacts.full_import_csv_path is not None and artifacts.full_import_csv_path.exists()
    assert artifacts.reconciliation_csv_path.exists()
    assert artifacts.rejected_rows_csv_path.exists()

    manifest = json.loads(artifacts.manifest_path.read_text(encoding="utf-8"))
    assert manifest["mode"] == mode
    assert manifest["summary"]["full_rows"] == 1
    assert manifest["summary"]["import_ready_rows"] == 1
    assert manifest["summary"]["skipped_existing_rows"] == 0


def test_run_manual_supabase_lead_export_builds_reconciliation_and_rejection_audits(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    file_name = "Arquivo.xlsx"
    materialized_batch = _make_batch(file_name, batch_id=244)
    pipeline_result = _write_pipeline_fixture(
        tmp_path,
        file_name=file_name,
        raw_rows=[
            {"source_file": file_name, "source_sheet": "Sheet1", "source_row": "2"},
            {"source_file": file_name, "source_sheet": "Sheet1", "source_row": "3"},
            {"source_file": file_name, "source_sheet": "Sheet1", "source_row": "4"},
        ],
        consolidated_rows=[
            {
                "nome": "Lead Existing",
                "cpf": "11111111111",
                "data_nascimento": "1990-01-01",
                "email": "existing@example.com",
                "telefone": "11999999999",
                "evento": "Evento A",
                "local": "Sessao A",
                "id_salesforce": "",
                "sobrenome": "",
                "sessao": "Sessao A",
                "data_compra": "",
                "data_compra_data": "",
                "data_compra_hora": "",
                "opt_in": "",
                "opt_in_id": "",
                "opt_in_flag": "",
                "metodo_entrega": "",
                "rg": "",
                "endereco_rua": "",
                "endereco_numero": "",
                "complemento": "",
                "bairro": "",
                "cep": "",
                "cidade": "",
                "estado": "",
                "genero": "",
                "codigo_promocional": "",
                "ingresso_tipo": "",
                "ingresso_qtd": "",
                "fonte_origem": "drive",
                "is_cliente_bb": "",
                "is_cliente_estilo": "",
            },
            {
                "nome": "Lead New",
                "cpf": "22222222222",
                "data_nascimento": "1991-01-01",
                "email": "new@example.com",
                "telefone": "21999999999",
                "evento": "Evento A",
                "local": "Sessao B",
                "id_salesforce": "",
                "sobrenome": "",
                "sessao": "Sessao B",
                "data_compra": "",
                "data_compra_data": "",
                "data_compra_hora": "",
                "opt_in": "",
                "opt_in_id": "",
                "opt_in_flag": "",
                "metodo_entrega": "",
                "rg": "",
                "endereco_rua": "",
                "endereco_numero": "",
                "complemento": "",
                "bairro": "",
                "cep": "",
                "cidade": "",
                "estado": "",
                "genero": "",
                "codigo_promocional": "",
                "ingresso_tipo": "",
                "ingresso_qtd": "",
                "fonte_origem": "drive",
                "is_cliente_bb": "",
                "is_cliente_estilo": "",
            },
        ],
        invalid_records=[
            {
                "source_file": file_name,
                "source_sheet": "Sheet1",
                "source_row": 4,
                "motivo_rejeicao": "CPF_INVALIDO",
                "row_data": {
                    "nome": "Lead Rejected",
                    "cpf": "123",
                    "email": "rejected@example.com",
                    "telefone": "11999999999",
                    "evento": "Evento A",
                    "data_evento": "2026-02-27",
                    "local": "Sessao C",
                    "sessao": "",
                },
            }
        ],
    )

    monkeypatch.setattr(
        manual_export,
        "materialize_frozen_batches",
        lambda db: [materialized_batch],
    )
    monkeypatch.setattr(manual_export, "run_pipeline", lambda config: pipeline_result)
    monkeypatch.setattr(
        manual_export,
        "fetch_existing_conflicts",
        lambda db, candidates: (set(), {"existing@example.com|11111111111|Evento A|Sessao A"}),
    )

    with _make_session() as session:
        artifacts = run_manual_supabase_lead_export(
            db=session,
            output_dir=tmp_path / "out-both",
            export_date="2026-04-20",
            lote_id="manual_supabase_import_2026-04-20",
            mode="both",
        )

    assert artifacts.import_csv_path is not None
    assert artifacts.full_import_csv_path is not None

    with artifacts.import_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["email"] == "new@example.com"
    assert rows[0]["batch_id"] == "244"
    assert rows[0]["data_criacao"] != ""

    with artifacts.full_import_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        full_rows = list(csv.DictReader(handle))
    assert len(full_rows) == 2
    assert {row["batch_id"] for row in full_rows} == {"244"}
    assert len({row["data_criacao"] for row in full_rows}) == 1

    with artifacts.reconciliation_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reconciliation_rows = list(csv.DictReader(handle))
    assert reconciliation_rows == [
        {
            "file_name": file_name,
            "arquivo_sha256": "sha256",
            "batch_id": "244",
            "stage": "gold",
            "pipeline_status": "pass_with_warnings",
            "silver_rows": "3",
            "raw_rows": "3",
            "pipeline_rejected_rows": "1",
            "pipeline_accepted_rows": "2",
            "already_existing_pre_export_rows": "1",
            "delta_rows": "1",
        }
    ]

    with artifacts.rejected_rows_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rejected_rows = list(csv.DictReader(handle))
    assert len(rejected_rows) == 1
    assert rejected_rows[0]["source_file"] == file_name
    assert rejected_rows[0]["evento_nome"] == "Evento A"
    assert rejected_rows[0]["motivo_rejeicao"] == "CPF_INVALIDO"
    assert rejected_rows[0]["related_field_names"] == "cpf"
    assert '"cpf": "123"' in rejected_rows[0]["related_field_values_json"]

    manifest = json.loads(artifacts.manifest_path.read_text(encoding="utf-8"))
    assert manifest["summary"]["full_rows"] == 2
    assert manifest["summary"]["import_ready_rows"] == 1
    assert manifest["summary"]["skipped_existing_rows"] == 1
    assert manifest["summary"]["pipeline_rejected_rows"] == 1
    assert manifest["files"][0]["full_rows"] == 2
    assert manifest["files"][0]["already_existing_pre_export_rows"] == 1
    assert manifest["files"][0]["delta_rows"] == 1
    assert manifest["artifacts"]["rejected_rows_csv_path"] == str(artifacts.rejected_rows_csv_path)


def test_build_rejected_audit_rows_extracts_report_fields(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(
            {
                "invalid_records": [
                    {
                        "source_file": "Arquivo.xlsx",
                        "source_sheet": "Sheet1",
                        "source_row": 10,
                        "motivo_rejeicao": "TELEFONE_INVALIDO",
                        "row_data": {
                            "evento": "Evento B",
                            "telefone": "(11) 1234",
                            "cpf": "12345678901",
                            "nome": "Lead",
                        },
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    rows = build_rejected_audit_rows(report_path)

    assert rows == [
        {
            "source_file": "Arquivo.xlsx",
            "source_sheet": "Sheet1",
            "source_row": "10",
            "motivo_rejeicao": "TELEFONE_INVALIDO",
            "evento_nome": "Evento B",
            "related_field_names": "telefone",
            "related_field_values_json": '{"telefone": "(11) 1234"}',
            "nome": "Lead",
            "cpf": "12345678901",
            "email": "",
            "telefone": "(11) 1234",
            "data_nascimento": "",
            "data_evento": "",
            "local": "",
            "sessao": "",
            "row_data_json": '{"cpf": "12345678901", "evento": "Evento B", "nome": "Lead", "telefone": "(11) 1234"}',
        }
    ]
