from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.models.models import (
    AttendanceAccessControl,
    BbRelationshipSegment,
    EventSession,
    EventSessionType,
    FestivalLead,
    IngestionRun,
    IngestionStatus,
    OptinTransaction,
    Source,
    SourceKind,
    TicketCategorySegmentMap,
)
from app.services.ingestion_registry import register_source, start_ingestion
from app.services.tmj_canonical_load import (
    load_access_control_from_template_csv,
    load_festival_leads_from_staging_csv,
    load_optin_transactions_from_staging_csv,
)
from app.services.tmj_segments import normalize_ticket_category
from app.services.tmj_sessions import infer_session_type_from_source_id, tmj2025_date_from_source_id


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _write_csv(path: Path, rows: list[dict]) -> None:
    assert rows, "rows must not be empty"
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def test_tmj_source_id_inference_helpers() -> None:
    assert tmj2025_date_from_source_id("SRC_PDF_ACESSO_DIURNO_GRATUITO_DOZE") == date(2025, 12, 12)
    assert tmj2025_date_from_source_id("SRC_PDF_ACESSO_NOTURNO_TREZE") == date(2025, 12, 13)
    assert tmj2025_date_from_source_id("SRC_XLSX_OPTIN_ACEITOS") is None

    assert infer_session_type_from_source_id("SRC_PDF_ACESSO_DIURNO_GRATUITO_DOZE") == EventSessionType.DIURNO_GRATUITO
    assert infer_session_type_from_source_id("SRC_PDF_ACESSO_NOTURNO_TREZE") == EventSessionType.NOTURNO_SHOW


def test_load_optin_transactions_creates_sessions_and_mappings(tmp_path: Path) -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    csv_path = tmp_path / "stg_optin.csv"
    _write_csv(
        csv_path,
        [
            {
                "source_id": "SRC_XLSX_OPTIN_ACEITOS_DOZE",
                "sheet_name": "01.1 - Opt-In Aceitos",
                "row_number": "4",
                "evento": "TAMO JUNTO BB",
                "sessao_start_at": "2025-12-12T19:00:00",
                "dt_hr_compra": "2025-10-14T09:25:55",
                "opt_in": "GENERIC",
                "opt_in_id": "3575",
                "opt_in_status": "Aceitou",
                "canal_venda": "Eventim",
                "metodo_entrega": "PDF",
                "ingresso": "FUNCIONÁRIOS BB",
                "qtd_ingresso": "2",
                "cpf_hash": "a" * 64,
                "email_hash": "b" * 64,
            },
            {
                "source_id": "SRC_XLSX_OPTIN_ACEITOS_DOZE",
                "sheet_name": "01.1 - Opt-In Aceitos",
                "row_number": "5",
                "evento": "TAMO JUNTO BB",
                "sessao_start_at": "2025-12-12T19:00:00",
                "dt_hr_compra": "2025-10-15T10:00:00",
                "opt_in": "GENERIC",
                "opt_in_id": "3575",
                "opt_in_status": "Aceitou",
                "canal_venda": "Eventim",
                "metodo_entrega": "PDF",
                "ingresso": "INTEIRA",
                "qtd_ingresso": "1",
                "cpf_hash": "",
                "email_hash": "c" * 64,
            },
        ],
    )

    with Session(engine) as session:
        register_source(
            session,
            source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE",
            kind=SourceKind.XLSX,
            uri=str(csv_path),
        )
        run = start_ingestion(session, source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE", pipeline="test")

        res = load_optin_transactions_from_staging_csv(
            session,
            csv_path=csv_path,
            source_id="SRC_XLSX_OPTIN_ACEITOS_DOZE",
            ingestion_id=run.id,
            event_id=None,
        )
        assert res.rows_loaded == 2

        sess = session.exec(select(EventSession)).first()
        assert sess is not None
        assert sess.session_type == EventSessionType.NOTURNO_SHOW
        assert sess.session_date == date(2025, 12, 12)

        txs = session.exec(select(OptinTransaction).order_by(OptinTransaction.row_number)).all()
        assert len(txs) == 2
        assert txs[0].ticket_category_norm == normalize_ticket_category("FUNCIONÁRIOS BB")
        assert txs[0].person_key_hash == "a" * 64  # cpf has priority
        assert txs[1].person_key_hash == "c" * 64  # email fallback

        maps = session.exec(select(TicketCategorySegmentMap)).all()
        assert {m.ticket_category_norm for m in maps} == {
            normalize_ticket_category("FUNCIONÁRIOS BB"),
            normalize_ticket_category("INTEIRA"),
        }
        seg_by_norm = {m.ticket_category_norm: m.segment for m in maps}
        assert seg_by_norm[normalize_ticket_category("FUNCIONÁRIOS BB")] == BbRelationshipSegment.FUNCIONARIO_BB
        assert seg_by_norm[normalize_ticket_category("INTEIRA")] == BbRelationshipSegment.PUBLICO_GERAL


def test_load_access_control_template_infers_session_date_and_type(tmp_path: Path) -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    csv_path = tmp_path / "stg_access.csv"
    _write_csv(
        csv_path,
        [
            {
                "source_id": "SRC_PDF_ACESSO_NOTURNO_TREZE",
                "session_name": "Show",
                "ingressos_validos": "100",
                "invalidos": "0",
                "bloqueados": "0",
                "presentes": "90",
                "ausentes": "",
                "comparecimento_pct": "",
                "pdf_page": "1",
                "evidence": "Tabela resumo",
            }
        ],
    )

    with Session(engine) as session:
        register_source(
            session,
            source_id="SRC_PDF_ACESSO_NOTURNO_TREZE",
            kind=SourceKind.PDF,
            uri=str(csv_path),
        )
        run = start_ingestion(session, source_id="SRC_PDF_ACESSO_NOTURNO_TREZE", pipeline="test")

        res = load_access_control_from_template_csv(
            session,
            csv_path=csv_path,
            source_id="SRC_PDF_ACESSO_NOTURNO_TREZE",
            ingestion_id=run.id,
            event_id=None,
        )
        assert res.rows_loaded == 1

        sess = session.exec(select(EventSession)).first()
        assert sess is not None
        assert sess.session_type == EventSessionType.NOTURNO_SHOW
        assert sess.session_date == date(2025, 12, 13)

        fact = session.exec(select(AttendanceAccessControl)).first()
        assert fact is not None
        assert fact.presentes == 90
        assert fact.ausentes == 10  # computed


def test_load_festival_leads_creates_diurno_session(tmp_path: Path) -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    csv_path = tmp_path / "stg_leads.csv"
    _write_csv(
        csv_path,
        [
            {
                "source_id": "SRC_XLSX_LEADS_FESTIVAL_ESPORTES",
                "sheet_name": "Entidades",
                "row_number": "2",
                "evento": "BB :: FESTIVAL TAMO JUNTO 2025",
                "cpf_hash": "d" * 64,
                "email_hash": "",
                "sexo": "",
                "estado": "CE",
                "cidade": "Fortaleza",
                "data_criacao": "2025-12-14T14:24:30.920000",
                "acoes": "BB :: CARAMELO",
                "interesses": "",
                "area_atuacao": "",
                "cpf_promotor": "",
                "nome_promotor": "",
            }
        ],
    )

    with Session(engine) as session:
        register_source(
            session,
            source_id="SRC_XLSX_LEADS_FESTIVAL_ESPORTES",
            kind=SourceKind.XLSX,
            uri=str(csv_path),
        )
        run = start_ingestion(session, source_id="SRC_XLSX_LEADS_FESTIVAL_ESPORTES", pipeline="test")

        res = load_festival_leads_from_staging_csv(
            session,
            csv_path=csv_path,
            source_id="SRC_XLSX_LEADS_FESTIVAL_ESPORTES",
            ingestion_id=run.id,
            event_id=None,
        )
        assert res.rows_loaded == 1

        sess = session.exec(select(EventSession)).first()
        assert sess is not None
        assert sess.session_type == EventSessionType.DIURNO_GRATUITO
        assert sess.session_date == date(2025, 12, 14)

        lead = session.exec(select(FestivalLead)).first()
        assert lead is not None
        assert lead.session_id == sess.id
