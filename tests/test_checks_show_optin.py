"""Unit tests for missing show opt-in coverage check."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
from textwrap import dedent

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from etl.validate.checks_show_optin import MissingShowOptInCheck
from etl.validate.framework import CheckContext, CheckStatus, Severity

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.models.stg_optin import StgOptinTransaction  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for show-optin check tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _dedupe_event_session_indexes() -> None:
    """Remove duplicated indexes for `event_sessions` table in test metadata."""

    table = EventSession.__table__
    seen: set[tuple[str, tuple[str, ...]]] = set()
    duplicates = []
    for index in list(table.indexes):
        key = (str(index.name), tuple(column.name for column in index.columns))
        if key in seen:
            duplicates.append(index)
            continue
        seen.add(key)
    for index in duplicates:
        table.indexes.discard(index)


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimum schema required by show-optin coverage check tests."""

    _dedupe_event_session_indexes()
    SQLModel.metadata.create_all(
        engine,
        tables=[
            LegacySource.__table__,
            EventSession.__table__,
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            StgOptinTransaction.__table__,
        ],
    )


def _insert_show_session(
    session: Session,
    *,
    event_id: int,
    session_key: str,
    session_date: date,
) -> int:
    """Insert one show session row and return its identifier."""

    row = EventSession(
        event_id=event_id,
        session_key=session_key,
        session_name=session_key,
        session_type=EventSessionType.NOTURNO_SHOW,
        session_date=session_date,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return int(row.id)


def _insert_optin_source(
    session: Session,
    *,
    source_id: str,
    source_uri: str,
    status: IngestionStatus,
    session_id: int | None = None,
    observed_in_staging: bool = False,
) -> None:
    """Insert source/run and optional staging row for opt-in coverage."""

    source = Source(
        source_id=source_id,
        kind=SourceKind.XLSX,
        uri=source_uri,
    )
    session.add(source)
    session.commit()
    session.refresh(source)

    run = IngestionRun(source_pk=source.id, status=status)
    session.add(run)
    session.commit()
    session.refresh(run)

    lineage = LineageRef(
        source_id=source.source_id,
        ingestion_id=run.id,
        location_type=LineageLocationType.SHEET,
        location_value="sheet:Optin",
        evidence_text="Planilha de opt-in Eventim",
    )
    session.add(lineage)
    session.commit()
    session.refresh(lineage)

    if observed_in_staging:
        if session_id is None:
            raise ValueError("session_id obrigatorio quando observed_in_staging=True")
        session.add(
            StgOptinTransaction(
                source_id=source.source_id,
                ingestion_id=run.id,
                lineage_ref_id=int(lineage.id),
                event_id=2025,
                session_id=session_id,
                sheet_name="Optin",
                header_row=1,
                row_number=1 if "DOZE" in source_id else 2,
                source_range="A1:H1",
                sessao="Show",
                raw_payload_json="{}",
            )
        )
        session.commit()


def _write_optional_show_optin_contract(path: Path) -> Path:
    """Write coverage contract fixture with optional opt-in for show sessions."""

    path.write_text(
        dedent(
            """
            version: 1
            status_domain: [ok, gap, partial]
            default_required_datasets: [access_control]
            session_types:
              NOTURNO_SHOW:
                datasets:
                  - dataset: access_control
                    required: true
                    severity: error
                    status_on_missing: gap
                  - dataset: optin
                    required: false
                    severity: warning
                    status_on_missing: partial
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return path


def test_missing_show_optin_check_flags_required_gap_and_includes_method_note() -> None:
    """Required show opt-in should fail as critical and include methodology warning."""

    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
        )
        _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251214_SHOW",
            session_date=date(2025, 12, 14),
        )
        _insert_optin_source(
            session,
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            source_uri="file:///tmp/optin_12.xlsx",
            status=IngestionStatus.FAILED,
        )

        result = MissingShowOptInCheck(
            event_id=2025,
        ).run(CheckContext(ingestion_id=None, resources={"session": session}))

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["finding_count"] >= 1
    samples = result.evidence["findings_sample"]
    assert any(item["session_date"] == "2025-12-14" for item in samples)
    assert all("opt-in" in item["expected_artifact"].lower() for item in samples)
    assert all("nao substitui" in item["methodological_note"].lower() for item in samples)
    assert any("20251214" in item["expected_filename_pattern"] for item in samples)
    assert all(item["required_by_contract"] is True for item in samples)


def test_missing_show_optin_check_warns_when_contract_marks_optional(tmp_path: Path) -> None:
    """Optional show opt-in should fail as warning with optional flag in findings."""

    engine = _make_engine()
    _create_required_tables(engine)
    contract_path = _write_optional_show_optin_contract(tmp_path / "coverage_contract.yml")

    with Session(engine) as session:
        _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
        )
        _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251214_SHOW",
            session_date=date(2025, 12, 14),
        )

        result = MissingShowOptInCheck(
            event_id=2025,
            contract_path=contract_path,
        ).run(CheckContext(ingestion_id=None, resources={"session": session}))

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.WARNING
    assert "warning" in result.message.lower()
    assert result.evidence["finding_count"] >= 1
    sample = result.evidence["findings_sample"][0]
    assert sample["required_by_contract"] is False
    assert sample["reason_code"] == "missing_in_catalog"
    assert "20251212" in sample["expected_filename_pattern"] or "20251214" in sample[
        "expected_filename_pattern"
    ]


def test_missing_show_optin_check_passes_when_focus_days_have_staging_coverage() -> None:
    """Check should pass when both focus show days have observed opt-in staging rows."""

    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        id_show_12 = _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
        )
        id_show_14 = _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251214_SHOW",
            session_date=date(2025, 12, 14),
        )
        _insert_optin_source(
            session,
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            source_uri="file:///tmp/optin_12.xlsx",
            status=IngestionStatus.SUCCESS,
            session_id=id_show_12,
            observed_in_staging=True,
        )
        _insert_optin_source(
            session,
            source_id="SRC_OPTIN_NOTURNO_QUATORZE",
            source_uri="file:///tmp/optin_14.xlsx",
            status=IngestionStatus.SUCCESS,
            session_id=id_show_14,
            observed_in_staging=True,
        )

        result = MissingShowOptInCheck(
            event_id=2025,
        ).run(CheckContext(ingestion_id=None, resources={"session": session}))

    assert result.status == CheckStatus.PASS
    assert result.severity == Severity.INFO
    assert result.evidence["finding_count"] == 0

