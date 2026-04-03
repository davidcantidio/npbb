"""Load TMJ staging artifacts into canonical tables.

This module provides "canonicalization" loaders:
- staging CSVs produced by local extractors (npbb/etl/extract/*)
- are loaded into canonical tables in the NPBB backend database.

Design goals:
- idempotent per source_id (replace-by-source, by default),
- minimal assumptions (do not invent sessions beyond what staging implies),
- support auditability via source_id + ingestion_id on every loaded row.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from sqlalchemy import delete
from sqlmodel import Session, select

from app.models.models import (
    AttendanceAccessControl,
    EventSessionType,
    FestivalLead,
    OptinTransaction,
    TicketCategorySegmentMap,
)
from app.services.tmj_segments import ensure_segment_mappings, normalize_ticket_category
from app.services.tmj_sessions import (
    get_or_create_tmj2025_session,
    infer_session_type_from_source_id,
    tmj2025_date_from_source_id,
)


@dataclass(frozen=True)
class LoadResult:
    rows_loaded: int
    rows_skipped: int


def _parse_iso_datetime(value: str | None) -> Optional[datetime]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # Some XLSX exports can use "YYYY-MM-DD HH:MM:SS".
        try:
            dt = datetime.fromisoformat(s.replace(" ", "T"))
        except ValueError:
            raise
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_int(value: str | None) -> Optional[int]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return int(s)


def _parse_decimal(value: str | None) -> Optional[Decimal]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def load_optin_transactions_from_staging_csv(
    session: Session,
    *,
    csv_path: Path,
    source_id: str,
    ingestion_id: int | None,
    event_id: int | None,
    replace_existing: bool = True,
) -> LoadResult:
    """Load staging `stg_optin_aceitos__*.csv` into `optin_transactions`."""
    if replace_existing:
        session.exec(delete(OptinTransaction).where(OptinTransaction.source_id == source_id))
        session.commit()

    categories: set[str] = set()
    to_add: list[OptinTransaction] = []
    loaded = 0
    skipped = 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessao_start_at = _parse_iso_datetime(row.get("sessao_start_at"))
            if sessao_start_at is None:
                skipped += 1
                continue

            sess_date = sessao_start_at.date()
            sess = get_or_create_tmj2025_session(
                session,
                event_id=event_id,
                session_date=sess_date,
                session_type=EventSessionType.NOTURNO_SHOW,
                session_start_at=sessao_start_at,
                source_of_truth_source_id=source_id,
            )

            purchase_at = _parse_iso_datetime(row.get("dt_hr_compra"))
            purchase_date = purchase_at.date() if purchase_at else None

            ticket_category = (row.get("ingresso") or "").strip() or None
            ticket_category_norm = normalize_ticket_category(ticket_category) if ticket_category else None
            if ticket_category:
                categories.add(ticket_category)

            cpf_hash = (row.get("cpf_hash") or "").strip() or None
            email_hash = (row.get("email_hash") or "").strip() or None
            person_key_hash = cpf_hash or email_hash

            tx = OptinTransaction(
                session_id=int(sess.id),
                source_id=source_id,
                ingestion_id=ingestion_id,
                sheet_name=(row.get("sheet_name") or "").strip() or None,
                row_number=_parse_int(row.get("row_number")),
                purchase_at=purchase_at,
                purchase_date=purchase_date,
                opt_in_text=(row.get("opt_in") or "").strip() or None,
                opt_in_id=(row.get("opt_in_id") or "").strip() or None,
                opt_in_status=(row.get("opt_in_status") or "").strip() or None,
                sales_channel=(row.get("canal_venda") or "").strip() or None,
                delivery_method=(row.get("metodo_entrega") or "").strip() or None,
                ticket_category_raw=ticket_category,
                ticket_category_norm=ticket_category_norm,
                ticket_qty=_parse_int(row.get("qtd_ingresso")),
                cpf_hash=cpf_hash,
                email_hash=email_hash,
                person_key_hash=person_key_hash,
            )
            to_add.append(tx)

            # Batch commits to keep memory/overhead bounded.
            if len(to_add) >= 1000:
                session.add_all(to_add)
                session.commit()
                loaded += len(to_add)
                to_add.clear()

    if to_add:
        session.add_all(to_add)
        session.commit()
        loaded += len(to_add)

    # Ensure mapping table covers the observed ticket categories.
    if categories:
        ensure_segment_mappings(session, categories_raw=sorted(categories))

    return LoadResult(rows_loaded=loaded, rows_skipped=skipped)


def load_access_control_from_template_csv(
    session: Session,
    *,
    csv_path: Path,
    source_id: str,
    ingestion_id: int | None,
    event_id: int | None,
    replace_existing: bool = True,
) -> LoadResult:
    """Load operator-assisted `stg_access_control_template__*.csv` into canonical attendance."""
    if replace_existing:
        session.exec(
            delete(AttendanceAccessControl).where(AttendanceAccessControl.source_id == source_id)
        )
        session.commit()

    inferred_date = tmj2025_date_from_source_id(source_id)
    inferred_type = infer_session_type_from_source_id(source_id)

    loaded = 0
    skipped = 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            session_name = (row.get("session_name") or "").strip() or None
            ingressos_validos = _parse_int(row.get("ingressos_validos"))
            presentes = _parse_int(row.get("presentes"))
            ausentes = _parse_int(row.get("ausentes"))

            # If the template is still empty, skip cleanly.
            if not any([session_name, ingressos_validos, presentes, ausentes]):
                skipped += 1
                continue

            sess_date = inferred_date
            if sess_date is None:
                raise ValueError(f"Nao foi possivel inferir session_date para source_id={source_id}")

            sess = get_or_create_tmj2025_session(
                session,
                event_id=event_id,
                session_date=sess_date,
                session_type=inferred_type,
                session_name=session_name,
                source_of_truth_source_id=source_id,
            )

            if ausentes is None and ingressos_validos is not None and presentes is not None:
                diff = int(ingressos_validos) - int(presentes)
                ausentes = diff if diff >= 0 else None

            comparecimento_pct = _parse_decimal(row.get("comparecimento_pct"))
            if (
                comparecimento_pct is None
                and ingressos_validos is not None
                and presentes is not None
                and int(ingressos_validos) > 0
            ):
                comparecimento_pct = (Decimal(int(presentes)) / Decimal(int(ingressos_validos))) * Decimal(
                    "100"
                )

            if ingressos_validos is not None and presentes is not None:
                if int(presentes) > int(ingressos_validos):
                    raise ValueError(
                        f"presentes > ingressos_validos (source_id={source_id}, session_id={sess.id})"
                    )

            fact = AttendanceAccessControl(
                session_id=int(sess.id),
                source_id=source_id,
                ingestion_id=ingestion_id,
                ingressos_validos=ingressos_validos,
                invalidos=_parse_int(row.get("invalidos")),
                bloqueados=_parse_int(row.get("bloqueados")),
                presentes=presentes,
                ausentes=ausentes,
                comparecimento_pct=comparecimento_pct,
                pdf_page=_parse_int(row.get("pdf_page")),
                evidence=(row.get("evidence") or "").strip() or None,
            )
            session.add(fact)
            loaded += 1

    session.commit()
    return LoadResult(rows_loaded=loaded, rows_skipped=skipped)


def load_festival_leads_from_staging_csv(
    session: Session,
    *,
    csv_path: Path,
    source_id: str,
    ingestion_id: int | None,
    event_id: int | None,
    replace_existing: bool = True,
) -> LoadResult:
    """Load staging `stg_leads_festival__*.csv` into `festival_leads` (hashed keys)."""
    if replace_existing:
        session.exec(delete(FestivalLead).where(FestivalLead.source_id == source_id))
        session.commit()

    loaded = 0
    skipped = 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lead_created_at = _parse_iso_datetime(row.get("data_criacao"))
            lead_created_date = lead_created_at.date() if lead_created_at else None

            cpf_hash = (row.get("cpf_hash") or "").strip() or None
            email_hash = (row.get("email_hash") or "").strip() or None
            person_key_hash = cpf_hash or email_hash

            # If there is no temporal anchor, we can still store the lead row, but without a session link.
            sess = None
            if lead_created_date is not None:
                sess = get_or_create_tmj2025_session(
                    session,
                    event_id=event_id,
                    session_date=lead_created_date,
                    session_type=EventSessionType.DIURNO_GRATUITO,
                    source_of_truth_source_id=source_id,
                )

            lead = FestivalLead(
                event_id=event_id,
                session_id=int(sess.id) if sess is not None else None,
                source_id=source_id,
                ingestion_id=ingestion_id,
                sheet_name=(row.get("sheet_name") or "").strip() or None,
                row_number=_parse_int(row.get("row_number")),
                lead_created_at=lead_created_at,
                lead_created_date=lead_created_date,
                cpf_hash=cpf_hash,
                email_hash=email_hash,
                person_key_hash=person_key_hash,
                sexo=(row.get("sexo") or "").strip() or None,
                estado=(row.get("estado") or "").strip() or None,
                cidade=(row.get("cidade") or "").strip() or None,
                acoes=(row.get("acoes") or "").strip() or None,
                interesses=(row.get("interesses") or "").strip() or None,
                area_atuacao=(row.get("area_atuacao") or "").strip() or None,
            )

            # Skip completely empty rows (defensive).
            if (
                lead.sheet_name is None
                and lead.row_number is None
                and lead.person_key_hash is None
                and lead.lead_created_at is None
            ):
                skipped += 1
                continue

            session.add(lead)
            loaded += 1

    session.commit()
    return LoadResult(rows_loaded=loaded, rows_skipped=skipped)


def list_unmapped_ticket_categories(session: Session) -> list[str]:
    """Return distinct ticket_category_raw values that have no mapping row yet."""
    # This list is used as a checklist for operators.
    stmt = (
        select(OptinTransaction.ticket_category_raw)
        .where(OptinTransaction.ticket_category_raw.is_not(None))
        .group_by(OptinTransaction.ticket_category_raw)
        .order_by(OptinTransaction.ticket_category_raw)
    )
    raw_vals = [str(v) for v in session.exec(stmt).all() if v]
    mapped_norms = {v for v in session.exec(select(TicketCategorySegmentMap.ticket_category_norm)).all() if v}
    # Fallback: if mapped_norms cannot be queried (table missing), just return raw list.
    if not mapped_norms:
        return raw_vals
    unmapped: list[str] = []
    from app.services.tmj_segments import normalize_ticket_category

    for raw in raw_vals:
        if normalize_ticket_category(raw) not in mapped_norms:
            unmapped.append(raw)
    return unmapped
