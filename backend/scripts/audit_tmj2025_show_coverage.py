"""Audit TMJ 2025 show coverage by day (12/12, 13/12, 14/12).

This is a lightweight operational check to avoid silent omissions in the closing report.

It prefers the mart/view `mart_report_show_day_summary` when available (migrations applied).
If the view does not exist (common in local SQLite without Alembic), it falls back to
computing coverage directly from canonical tables.
"""

from __future__ import annotations

import argparse
from datetime import date

from sqlalchemy import func, text
from sqlmodel import Session, select

from app.db.database import engine
from app.db.metadata import SQLModel
from app.models.models import (
    AttendanceAccessControl,
    EventSession,
    EventSessionType,
    FestivalLead,  # noqa: F401 (ensures table exists for create_all in sqlite)
    OptinTransaction,
    TicketSales,
)
from app.services.tmj_sessions import tmj2025_session_key


def _try_query_view(session: Session) -> list[dict]:
    stmt = text(
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
    try:
        rows = session.exec(stmt).all()
    except Exception:
        return []

    out: list[dict] = []
    for r in rows:
        try:
            m = dict(r._mapping)  # SQLAlchemy Row
        except Exception:
            # Fallback: assume tuple order
            m = {
                "show_date": r[0],
                "session_key_expected": r[1],
                "status": r[2],
                "missing_flags": r[3],
                "request_needed": r[4],
            }
        out.append(m)
    return out


def _fallback_compute(session: Session) -> list[dict]:
    expected = [date(2025, 12, 12), date(2025, 12, 13), date(2025, 12, 14)]
    out: list[dict] = []

    for d in expected:
        key = tmj2025_session_key(d, EventSessionType.NOTURNO_SHOW)
        sess = session.exec(select(EventSession).where(EventSession.session_key == key)).first()
        if sess is None:
            out.append(
                {
                    "show_date": d,
                    "session_key_expected": key,
                    "status": "GAP",
                    "missing_flags": "sessao_ausente; optin; acesso; vendas;",
                    "request_needed": "Solicitar agenda master da sessao (show) e fontes minimas (acesso, vendas, opt-in).",
                }
            )
            continue

        sid = int(sess.id)
        optin_tickets = session.exec(
            select(func.sum(func.coalesce(OptinTransaction.ticket_qty, 0))).where(OptinTransaction.session_id == sid)
        ).one()
        has_optin = int(optin_tickets or 0) > 0

        presentes = session.exec(
            select(func.max(AttendanceAccessControl.presentes)).where(AttendanceAccessControl.session_id == sid)
        ).one()
        has_access = presentes is not None and int(presentes or 0) > 0

        has_sales = (
            session.exec(select(func.count(TicketSales.id)).where(TicketSales.session_id == sid)).one() or 0
        ) > 0

        missing = []
        if not has_optin:
            missing.append("optin")
        if not has_access:
            missing.append("acesso")
        if not has_sales:
            missing.append("vendas")

        status = "OK" if not missing else "GAP"
        missing_flags = ("; ".join(missing) + ";") if missing else ""
        if not missing:
            req = ""
        elif not has_optin and not has_access and not has_sales:
            req = "Solicitar: XLSX opt-in aceitos (Eventim); PDF controle de acesso (show) por sessao; base de vendas total/liquida por sessao."
        elif not has_optin:
            req = "Solicitar: XLSX opt-in aceitos (Eventim) por sessao."
        elif not has_access:
            req = "Solicitar: PDF controle de acesso (show) com ingressos_validos/presentes por sessao."
        else:
            req = "Solicitar: base de vendas (sold_total/net_sold_total) por sessao."

        out.append(
            {
                "show_date": d,
                "session_key_expected": key,
                "status": status,
                "missing_flags": missing_flags,
                "request_needed": req,
            }
        )

    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-on-gap", action="store_true", help="Exit 1 if any day is GAP/INCONSISTENTE.")
    args = ap.parse_args(argv)

    if engine.url.drivername.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        rows = _try_query_view(session)
        if not rows:
            rows = _fallback_compute(session)

    blocked = False
    for r in rows:
        day = r.get("show_date")
        key = r.get("session_key_expected")
        status = (r.get("status") or "").strip()
        miss = (r.get("missing_flags") or "").strip()
        req = (r.get("request_needed") or "").strip()
        print(f"{day} | {key} | status={status} | missing={miss}")
        if status and status != "OK":
            blocked = True
            if req:
                print(f"  -> {req}")

    if args.fail_on_gap and blocked:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
