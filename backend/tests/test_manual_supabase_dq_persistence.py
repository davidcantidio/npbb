from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlmodel import Session

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Usuario
from app.services.manual_supabase_frozen_batches import FrozenBatchSpec
from app.services.manual_supabase_dq_persistence import (
    BATCH255_BATCH_ID,
    batch_has_existing_dq_snapshot,
    build_batch255_synthetic_report,
    build_quality_metrics_for_source_file,
    build_sliced_pipeline_report_for_source_file,
    gold_dq_snapshot_from_report,
    persist_batch255_manual_dq,
    persist_consolidated_manual_dq,
)


FILE_A = "Arquivo Teste A.xlsx"


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="dq-persist@test.npbb",
        password_hash="x",
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _minimal_report(*, invalid_for_a: list[dict]) -> dict:
    return {
        "lote_id": "test",
        "totals": {"raw_rows": 100, "valid_rows": 90, "discarded_rows": 10},
        "quality_metrics": {k: 0 for k in [
            "cpf_invalid_discarded", "telefone_invalid", "data_evento_invalid",
            "data_nascimento_invalid", "data_nascimento_missing", "duplicidades_cpf_evento",
            "cidade_fora_mapeamento", "localidade_invalida", "localidade_nao_resolvida",
            "localidade_fora_brasil", "localidade_cidade_uf_inconsistente",
        ]},
        "invalid_records": invalid_for_a,
        "data_nascimento_controle": [],
        "localidade_controle": [],
        "cidade_fora_mapeamento_controle": [],
        "gate": {"status": "PASS", "decision": "promote", "fail_reasons": [], "warnings": []},
    }


def test_build_quality_metrics_from_invalid_motivos() -> None:
    full = _minimal_report(
        invalid_for_a=[
            {
                "source_file": FILE_A,
                "source_sheet": "S1",
                "source_row": 2,
                "motivo_rejeicao": "CPF_INVALIDO;TELEFONE_INVALIDO",
                "row_data": {},
            },
            {
                "source_file": FILE_A,
                "source_sheet": "S1",
                "source_row": 3,
                "motivo_rejeicao": "DUPLICIDADE_CPF_EVENTO",
                "row_data": {},
            },
        ],
    )
    m = build_quality_metrics_for_source_file(full, FILE_A)
    assert m["cpf_invalid_discarded"] == 1
    assert m["telefone_invalid"] == 1
    assert m["duplicidades_cpf_evento"] == 1


def test_build_sliced_report_totals() -> None:
    full = _minimal_report(
        invalid_for_a=[
            {
                "source_file": FILE_A,
                "source_sheet": "S1",
                "source_row": 2,
                "motivo_rejeicao": "CPF_INVALIDO",
                "row_data": {},
            },
        ],
    )
    full["invalid_records"] = full["invalid_records"] + [
        {
            "source_file": "Outro.xlsx",
            "source_sheet": "S1",
            "source_row": 9,
            "motivo_rejeicao": "CPF_INVALIDO",
            "row_data": {},
        },
    ]
    sliced = build_sliced_pipeline_report_for_source_file(full, source_file=FILE_A, raw_rows=10)
    assert sliced["totals"]["raw_rows"] == 10
    assert sliced["totals"]["discarded_rows"] == 1
    assert sliced["totals"]["valid_rows"] == 9
    assert len(sliced["invalid_records"]) == 1


def test_batch_has_existing_dq_snapshot() -> None:
    ts = datetime(2026, 4, 20, tzinfo=timezone.utc)
    batch = LeadBatch(
        id=1,
        enviado_por=1,
        plataforma_origem="x",
        data_envio=ts,
        nome_arquivo_original="f.csv",
        stage=BatchStage.GOLD,
        pipeline_status=PipelineStatus.PASS,
    )
    assert not batch_has_existing_dq_snapshot(batch)
    batch.pipeline_report = {}
    assert batch_has_existing_dq_snapshot(batch)
    batch.pipeline_report = None
    batch.gold_dq_discarded_rows = 0
    assert batch_has_existing_dq_snapshot(batch)


def test_build_batch255_synthetic_report_matches_snapshot() -> None:
    manifest = {
        "summary": {
            "raw_rows": 100,
            "final_rows": 80,
            "document_blank": 5,
            "internal_duplicates_skipped": 2,
            "existing_conflicts_skipped": 3,
        }
    }
    rep = build_batch255_synthetic_report(manifest)
    disc, issues, inv_n = gold_dq_snapshot_from_report(rep)
    assert disc == 20
    assert issues is not None
    assert issues.get("document_blank") == 5
    assert inv_n == 0


def test_persist_consolidated_updates_batch(db_session: Session, tmp_path: Path) -> None:
    user = _seed_user(db_session)
    batch_id = 99100
    batch = LeadBatch(
        id=batch_id,
        enviado_por=int(user.id),
        plataforma_origem="manual",
        data_envio=datetime(2026, 4, 20, tzinfo=timezone.utc),
        nome_arquivo_original=FILE_A,
        arquivo_sha256="ab" * 32,
        stage=BatchStage.GOLD,
        evento_id=1,
        pipeline_status=PipelineStatus.PASS_WITH_WARNINGS,
    )
    db_session.add(batch)
    db_session.commit()

    report = _minimal_report(
        invalid_for_a=[
            {
                "source_file": FILE_A,
                "source_sheet": "S1",
                "source_row": 2,
                "motivo_rejeicao": "CPF_INVALIDO",
                "row_data": {},
            },
        ],
    )
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    manifest = {
        "files": [
            {
                "file_name": FILE_A,
                "batch_id": batch_id,
                "raw_rows": 5,
            },
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    one_spec = (
        FrozenBatchSpec(file_name=FILE_A, arquivo_sha256=batch.arquivo_sha256 or "", batch_id=batch_id),
    )
    with patch(
        "app.services.manual_supabase_dq_persistence.FROZEN_BATCH_SPECS",
        one_spec,
    ):
        out = persist_consolidated_manual_dq(
            db_session,
            report_path=report_path,
            manifest_path=manifest_path,
            dry_run=False,
        )

    assert not out["errors"]
    assert any(u["batch_id"] == batch_id for u in out["updated"])
    db_session.refresh(batch)
    assert batch.pipeline_report is not None
    assert batch.gold_dq_discarded_rows == 1
    assert batch.gold_dq_invalid_records_total == 1


def test_persist_consolidated_skips_when_snapshot_exists(db_session: Session, tmp_path: Path) -> None:
    user = _seed_user(db_session)
    batch_id = 99101
    batch = LeadBatch(
        id=batch_id,
        enviado_por=int(user.id),
        plataforma_origem="manual",
        data_envio=datetime(2026, 4, 20, tzinfo=timezone.utc),
        nome_arquivo_original=FILE_A,
        stage=BatchStage.GOLD,
        evento_id=1,
        pipeline_status=PipelineStatus.PASS,
        pipeline_report={"existing": True},
    )
    db_session.add(batch)
    db_session.commit()

    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(_minimal_report(invalid_for_a=[])), encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps({"files": [{"file_name": FILE_A, "batch_id": batch_id, "raw_rows": 1}]}),
        encoding="utf-8",
    )

    one_spec = (FrozenBatchSpec(file_name=FILE_A, arquivo_sha256="c" * 64, batch_id=batch_id),)
    with patch("app.services.manual_supabase_dq_persistence.FROZEN_BATCH_SPECS", one_spec):
        out = persist_consolidated_manual_dq(
            db_session,
            report_path=report_path,
            manifest_path=manifest_path,
            dry_run=False,
        )

    assert any(s["batch_id"] == batch_id and s["reason"] == "existing_dq_snapshot" for s in out["skipped"])
    db_session.refresh(batch)
    assert batch.pipeline_report == {"existing": True}


def test_persist_batch255_updates(db_session: Session, tmp_path: Path) -> None:
    user = _seed_user(db_session)
    batch = LeadBatch(
        id=BATCH255_BATCH_ID,
        enviado_por=int(user.id),
        plataforma_origem="manual",
        data_envio=datetime(2026, 4, 20, tzinfo=timezone.utc),
        nome_arquivo_original="f.csv",
        stage=BatchStage.GOLD,
        evento_id=1,
        pipeline_status=PipelineStatus.PASS,
    )
    db_session.add(batch)
    db_session.commit()

    manifest_path = tmp_path / "m255.json"
    manifest_path.write_text(
        json.dumps(
            {
                "summary": {
                    "raw_rows": 50,
                    "final_rows": 40,
                    "document_blank": 2,
                    "internal_duplicates_skipped": 1,
                    "existing_conflicts_skipped": 1,
                }
            }
        ),
        encoding="utf-8",
    )

    out = persist_batch255_manual_dq(db_session, manifest_path=manifest_path, dry_run=False)
    assert out["updated"]
    db_session.refresh(batch)
    assert batch.pipeline_report is not None
    assert batch.gold_dq_discarded_rows == 10
