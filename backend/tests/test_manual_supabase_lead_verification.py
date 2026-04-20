from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from app.services.manual_supabase_lead_export import LEAD_IMPORT_COLUMNS, build_ticketing_key
from app.services import manual_supabase_lead_verification as verification_service
from app.services.manual_supabase_lead_verification import verify_manual_supabase_lead_import


def _make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return Session(engine)


def _lead_row(
    *,
    email: str,
    cpf: str,
    evento_nome: str,
    sessao: str,
    nome: str,
) -> dict[str, str]:
    row = {column: "" for column in LEAD_IMPORT_COLUMNS}
    row.update(
        {
            "email": email,
            "cpf": cpf,
            "evento_nome": evento_nome,
            "sessao": sessao,
            "nome": nome,
            "data_criacao": "2026-04-20 19:12:07.230232",
            "batch_id": "244",
        }
    )
    return row


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEAD_IMPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _write_manifest(
    path: Path,
    *,
    accepted_csv: Path,
    delta_csv: Path,
    skipped_csv: Path,
    full_rows: int,
    delta_rows: int,
    skipped_rows: int,
) -> None:
    path.write_text(
        json.dumps(
            {
                "export_date": "2026-04-20",
                "artifacts": {
                    "full_import_csv_path": str(accepted_csv),
                    "import_csv_path": str(delta_csv),
                    "skipped_existing_csv_path": str(skipped_csv),
                },
                "summary": {
                    "full_rows": full_rows,
                    "import_ready_rows": delta_rows,
                    "skipped_existing_rows": skipped_rows,
                    "already_existing_pre_export_rows": skipped_rows,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _ticketing_keys(rows: list[dict[str, str]]) -> set[str]:
    return {
        build_ticketing_key(
            email=row["email"],
            cpf=row["cpf"],
            evento_nome=row["evento_nome"],
            sessao=row["sessao"],
        )
        for row in rows
    }


def test_verify_manual_supabase_lead_import_returns_ok_when_all_rows_present(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    accepted_rows = [
        _lead_row(
            email="existing@example.com",
            cpf="11111111111",
            evento_nome="Evento A",
            sessao="Sessao A",
            nome="Existing",
        ),
        _lead_row(
            email="new@example.com",
            cpf="22222222222",
            evento_nome="Evento A",
            sessao="Sessao B",
            nome="New",
        ),
    ]
    delta_rows = [accepted_rows[1]]
    skipped_rows = [accepted_rows[0]]
    accepted_csv = tmp_path / "accepted.csv"
    delta_csv = tmp_path / "delta.csv"
    skipped_csv = tmp_path / "skipped.csv"
    manifest_path = tmp_path / "manifest.json"
    _write_csv(accepted_csv, accepted_rows)
    _write_csv(delta_csv, delta_rows)
    _write_csv(skipped_csv, skipped_rows)
    _write_manifest(
        manifest_path,
        accepted_csv=accepted_csv,
        delta_csv=delta_csv,
        skipped_csv=skipped_csv,
        full_rows=2,
        delta_rows=1,
        skipped_rows=1,
    )

    existing_keys = _ticketing_keys(accepted_rows)
    monkeypatch.setattr(
        verification_service,
        "fetch_existing_lookup_sets",
        lambda db, rows: (100, set(), existing_keys),
    )

    with _make_session() as session:
        artifacts = verify_manual_supabase_lead_import(
            db=session,
            accepted_csv_path=accepted_csv,
            manifest_path=manifest_path,
            output_dir=tmp_path / "verification-ok",
        )

    assert artifacts.status == "ok"
    assert artifacts.summary["accepted_rows_present_now"] == 2
    assert artifacts.summary["accepted_rows_missing_now"] == 0
    assert artifacts.summary["delta_rows_present_now"] == 1
    assert artifacts.summary["already_existing_pre_export_rows_present_now"] == 1
    with artifacts.missing_rows_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        assert list(csv.DictReader(handle)) == []


def test_verify_manual_supabase_lead_import_returns_partial_when_some_rows_are_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    accepted_rows = [
        _lead_row(
            email="existing@example.com",
            cpf="11111111111",
            evento_nome="Evento A",
            sessao="Sessao A",
            nome="Existing",
        ),
        _lead_row(
            email="new@example.com",
            cpf="22222222222",
            evento_nome="Evento A",
            sessao="Sessao B",
            nome="New",
        ),
    ]
    delta_rows = [accepted_rows[1]]
    skipped_rows = [accepted_rows[0]]
    accepted_csv = tmp_path / "accepted.csv"
    delta_csv = tmp_path / "delta.csv"
    skipped_csv = tmp_path / "skipped.csv"
    manifest_path = tmp_path / "manifest.json"
    _write_csv(accepted_csv, accepted_rows)
    _write_csv(delta_csv, delta_rows)
    _write_csv(skipped_csv, skipped_rows)
    _write_manifest(
        manifest_path,
        accepted_csv=accepted_csv,
        delta_csv=delta_csv,
        skipped_csv=skipped_csv,
        full_rows=2,
        delta_rows=1,
        skipped_rows=1,
    )

    existing_key = build_ticketing_key(
        email=accepted_rows[0]["email"],
        cpf=accepted_rows[0]["cpf"],
        evento_nome=accepted_rows[0]["evento_nome"],
        sessao=accepted_rows[0]["sessao"],
    )
    monkeypatch.setattr(
        verification_service,
        "fetch_existing_lookup_sets",
        lambda db, rows: (100, set(), {existing_key}),
    )

    with _make_session() as session:
        artifacts = verify_manual_supabase_lead_import(
            db=session,
            accepted_csv_path=accepted_csv,
            manifest_path=manifest_path,
            output_dir=tmp_path / "verification-partial",
        )

    assert artifacts.status == "partial"
    assert artifacts.summary["accepted_rows_present_now"] == 1
    assert artifacts.summary["accepted_rows_missing_now"] == 1
    assert artifacts.summary["delta_rows_missing_now"] == 1
    with artifacts.missing_rows_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        missing_rows = list(csv.DictReader(handle))
    assert len(missing_rows) == 1
    assert missing_rows[0]["email"] == "new@example.com"


def test_verify_manual_supabase_lead_import_returns_wrong_target_when_preexisting_rows_disappear(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    accepted_rows = [
        _lead_row(
            email="existing@example.com",
            cpf="11111111111",
            evento_nome="Evento A",
            sessao="Sessao A",
            nome="Existing",
        ),
        _lead_row(
            email="new@example.com",
            cpf="22222222222",
            evento_nome="Evento A",
            sessao="Sessao B",
            nome="New",
        ),
    ]
    delta_rows = [accepted_rows[1]]
    skipped_rows = [accepted_rows[0]]
    accepted_csv = tmp_path / "accepted.csv"
    delta_csv = tmp_path / "delta.csv"
    skipped_csv = tmp_path / "skipped.csv"
    manifest_path = tmp_path / "manifest.json"
    _write_csv(accepted_csv, accepted_rows)
    _write_csv(delta_csv, delta_rows)
    _write_csv(skipped_csv, skipped_rows)
    _write_manifest(
        manifest_path,
        accepted_csv=accepted_csv,
        delta_csv=delta_csv,
        skipped_csv=skipped_csv,
        full_rows=2,
        delta_rows=1,
        skipped_rows=1,
    )

    delta_key = build_ticketing_key(
        email=accepted_rows[1]["email"],
        cpf=accepted_rows[1]["cpf"],
        evento_nome=accepted_rows[1]["evento_nome"],
        sessao=accepted_rows[1]["sessao"],
    )
    monkeypatch.setattr(
        verification_service,
        "fetch_existing_lookup_sets",
        lambda db, rows: (52736, set(), {delta_key}),
    )

    with _make_session() as session:
        artifacts = verify_manual_supabase_lead_import(
            db=session,
            accepted_csv_path=accepted_csv,
            manifest_path=manifest_path,
            output_dir=tmp_path / "verification-wrong-target",
        )

    assert artifacts.status == "wrong_target_or_empty"
    assert artifacts.summary["already_existing_pre_export_rows_present_now"] == 0
