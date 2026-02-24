from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.models.models import (
    BbRelationshipSegment,
    DataQualitySeverity,
    DataQualityStatus,
    EventSessionType,
    IngestionStatus,
    OptinTransaction,
    SourceKind,
    TicketCategorySegmentMap,
)
from app.services.data_quality import quality_gate_blocked, run_quality_checks_for_ingestion, upsert_ingestion_evidence
from app.services.ingestion_registry import register_source, start_ingestion
from app.services.tmj_sessions import get_or_create_tmj2025_session
from app.services.tmj_segments import normalize_ticket_category


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_run_quality_checks_for_xlsx_optin_happy_path() -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        register_source(
            session,
            source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin.xlsx",
        )
        run = start_ingestion(session, source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE", pipeline="test")

        sess = get_or_create_tmj2025_session(
            session,
            event_id=None,
            session_date=date(2025, 12, 12),
            session_type=EventSessionType.NOTURNO_SHOW,
            source_of_truth_source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE",
        )

        cat_raw = "FUNCIONÁRIOS BB"
        cat_norm = normalize_ticket_category(cat_raw)
        session.add(
            TicketCategorySegmentMap(
                ticket_category_raw=cat_raw,
                ticket_category_norm=cat_norm,
                segment=BbRelationshipSegment.FUNCIONARIO_BB,
                inferred=True,
                inference_rule="test",
            )
        )
        session.commit()

        session.add(
            OptinTransaction(
                session_id=int(sess.id),
                source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE",
                ingestion_id=run.id,
                sheet_name="01.1 - Opt-In Aceitos",
                row_number=4,
                purchase_at=datetime(2025, 10, 14, 9, 0, 0, tzinfo=timezone.utc),
                purchase_date=date(2025, 10, 14),
                ticket_category_raw=cat_raw,
                ticket_category_norm=cat_norm,
                ticket_qty=1,
                person_key_hash="a" * 64,
            )
        )
        session.commit()

        upsert_ingestion_evidence(
            session,
            ingestion_id=run.id,
            source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE",
            extractor="extract_xlsx_optin_aceitos",
            evidence_status="OK",
            stats={"header": ["Evento", "Sessao", "Dt Hr Compra"], "header_row": 3},
        )

        results = run_quality_checks_for_ingestion(session, ingestion_id=run.id)
        assert results
        assert quality_gate_blocked(session, ingestion_id=run.id) is False

        # Ensure we have at least one PASS on canonical optin.
        keys = {(r.check_key, r.status, r.severity) for r in results}
        assert ("canonical.optin.rows_nonzero", DataQualityStatus.PASS, DataQualitySeverity.ERROR) in keys


def test_quality_gate_blocks_when_access_control_missing() -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        register_source(
            session,
            source_id="SRC_PDF_ACESSO_NOTURNO_TREZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/acesso.pdf",
        )
        run = start_ingestion(session, source_id="SRC_PDF_ACESSO_NOTURNO_TREZE", pipeline="test")

        upsert_ingestion_evidence(
            session,
            ingestion_id=run.id,
            source_id="SRC_PDF_ACESSO_NOTURNO_TREZE",
            extractor="extract_pdf_assisted",
            evidence_status="MANUAL",
            stats={"template": "access_control"},
        )

        results = run_quality_checks_for_ingestion(session, ingestion_id=run.id)
        assert results
        assert quality_gate_blocked(session, ingestion_id=run.id) is True

