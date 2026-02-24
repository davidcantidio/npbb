"""TMJ 2025 closing report generator (Word/DOCX).

Constraints:
- Offline/local execution.
- Uses `python-docx` only (no docxtpl placeholders). The template is treated as
  a structured document anchored by stable headings (Heading 1/2).

Design:
- For each section heading in the template, we clear the existing body content
  (without deleting the heading itself) and insert report-ready paragraphs/tables.
- Every metric table inserted includes one or more "Fonte:" paragraphs right
  after it, pointing to `source_id` + location hints (sheet/page) and evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Optional, Sequence

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from sqlalchemy import func, text
from sqlmodel import Session, select

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
    TicketSales,
)
from app.reports.docx_ops import (
    add_kv_table,
    add_matrix_table,
    clear_blocks_between,
    find_heading_by_prefix,
    find_next_heading,
    insert_paragraph_after_block,
)
from app.services.data_quality import quality_gate_blocked, quality_summary
from app.services.tmj_sessions import tmj2025_session_key


Block = Paragraph | Table


@dataclass(frozen=True)
class RenderOptions:
    """Options controlling what the generator renders and how strict it is."""

    event_id: int | None = None
    session_key_prefix: str = "TMJ2025_"
    expected_show_dates: Sequence[date] = (
        date(2025, 12, 12),
        date(2025, 12, 13),
        date(2025, 12, 14),
    )
    fail_on_dq_blocked: bool = False


def _as_percent(value: Decimal | float | None) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return ""


def _yes_no(value: bool | None) -> str:
    if value is None:
        return "N/A"
    return "SIM" if value else "NAO"


def _safe_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _scalar(row):
    """Return the scalar value from a SQLModel exec row.

    SQLModel may return scalars for single-column selects, or 1-tuples depending on context.
    """
    if row is None:
        return None
    if isinstance(row, (tuple, list)):
        return row[0] if row else None
    return row


def _fmt_int(value: int | None) -> str:
    return "" if value is None else str(int(value))


def _fmt_date(value: date | None) -> str:
    return "" if value is None else value.isoformat()


def _source_label(src: Source | None, source_id: str) -> str:
    if src is None:
        return source_id
    if src.display_name:
        return f"{source_id} ({src.display_name})"
    return source_id


def _latest_ingestion_by_source(session: Session, *, source_ids: Iterable[str]) -> dict[str, IngestionRun]:
    latest: dict[str, IngestionRun] = {}
    for sid in sorted({(s or "").strip() for s in source_ids if (s or "").strip()}):
        row = session.exec(
            select(IngestionRun)
            .where(IngestionRun.source_id == sid)
            .order_by(IngestionRun.started_at.desc())
            .limit(1)
        ).first()
        if row is not None:
            latest[sid] = row
    return latest


def _insert_heading_section_body(doc: Document, *, heading_prefix: str) -> Paragraph:
    """Clear the section body after a heading and return the heading paragraph."""
    match = find_heading_by_prefix(doc, prefix=heading_prefix)
    end = find_next_heading(doc, after=match.paragraph, max_level=2)
    clear_blocks_between(doc, start=match.paragraph, end=end.paragraph if end else None)
    return match.paragraph


def _add_source_lines(doc: Document, *, anchor: Block, lines: Sequence[str]) -> Block:
    cur: Block = anchor
    for line in lines:
        cur = insert_paragraph_after_block(doc, anchor=cur, text=line)
    return cur


def _collect_tmj_sources(session: Session, *, options: RenderOptions) -> list[Source]:
    # Prefer filtering by known prefix; fall back to "sources with TMJ-ish uri".
    rows = list(session.exec(select(Source)).all())
    prefix = (options.session_key_prefix or "").strip().upper()

    def is_tmj(src: Source) -> bool:
        if src.source_id.upper().startswith("SRC_"):
            return True
        if prefix and prefix in src.source_id.upper():
            return True
        uri = (src.uri or "").lower()
        return "tamo_junto_2025" in uri or "tmj" in uri

    out = [r for r in rows if is_tmj(r)]
    out.sort(key=lambda s: (s.kind.value if hasattr(s.kind, "value") else str(s.kind), s.source_id))
    return out


def _render_context_and_objective(doc: Document, session: Session, *, options: RenderOptions) -> None:
    """Fill template sections 1 and 2 with minimal, sourced context."""
    sessions = _tmj_sessions(session, options=options)
    min_day = min((s.session_date for s in sessions if s.session_date), default=None)
    max_day = max((s.session_date for s in sessions if s.session_date), default=None)

    try:
        heading = _insert_heading_section_body(doc, heading_prefix="1. Contexto do evento")
        cur: Block = heading
        cur = insert_paragraph_after_block(
            doc,
            anchor=cur,
            text="Relatorio gerado automaticamente a partir do banco NPBB, preservando a estrutura do template.",
        )
        if min_day and max_day:
            cur = insert_paragraph_after_block(
                doc,
                anchor=cur,
                text=f"Periodo observado nas sessoes carregadas: {min_day.isoformat()} a {max_day.isoformat()}.",
            )
            _add_source_lines(
                doc,
                anchor=cur,
                lines=[
                    "Fonte: banco NPBB | local: tabela event_sessions | evidencia: min/max de session_date (recorte carregado)",
                ],
            )
        else:
            cur = insert_paragraph_after_block(
                doc,
                anchor=cur,
                text="GAP: nao ha sessoes carregadas em event_sessions para inferir periodo observado.",
            )
    except ValueError:
        # Template may be missing the section; ignore.
        pass

    try:
        heading = _insert_heading_section_body(doc, heading_prefix="2. Objetivo do relatorio")
        cur = heading
        cur = insert_paragraph_after_block(
            doc,
            anchor=cur,
            text="Objetivo: consolidar metricas do Festival TMJ 2025 com rastreabilidade (Fonte/local) e explicitar GAP/INCONSISTENTE.",
        )
    except ValueError:
        pass


def _render_sources_and_limits(doc: Document, session: Session, *, options: RenderOptions) -> None:
    heading = _insert_heading_section_body(doc, heading_prefix="3. Fontes de dados e limitacoes")
    cur: Block = heading

    sources = _collect_tmj_sources(session, options=options)
    latest = _latest_ingestion_by_source(session, source_ids=[s.source_id for s in sources])

    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Fontes registradas no catalogo (source/ingestion).",
    )

    header = ["source_id", "kind", "arquivo", "status_ultima_ingestao", "dq_gate_bloqueado"]
    rows: list[list[str]] = []
    for src in sources:
        run = latest.get(src.source_id)
        status = run.status.value if run is not None and hasattr(run.status, "value") else (str(run.status) if run is not None else "")
        dq = "N/A"
        if run is not None:
            summ = quality_summary(session, ingestion_id=int(run.id))
            if summ["total"] > 0:
                dq = _yes_no(quality_gate_blocked(session, ingestion_id=int(run.id)))
            else:
                dq = "N/A"
        rows.append(
            [
                src.source_id,
                src.kind.value if hasattr(src.kind, "value") else str(src.kind),
                src.display_name or Path(src.uri).name,
                status or "",
                dq,
            ]
        )

    cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows or [["(nenhuma)", "", "", "", ""]])
    cur = _add_source_lines(
        doc,
        anchor=cur,
        lines=[
            "Fonte: banco NPBB | local: tabela source + ingestion + data_quality_result | evidencia: catalogo operacional",
        ],
    )

    cur = insert_paragraph_after_block(doc, anchor=cur, text="Limitacoes (tecnico/metodologico):")
    for item in [
        "- Metricas de controle de acesso sao agregadas por sessao (sem deduplicacao de publico unico).",
        "- Opt-in (Eventim) e uma regua de interesse/aceite; nao equivale a entradas validadas.",
        "- Vendas totais (ingressos vendidos/liquidos) dependem de fonte especifica de vendas; quando ausente, fica como GAP.",
        "- Redes sociais, DIMAC e MTC dependem de extracao/normalizacao propria; quando nao carregadas, ficam como GAP.",
    ]:
        cur = insert_paragraph_after_block(doc, anchor=cur, text=item)


def _tmj_sessions(session: Session, *, options: RenderOptions) -> list[EventSession]:
    stmt = select(EventSession)
    if options.event_id is not None:
        stmt = stmt.where(EventSession.event_id == int(options.event_id))
    if options.session_key_prefix:
        stmt = stmt.where(EventSession.session_key.like(f"{options.session_key_prefix}%"))
    stmt = stmt.order_by(EventSession.session_date.asc(), EventSession.session_type.asc(), EventSession.session_key.asc())
    return list(session.exec(stmt).all())


def _attendance_summary_by_session_id(session: Session) -> dict[int, dict]:
    facts = list(session.exec(select(AttendanceAccessControl)).all())
    by_sid: dict[int, dict] = {}
    for f in facts:
        sid = int(f.session_id)
        row = by_sid.setdefault(
            sid,
            {
                "ingressos_validos": None,
                "presentes": None,
                "ausentes": None,
                "invalidos": None,
                "bloqueados": None,
                "sources": set(),
                "pages": set(),
                "evidences": set(),
            },
        )
        row["sources"].add(f.source_id)
        if f.pdf_page is not None:
            row["pages"].add(int(f.pdf_page))
        if f.evidence:
            row["evidences"].add(str(f.evidence))
        for key in ["ingressos_validos", "presentes", "ausentes", "invalidos", "bloqueados"]:
            cur = row.get(key)
            val = getattr(f, key)
            if val is None:
                continue
            if cur is None or int(val) > int(cur):
                row[key] = int(val)
    return by_sid


def _optin_summary_by_session_id(session: Session) -> dict[int, dict]:
    txs = list(session.exec(select(OptinTransaction)).all())
    by_sid: dict[int, dict] = {}
    for t in txs:
        sid = int(t.session_id)
        row = by_sid.setdefault(
            sid,
            {
                "tx_count": 0,
                "tickets_qty": 0,
                "unique_people": set(),
                "sources": set(),
                "sheets": set(),
            },
        )
        row["tx_count"] += 1
        row["tickets_qty"] += int(t.ticket_qty or 0)
        if t.person_key_hash:
            row["unique_people"].add(t.person_key_hash)
        row["sources"].add(t.source_id)
        if t.sheet_name:
            row["sheets"].add(str(t.sheet_name))
    # convert set sizes
    for sid, row in by_sid.items():
        row["unique_people_count"] = len(row["unique_people"])
    return by_sid


def _ticket_sales_summary_by_session_id(session: Session) -> dict[int, dict]:
    facts = list(session.exec(select(TicketSales)).all())
    by_sid: dict[int, dict] = {}
    for f in facts:
        sid = int(f.session_id)
        row = by_sid.setdefault(
            sid,
            {"sold_total": None, "net_sold_total": None, "sources": set(), "evidences": set()},
        )
        row["sources"].add(f.source_id)
        if f.evidence:
            row["evidences"].add(str(f.evidence))
        for key in ["sold_total", "net_sold_total"]:
            cur = row.get(key)
            val = getattr(f, key)
            if val is None:
                continue
            if cur is None or int(val) > int(cur):
                row[key] = int(val)
    return by_sid


def _render_big_numbers(doc: Document, session: Session, *, options: RenderOptions) -> None:
    heading = _insert_heading_section_body(doc, heading_prefix="4. Big numbers")
    cur: Block = heading

    sessions = _tmj_sessions(session, options=options)
    attendance = _attendance_summary_by_session_id(session)
    optin = _optin_summary_by_session_id(session)

    total_presentes = sum(int(attendance.get(int(s.id), {}).get("presentes") or 0) for s in sessions if s.id is not None)
    total_optin_tickets = sum(int(optin.get(int(s.id), {}).get("tickets_qty") or 0) for s in sessions if s.id is not None)
    optin_people: set[str] = set()
    for row in session.exec(select(OptinTransaction.person_key_hash)).all():
        v = _scalar(row)
        if v is not None:
            optin_people.add(str(v))
    total_optin_unique = len(optin_people)

    leads_people: set[str] = set()
    for row in session.exec(select(FestivalLead.person_key_hash)).all():
        v = _scalar(row)
        if v is not None:
            leads_people.add(str(v))
    total_leads_unique = len(leads_people)

    cur = insert_paragraph_after_block(doc, anchor=cur, text="Resumo agregado do recorte carregado no banco.")
    cur = add_kv_table(
        doc,
        anchor=cur,
        rows=[
            ("Entradas validadas (presentes) - controle de acesso (soma sessoes com dado)", str(total_presentes)),
            ("Opt-in aceitos - tickets (soma por sessao)", str(total_optin_tickets)),
            ("Opt-in aceitos - publico unico (dedupe por person_key_hash)", str(total_optin_unique)),
            ("Leads (Festival de Esportes) - publico unico (dedupe por person_key_hash)", str(total_leads_unique)),
        ],
    )

    # Lineage at section level for aggregated big numbers.
    sources_used: set[str] = set()
    for sid, row in attendance.items():
        sources_used.update(row.get("sources") or set())
    for sid, row in optin.items():
        sources_used.update(row.get("sources") or set())
    sources_used.update({str(v) for row in session.exec(select(FestivalLead.source_id)).all() if (v := _scalar(row)) is not None})

    src_map = {s.source_id: s for s in session.exec(select(Source)).all()}
    fonte_lines = []
    for sid in sorted(sources_used):
        fonte_lines.append(
            f"Fonte: {_source_label(src_map.get(sid), sid)} | local: banco (canonical) | evidencia: agregacoes de fechamento"
        )
    cur = _add_source_lines(doc, anchor=cur, lines=fonte_lines or ["Fonte: (sem dados) | local: N/A | evidencia: N/A"])

    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Nota: ver subsecoes 4.1 a 4.3 para detalhamento por sessao e reguas de publico.",
    )

    # Shows coverage audit (critical feedback: avoid omitting 12/12 and 14/12).
    cur = insert_paragraph_after_block(doc, anchor=cur, text="Shows por dia (auditoria de cobertura minima):")

    view_rows: list[dict] = []
    if options.session_key_prefix == "TMJ2025_" and set(options.expected_show_dates) == {
        date(2025, 12, 12),
        date(2025, 12, 13),
        date(2025, 12, 14),
    }:
        # Prefer marts/view when migrations are applied.
        try:
            q = text(
                """
SELECT
  show_date,
  session_key_expected,
  status,
  missing_flags,
  request_needed
FROM mart_report_show_day_summary
ORDER BY show_date
"""
            )
            res = session.exec(q).all()
            for r in res:
                try:
                    view_rows.append(dict(r._mapping))
                except Exception:
                    view_rows.append(
                        {
                            "show_date": r[0],
                            "session_key_expected": r[1],
                            "status": r[2],
                            "missing_flags": r[3],
                            "request_needed": r[4],
                        }
                    )
        except Exception:
            view_rows = []

    header = ["dia_show", "session_key", "status", "missing_flags"]
    rows: list[list[str]] = []
    req_lines: list[str] = []

    if view_rows:
        for r in view_rows:
            day = r.get("show_date")
            key = str(r.get("session_key_expected") or "")
            status = str(r.get("status") or "")
            missing_flags = str(r.get("missing_flags") or "")
            req = str(r.get("request_needed") or "")
            rows.append([str(day), key, status, missing_flags])
            if status and status != "OK" and req:
                req_lines.append(f"- {day}: {req}")

        cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows)
        cur = _add_source_lines(
            doc,
            anchor=cur,
            lines=[
                "Fonte: banco NPBB | local: view mart_report_show_day_summary | evidencia: status/missing_flags/request_needed",
            ],
        )
    else:
        # Fallback: compute directly from canonical facts.
        sess_by_key = {s.session_key: s for s in sessions}
        sales = _ticket_sales_summary_by_session_id(session)

        for d in options.expected_show_dates:
            expected_key = tmj2025_session_key(d, EventSessionType.NOTURNO_SHOW)
            sess = sess_by_key.get(expected_key)
            if sess is None or sess.id is None:
                rows.append([_fmt_date(d), expected_key, "GAP", "sessao_ausente; optin; acesso; vendas;"])
                req_lines.append(
                    f"- {d.isoformat()}: Solicitar agenda master da sessao (show) e fontes minimas (acesso, vendas, opt-in)."
                )
                continue

            sid = int(sess.id)
            has_optin = sid in optin and int(optin[sid].get("tickets_qty") or 0) > 0
            has_acc = sid in attendance and (attendance[sid].get("presentes") is not None)
            has_sales = sid in sales and (
                sales[sid].get("sold_total") is not None or sales[sid].get("net_sold_total") is not None
            )

            missing: list[str] = []
            if not has_optin:
                missing.append("optin")
            if not has_acc:
                missing.append("acesso")
            if not has_sales:
                missing.append("vendas")

            status = "OK" if not missing else "GAP"
            missing_flags = ("; ".join(missing) + ";") if missing else ""
            rows.append([_fmt_date(d), expected_key, status, missing_flags])

            if missing:
                if (not has_optin) and (not has_acc) and (not has_sales):
                    req = "Solicitar: XLSX opt-in aceitos (Eventim); PDF controle de acesso (show) por sessao; base de vendas total/liquida por sessao."
                elif not has_optin:
                    req = "Solicitar: XLSX opt-in aceitos (Eventim) por sessao."
                elif not has_acc:
                    req = "Solicitar: PDF controle de acesso (show) com ingressos_validos/presentes por sessao."
                else:
                    req = "Solicitar: base de vendas (sold_total/net_sold_total) por sessao."
                req_lines.append(f"- {d.isoformat()}: {req}")

        cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows)
        cur = _add_source_lines(
            doc,
            anchor=cur,
            lines=[
                "Fonte: banco NPBB | local: event_sessions + facts (optin_transactions, attendance_access_control, ticket_sales) | evidencia: auditoria de cobertura por dia",
            ],
        )

    if req_lines:
        cur = insert_paragraph_after_block(doc, anchor=cur, text="GAP formal (o que falta pedir):")
        for line in req_lines:
            cur = insert_paragraph_after_block(doc, anchor=cur, text=line)


def _render_attendance_section(doc: Document, session: Session, *, options: RenderOptions) -> None:
    heading = _insert_heading_section_body(doc, heading_prefix="4.1 Publico do evento")
    cur: Block = heading

    sessions = _tmj_sessions(session, options=options)
    attendance = _attendance_summary_by_session_id(session)
    src_map = {s.source_id: s for s in session.exec(select(Source)).all()}

    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Controle de acesso (entradas validadas) por sessao. Regua: catraca/controle de acesso.",
    )

    header = [
        "sessao",
        "data",
        "tipo",
        "ingressos_validos",
        "presentes",
        "ausentes",
        "comparecimento_pct",
    ]
    rows: list[list[str]] = []
    sources_used: set[str] = set()
    for s in sessions:
        if s.id is None:
            continue
        att = attendance.get(int(s.id)) or {}
        iv = _safe_int(att.get("ingressos_validos"))
        pres = _safe_int(att.get("presentes"))
        aus = _safe_int(att.get("ausentes"))
        pct = None
        if iv is not None and iv > 0 and pres is not None:
            pct = (float(pres) * 100.0) / float(iv)
        rows.append(
            [
                s.session_name,
                _fmt_date(s.session_date),
                s.session_type.value if hasattr(s.session_type, "value") else str(s.session_type),
                _fmt_int(iv),
                _fmt_int(pres),
                _fmt_int(aus),
                _as_percent(pct),
            ]
        )
        sources_used.update(att.get("sources") or set())

    cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows or [["(sem dados)", "", "", "", "", "", ""]])

    fonte_lines: list[str] = []
    # Add more precise pages/evidence when present.
    for sid in sorted(sources_used):
        src = src_map.get(sid)
        pages = sorted({p for row in attendance.values() if sid in (row.get("sources") or set()) for p in (row.get("pages") or set())})
        evs = sorted({e for row in attendance.values() if sid in (row.get("sources") or set()) for e in (row.get("evidences") or set())})
        local = f"page:{pages[0]}" if pages else "page:(nao informado)"
        evidencia = evs[0] if evs else "AttendanceAccessControl.evidence (nao informado)"
        fonte_lines.append(
            f"Fonte: {_source_label(src, sid)} | local: {local} | evidencia: {evidencia}"
        )
    cur = _add_source_lines(
        doc,
        anchor=cur,
        lines=fonte_lines or ["Fonte: (sem fonte carregada) | local: N/A | evidencia: N/A"],
    )


def _render_optin_section(doc: Document, session: Session, *, options: RenderOptions) -> None:
    heading = _insert_heading_section_body(doc, heading_prefix="4.2 Dinamica de vendas")
    cur: Block = heading

    sessions = _tmj_sessions(session, options=options)
    optin = _optin_summary_by_session_id(session)
    src_map = {s.source_id: s for s in session.exec(select(Source)).all()}

    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Opt-in aceitos (Eventim) por sessao. Regua: opt-in aceitos, nao equivale a controle de acesso.",
    )

    header = ["sessao", "data", "tickets_qty", "publico_unico", "tx_count"]
    rows: list[list[str]] = []
    sources_used: set[str] = set()
    sheets_used: set[str] = set()
    for s in sessions:
        if s.id is None:
            continue
        row = optin.get(int(s.id)) or {}
        rows.append(
            [
                s.session_name,
                _fmt_date(s.session_date),
                _fmt_int(_safe_int(row.get("tickets_qty"))),
                _fmt_int(_safe_int(row.get("unique_people_count"))),
                _fmt_int(_safe_int(row.get("tx_count"))),
            ]
        )
        sources_used.update(row.get("sources") or set())
        sheets_used.update(row.get("sheets") or set())

    cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows or [["(sem dados)", "", "", "", ""]])

    fonte_lines: list[str] = []
    for sid in sorted(sources_used):
        src = src_map.get(sid)
        sheet = sorted(sheets_used)[0] if sheets_used else "(nao informado)"
        fonte_lines.append(
            f"Fonte: {_source_label(src, sid)} | local: sheet:{sheet} | evidencia: colunas qtd_ingresso, person_key_hash, dt_hr_compra"
        )
    cur = _add_source_lines(
        doc,
        anchor=cur,
        lines=fonte_lines or ["Fonte: (sem fonte carregada) | local: N/A | evidencia: N/A"],
    )

    # Minimal pre-venda curve (daily tickets) as a table.
    cur = insert_paragraph_after_block(doc, anchor=cur, text="Serie diaria (opt-in tickets por data de compra):")
    daily_rows = session.exec(
        select(OptinTransaction.purchase_date, func.sum(func.coalesce(OptinTransaction.ticket_qty, 0)))
        .where(OptinTransaction.purchase_date.is_not(None))
        .group_by(OptinTransaction.purchase_date)
        .order_by(OptinTransaction.purchase_date.asc())
    ).all()
    mat_rows = [[_fmt_date(d), _fmt_int(_safe_int(qty))] for d, qty in daily_rows]
    cur = add_matrix_table(doc, anchor=cur, header=["purchase_date", "tickets_qty"], rows=mat_rows or [["(sem dados)", ""]])
    cur = _add_source_lines(
        doc,
        anchor=cur,
        lines=fonte_lines or ["Fonte: (sem fonte carregada) | local: N/A | evidencia: N/A"],
    )


def _render_bb_share_section(doc: Document, session: Session, *, options: RenderOptions) -> None:
    heading = _insert_heading_section_body(doc, heading_prefix="4.3 Quem sao clientes do Banco")
    cur: Block = heading

    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Proxy de relacionamento BB via categoria de ingresso (opt-in).",
    )

    # Aggregate across all sessions in scope.
    seg_rows = session.exec(
        select(
            func.coalesce(TicketCategorySegmentMap.segment, BbRelationshipSegment.DESCONHECIDO),
            func.sum(func.coalesce(OptinTransaction.ticket_qty, 0)),
        )
        .select_from(OptinTransaction)
        .join(
            TicketCategorySegmentMap,
            TicketCategorySegmentMap.ticket_category_norm == OptinTransaction.ticket_category_norm,
            isouter=True,
        )
        .group_by(func.coalesce(TicketCategorySegmentMap.segment, BbRelationshipSegment.DESCONHECIDO))
        .order_by(func.sum(func.coalesce(OptinTransaction.ticket_qty, 0)).desc())
    ).all()
    total = sum(int(qty or 0) for _, qty in seg_rows) or 0

    header = ["segmento", "tickets_qty", "share_pct"]
    rows: list[list[str]] = []
    for seg, qty in seg_rows:
        qty_int = int(qty or 0)
        share = (float(qty_int) * 100.0) / float(total) if total > 0 else None
        seg_val = seg.value if hasattr(seg, "value") else str(seg)
        rows.append([seg_val, str(qty_int), _as_percent(share)])

    cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows or [["(sem dados)", "", ""]])

    # Lineage: optin source(s) + mapping table (inferred).
    src_map = {s.source_id: s for s in session.exec(select(Source)).all()}
    optin_sources = sorted({str(v) for row in session.exec(select(OptinTransaction.source_id)).all() if (v := _scalar(row)) is not None})
    fonte_lines = []
    for sid in optin_sources:
        fonte_lines.append(
            f"Fonte: {_source_label(src_map.get(sid), sid)} | local: sheet:(ver opt-in) | evidencia: ticket_category_norm -> segment"
        )
    fonte_lines.append(
        "Fonte: banco NPBB | local: tabela ticket_category_segment_map | evidencia: inferencia/edicao auditavel do segmento"
    )
    cur = _add_source_lines(doc, anchor=cur, lines=fonte_lines)


def _render_pre_venda_section(doc: Document, session: Session, *, options: RenderOptions) -> None:
    """Fill section 6 (pre-venda) with per-session operational indicators derived from opt-in."""
    try:
        heading = _insert_heading_section_body(doc, heading_prefix="6. Pre-venda")
    except ValueError:
        return

    cur: Block = heading
    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Indicadores operacionais (opt-in) por sessao: publico unico, tickets e janela observada de compra.",
    )

    sessions = _tmj_sessions(session, options=options)
    sess_map = {int(s.id): s for s in sessions if s.id is not None}
    sess_ids = sorted(sess_map.keys())
    if not sess_ids:
        cur = insert_paragraph_after_block(doc, anchor=cur, text="GAP: nenhuma sessao encontrada para o recorte.")
        _add_source_lines(
            doc,
            anchor=cur,
            lines=["Fonte: banco NPBB | local: tabela event_sessions | evidencia: recorte vazio"],
        )
        return

    per = session.exec(
        select(
            OptinTransaction.session_id,
            func.min(OptinTransaction.purchase_date),
            func.max(OptinTransaction.purchase_date),
            func.sum(func.coalesce(OptinTransaction.ticket_qty, 0)),
            func.count(func.distinct(OptinTransaction.person_key_hash)),
        )
        .where(OptinTransaction.session_id.in_(sess_ids))
        .where(OptinTransaction.purchase_date.is_not(None))
        .group_by(OptinTransaction.session_id)
        .order_by(OptinTransaction.session_id.asc())
    ).all()

    header = [
        "sessao",
        "data",
        "purchase_date_min",
        "purchase_date_max",
        "tickets_qty",
        "publico_unico",
        "tickets_por_pessoa",
    ]
    rows: list[list[str]] = []
    for sid, dmin, dmax, qty, uniq in per:
        if sid is None:
            continue
        sess = sess_map.get(int(sid))
        if sess is None:
            continue
        qty_i = int(qty or 0)
        uniq_i = int(uniq or 0)
        ratio = (float(qty_i) / float(uniq_i)) if uniq_i > 0 else None
        rows.append(
            [
                sess.session_name,
                _fmt_date(sess.session_date),
                _fmt_date(dmin),
                _fmt_date(dmax),
                str(qty_i),
                str(uniq_i),
                "" if ratio is None else f"{ratio:.2f}",
            ]
        )

    cur = add_matrix_table(doc, anchor=cur, header=header, rows=rows or [["(sem dados)", "", "", "", "", "", ""]])

    src_map = {s.source_id: s for s in session.exec(select(Source)).all()}
    optin_sources = sorted({str(v) for row in session.exec(select(OptinTransaction.source_id)).all() if (v := _scalar(row)) is not None})
    fonte_lines = []
    for sid in optin_sources:
        fonte_lines.append(
            f"Fonte: {_source_label(src_map.get(sid), sid)} | local: sheet:(ver opt-in) | evidencia: purchase_date, ticket_qty, person_key_hash"
        )
    _add_source_lines(doc, anchor=cur, lines=fonte_lines or ["Fonte: (sem fonte carregada) | local: N/A | evidencia: N/A"])


def _render_leads_section(doc: Document, session: Session, *, options: RenderOptions) -> None:
    heading = _insert_heading_section_body(doc, heading_prefix="9. Leads e ativacoes")
    cur: Block = heading

    cur = insert_paragraph_after_block(
        doc,
        anchor=cur,
        text="Leads e participacoes (Festival de Esportes). Regua: planilhas de leads (sem PII, com hash).",
    )

    daily = session.exec(
        select(
            FestivalLead.lead_created_date,
            func.count(FestivalLead.id),
            func.count(func.distinct(FestivalLead.person_key_hash)),
        )
        .where(FestivalLead.lead_created_date.is_not(None))
        .group_by(FestivalLead.lead_created_date)
        .order_by(FestivalLead.lead_created_date.asc())
    ).all()
    rows = [[_fmt_date(d), str(int(cnt or 0)), str(int(uniq or 0))] for d, cnt, uniq in daily]
    cur = add_matrix_table(doc, anchor=cur, header=["dia", "leads_count", "publico_unico"], rows=rows or [["(sem dados)", "", ""]])

    src_map = {s.source_id: s for s in session.exec(select(Source)).all()}
    lead_sources = sorted({str(v) for row in session.exec(select(FestivalLead.source_id)).all() if (v := _scalar(row)) is not None})
    fonte_lines = []
    for sid in lead_sources:
        fonte_lines.append(
            f"Fonte: {_source_label(src_map.get(sid), sid)} | local: sheet:(ver leads) | evidencia: colunas person_key_hash, data_criacao, acoes"
        )
    cur = _add_source_lines(doc, anchor=cur, lines=fonte_lines or ["Fonte: (sem fonte carregada) | local: N/A | evidencia: N/A"])

    # Top actions (split by comma) - best effort.
    cur = insert_paragraph_after_block(doc, anchor=cur, text="Top acoes (contagem de participacoes, melhor-esforco):")
    action_counts: dict[str, int] = {}
    for row in session.exec(select(FestivalLead.acoes)).all():
        acoes = _scalar(row)
        if not acoes:
            continue
        raw = str(acoes)
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if not parts:
            continue
        for p in parts:
            action_counts[p] = action_counts.get(p, 0) + 1
    top = sorted(action_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    top_rows = [[name, str(cnt)] for name, cnt in top]
    cur = add_matrix_table(doc, anchor=cur, header=["acao", "participacoes"], rows=top_rows or [["(sem dados)", ""]])
    cur = _add_source_lines(doc, anchor=cur, lines=fonte_lines or ["Fonte: (sem fonte carregada) | local: N/A | evidencia: N/A"])


def _render_gap_sections(doc: Document) -> None:
    # DIMAC/MTC/Redes sections are not yet loaded in canonical in this iteration.
    for prefix, msg in [
        ("5. Perfil do publico", "GAP: DIMAC ainda nao carregado no banco (necessario extractor/loader)."),
        ("5.1 Satisfacao e percepcao", "GAP: DIMAC (satisfacao/percepcao) ainda nao carregado no banco."),
        ("7. Performance nas redes", "GAP: metricas de redes/social listening ainda nao carregadas no banco."),
        ("8. Midia e imprensa", "GAP: MTC/imprensa ainda nao carregado no banco."),
    ]:
        try:
            heading = _insert_heading_section_body(doc, heading_prefix=prefix)
        except ValueError:
            continue
        cur: Block = heading
        cur = insert_paragraph_after_block(doc, anchor=cur, text=msg)
        _add_source_lines(
            doc,
            anchor=cur,
            lines=[
                "Fonte: staging templates (quando existirem) | local: npbb/docs/analises/eventos/tamo_junto_2025/staging | evidencia: falta de loader canonical",
            ],
        )


def _render_recommendations_and_appendix(doc: Document) -> None:
    try:
        heading = _insert_heading_section_body(doc, heading_prefix="10. Recomendacoes")
        cur: Block = heading
        for item in [
            "- Tratar 'shows por dia' como checklist obrigatorio: nenhum fechamento sem status por dia (OK/GAP/INCONSISTENTE).",
            "- Padronizar regua de publico no banco e no texto: entradas validadas vs opt-in vs vendidos vs publico unico.",
            "- Exigir evidencia (Fonte/local) para qualquer numero renderizado no Word.",
        ]:
            cur = insert_paragraph_after_block(doc, anchor=cur, text=item)
    except ValueError:
        pass

    try:
        heading = _insert_heading_section_body(doc, heading_prefix="11. Apendice")
        cur: Block = heading
        for item in [
            "Definicoes rapidas:",
            "- Entradas validadas: metricas de controle de acesso/catraca por sessao (presentes).",
            "- Opt-in aceitos: registros Eventim de aceite (tickets_qty e publico unico por hash).",
            "- Ingressos vendidos: requer fonte de vendas total/liquida (ticket_sales).",
            "- Publico unico: deduplicacao quando existe chave consistente (ex.: person_key_hash).",
        ]:
            cur = insert_paragraph_after_block(doc, anchor=cur, text=item)
    except ValueError:
        pass


def generate_tmj2025_closing_report(
    session: Session,
    *,
    template_path: Path,
    output_path: Path,
    options: RenderOptions | None = None,
) -> Path:
    """Generate TMJ 2025 closing report docx using the v2 template."""
    opts = options or RenderOptions()

    if opts.fail_on_dq_blocked:
        # Gate on latest ingestion per relevant source_id (only when DQ results exist).
        relevant: set[str] = set()
        relevant.update({str(v) for row in session.exec(select(OptinTransaction.source_id)).all() if (v := _scalar(row)) is not None})
        relevant.update({str(v) for row in session.exec(select(AttendanceAccessControl.source_id)).all() if (v := _scalar(row)) is not None})
        relevant.update({str(v) for row in session.exec(select(FestivalLead.source_id)).all() if (v := _scalar(row)) is not None})
        relevant.update({str(v) for row in session.exec(select(TicketSales.source_id)).all() if (v := _scalar(row)) is not None})

        latest = _latest_ingestion_by_source(session, source_ids=relevant)
        blocked: list[str] = []
        for sid, run in latest.items():
            summ = quality_summary(session, ingestion_id=int(run.id))
            if summ["total"] <= 0:
                continue
            if quality_gate_blocked(session, ingestion_id=int(run.id)):
                blocked.append(f"{sid} (ingestion_id={int(run.id)})")
        if blocked:
            raise RuntimeError("DQ gate bloqueado para fontes: " + ", ".join(sorted(blocked)))

    doc = Document(str(template_path))

    # Core sections
    _render_context_and_objective(doc, session, options=opts)
    _render_sources_and_limits(doc, session, options=opts)
    _render_big_numbers(doc, session, options=opts)
    _render_attendance_section(doc, session, options=opts)
    _render_optin_section(doc, session, options=opts)
    _render_bb_share_section(doc, session, options=opts)
    _render_pre_venda_section(doc, session, options=opts)
    _render_leads_section(doc, session, options=opts)

    # GAP sections (best-effort)
    _render_gap_sections(doc)
    _render_recommendations_and_appendix(doc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    return output_path
