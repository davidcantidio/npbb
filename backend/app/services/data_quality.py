"""Data Quality + Observabilidade (TMJ / ETL).

This module provides:
- persistence models for quality results (`data_quality_result`),
- helpers to persist extractor evidence summaries (`ingestion_evidence`),
- and a lightweight check runner that can be executed per `ingestion_id`.

The runner is intentionally conservative:
- it does not invent data,
- it focuses on detecting missing/partial loads, critical nulls, domain violations,
  and reconciliation issues that would contaminate marts/report.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import (
    AttendanceAccessControl,
    DataQualityResult,
    DataQualityScope,
    DataQualitySeverity,
    DataQualityStatus,
    EventSession,
    FestivalLead,
    IngestionEvidence,
    IngestionRun,
    OptinTransaction,
    Source,
    SourceKind,
    TicketCategorySegmentMap,
    now_utc,
)


@dataclass(frozen=True)
class CheckOutcome:
    check_key: str
    scope: DataQualityScope
    severity: DataQualitySeverity
    status: DataQualityStatus
    message: str
    details: str | None = None
    session_id: int | None = None


def compute_layout_signature(*, extractor: str, stats: dict[str, Any] | None) -> str | None:
    """Compute a stable signature for extractor layout stats.

    The goal is drift detection: when the signature changes, operators should review.
    """
    if not extractor:
        return None
    payload: dict[str, Any] = {"extractor": extractor}
    if isinstance(stats, dict):
        # Keep only stable, low-cardinality fields.
        if "header" in stats:
            payload["header"] = stats.get("header")
        if "header_row" in stats:
            payload["header_row"] = stats.get("header_row")
        if "sheet" in stats:
            payload["sheet"] = stats.get("sheet")
        if "slides" in stats:
            payload["slides"] = stats.get("slides")
        if "template" in stats:
            payload["template"] = stats.get("template")
        if "approx_page_count" in stats:
            payload["approx_page_count"] = stats.get("approx_page_count")
        if "max_col" in stats:
            payload["max_col"] = stats.get("max_col")

    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def upsert_ingestion_evidence(
    session: Session,
    *,
    ingestion_id: int,
    source_id: str,
    extractor: str,
    evidence_status: str,
    stats: dict[str, Any] | None,
    evidence_path: str | None = None,
) -> IngestionEvidence:
    """Upsert evidence summary for an ingestion run (unique by ingestion_id + extractor)."""
    sig = compute_layout_signature(extractor=extractor, stats=stats)
    stats_json = json.dumps(stats or {}, ensure_ascii=False, sort_keys=True)

    row = session.exec(
        select(IngestionEvidence).where(
            IngestionEvidence.ingestion_id == ingestion_id,
            IngestionEvidence.extractor == extractor,
        )
    ).first()
    if row is None:
        row = IngestionEvidence(
            ingestion_id=ingestion_id,
            source_id=source_id,
            extractor=extractor,
            evidence_status=evidence_status or "",
            layout_signature=sig,
            stats_json=stats_json,
            evidence_path=evidence_path,
            created_at=now_utc(),
        )
        session.add(row)
    else:
        row.evidence_status = evidence_status or row.evidence_status
        row.layout_signature = sig
        row.stats_json = stats_json
        if evidence_path is not None:
            row.evidence_path = evidence_path

    session.commit()
    session.refresh(row)
    return row


def clear_quality_results(session: Session, *, ingestion_id: int) -> None:
    """Delete previous results for an ingestion (idempotent reruns)."""
    rows = session.exec(
        select(DataQualityResult).where(DataQualityResult.ingestion_id == ingestion_id)
    ).all()
    for r in rows:
        session.delete(r)
    session.commit()


def persist_quality_results(
    session: Session,
    *,
    ingestion_id: int,
    source_id: str,
    outcomes: list[CheckOutcome],
) -> list[DataQualityResult]:
    """Persist a list of outcomes as DataQualityResult rows."""
    persisted: list[DataQualityResult] = []
    for o in outcomes:
        row = DataQualityResult(
            ingestion_id=ingestion_id,
            source_id=source_id,
            session_id=o.session_id,
            scope=o.scope,
            severity=o.severity,
            status=o.status,
            check_key=o.check_key,
            message=o.message,
            details=o.details,
            created_at=now_utc(),
        )
        session.add(row)
        persisted.append(row)
    session.commit()
    for row in persisted:
        session.refresh(row)
    return persisted


def _count(session: Session, model, *where) -> int:
    stmt = select(func.count()).select_from(model)
    for cond in where:
        stmt = stmt.where(cond)
    return int(session.exec(stmt).one())


def _first(session: Session, stmt):
    return session.exec(stmt).first()


def _layout_drift_outcome(
    session: Session, *, ingestion: IngestionRun, source: Source
) -> CheckOutcome:
    """Compare evidence signatures between current and previous ingestions for the same source."""
    cur = _first(
        session,
        select(IngestionEvidence)
        .where(IngestionEvidence.ingestion_id == ingestion.id)
        .order_by(IngestionEvidence.created_at.desc()),
    )
    if cur is None or not cur.layout_signature:
        return CheckOutcome(
            check_key="layout.signature_present",
            scope=DataQualityScope.STAGING,
            severity=DataQualitySeverity.WARN,
            status=DataQualityStatus.SKIP,
            message="Sem ingestion_evidence/layout_signature para comparar drift",
        )

    prev = _first(
        session,
        select(IngestionEvidence)
        .join(IngestionRun, IngestionRun.id == IngestionEvidence.ingestion_id)
        .where(IngestionEvidence.source_id == source.source_id)
        .where(IngestionRun.started_at < ingestion.started_at)
        .order_by(IngestionRun.started_at.desc())
        .limit(1),
    )
    if prev is None or not prev.layout_signature:
        return CheckOutcome(
            check_key="layout.drift",
            scope=DataQualityScope.STAGING,
            severity=DataQualitySeverity.WARN,
            status=DataQualityStatus.SKIP,
            message="Sem execucao anterior com layout_signature para comparar drift",
        )

    if prev.layout_signature != cur.layout_signature:
        return CheckOutcome(
            check_key="layout.drift",
            scope=DataQualityScope.STAGING,
            severity=DataQualitySeverity.WARN,
            status=DataQualityStatus.FAIL,
            message="Possivel drift de layout detectado (assinatura mudou vs execucao anterior)",
            details=f"prev_sig={prev.layout_signature} cur_sig={cur.layout_signature}",
        )

    return CheckOutcome(
        check_key="layout.drift",
        scope=DataQualityScope.STAGING,
        severity=DataQualitySeverity.WARN,
        status=DataQualityStatus.PASS,
        message="Sem drift de layout (assinatura igual a execucao anterior)",
    )


def _optin_checks(session: Session, *, ingestion_id: int) -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []

    rows = _count(session, OptinTransaction, OptinTransaction.ingestion_id == ingestion_id)
    if rows <= 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.rows_nonzero",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.FAIL,
                message="Nenhuma linha carregada em optin_transactions para esta ingestao",
            )
        )
        return outcomes

    outcomes.append(
        CheckOutcome(
            check_key="canonical.optin.rows_nonzero",
            scope=DataQualityScope.CANONICAL,
            severity=DataQualitySeverity.ERROR,
            status=DataQualityStatus.PASS,
            message="Opt-in carregado (linhas > 0)",
            details=f"rows={rows}",
        )
    )

    bad_qty = _count(
        session,
        OptinTransaction,
        OptinTransaction.ingestion_id == ingestion_id,
        OptinTransaction.ticket_qty.is_not(None),
        OptinTransaction.ticket_qty <= 0,
    )
    if bad_qty > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.ticket_qty_positive",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.FAIL,
                message="ticket_qty <= 0 em optin_transactions",
                details=f"bad_rows={bad_qty}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.ticket_qty_positive",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.PASS,
                message="ticket_qty valida (nao ha <= 0)",
            )
        )

    unmapped = session.exec(
        select(func.count())
        .select_from(OptinTransaction)
        .where(OptinTransaction.ingestion_id == ingestion_id)
        .where(OptinTransaction.ticket_category_norm.is_not(None))
        .where(
            ~OptinTransaction.ticket_category_norm.in_(
                select(TicketCategorySegmentMap.ticket_category_norm)
            )
        )
    ).one()
    unmapped_int = int(unmapped or 0)
    if unmapped_int > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.ticket_category_mapped",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.FAIL,
                message="Categorias de ingresso sem mapeamento para segmento BB",
                details=f"unmapped={unmapped_int}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.ticket_category_mapped",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.PASS,
                message="Todas as categorias de ingresso estao mapeadas",
            )
        )

    missing_purchase_date = _count(
        session,
        OptinTransaction,
        OptinTransaction.ingestion_id == ingestion_id,
        OptinTransaction.purchase_date.is_(None),
    )
    if missing_purchase_date > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.purchase_date_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.FAIL,
                message="Linhas de opt-in sem purchase_date",
                details=f"missing={missing_purchase_date}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.optin.purchase_date_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.PASS,
                message="purchase_date preenchida",
            )
        )

    return outcomes


def _festival_leads_checks(session: Session, *, ingestion_id: int) -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    rows = _count(session, FestivalLead, FestivalLead.ingestion_id == ingestion_id)
    if rows <= 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.festival_leads.rows_nonzero",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.FAIL,
                message="Nenhuma linha carregada em festival_leads para esta ingestao",
            )
        )
        return outcomes

    outcomes.append(
        CheckOutcome(
            check_key="canonical.festival_leads.rows_nonzero",
            scope=DataQualityScope.CANONICAL,
            severity=DataQualitySeverity.WARN,
            status=DataQualityStatus.PASS,
            message="Leads do festival carregados (linhas > 0)",
            details=f"rows={rows}",
        )
    )

    missing_person = _count(
        session,
        FestivalLead,
        FestivalLead.ingestion_id == ingestion_id,
        FestivalLead.person_key_hash.is_(None),
    )
    if missing_person > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.festival_leads.person_key_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.FAIL,
                message="Leads sem person_key_hash (cpf_hash/email_hash ausentes)",
                details=f"missing={missing_person}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.festival_leads.person_key_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.PASS,
                message="person_key_hash preenchido",
            )
        )

    missing_date = _count(
        session,
        FestivalLead,
        FestivalLead.ingestion_id == ingestion_id,
        FestivalLead.lead_created_date.is_(None),
    )
    if missing_date > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.festival_leads.created_date_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.FAIL,
                message="Leads sem lead_created_date",
                details=f"missing={missing_date}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.festival_leads.created_date_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.PASS,
                message="lead_created_date preenchido",
            )
        )

    return outcomes


def _access_control_checks(session: Session, *, ingestion_id: int) -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    rows = _count(session, AttendanceAccessControl, AttendanceAccessControl.ingestion_id == ingestion_id)
    if rows <= 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.access_control.rows_nonzero",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.FAIL,
                message="Nenhuma linha carregada em attendance_access_control para esta ingestao (template vazio?)",
            )
        )
        return outcomes

    outcomes.append(
        CheckOutcome(
            check_key="canonical.access_control.rows_nonzero",
            scope=DataQualityScope.CANONICAL,
            severity=DataQualitySeverity.ERROR,
            status=DataQualityStatus.PASS,
            message="Controle de acesso carregado (linhas > 0)",
            details=f"rows={rows}",
        )
    )

    bad_presentes = _count(
        session,
        AttendanceAccessControl,
        AttendanceAccessControl.ingestion_id == ingestion_id,
        AttendanceAccessControl.ingressos_validos.is_not(None),
        AttendanceAccessControl.presentes.is_not(None),
        AttendanceAccessControl.presentes > AttendanceAccessControl.ingressos_validos,
    )
    if bad_presentes > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.access_control.presentes_le_validos",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.FAIL,
                message="presentes > ingressos_validos no controle de acesso",
                details=f"bad_rows={bad_presentes}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.access_control.presentes_le_validos",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.PASS,
                message="presentes <= ingressos_validos",
            )
        )

    # Reconciliacao: quando os tres campos existem, validar a soma.
    bad_sum = _count(
        session,
        AttendanceAccessControl,
        AttendanceAccessControl.ingestion_id == ingestion_id,
        AttendanceAccessControl.ingressos_validos.is_not(None),
        AttendanceAccessControl.presentes.is_not(None),
        AttendanceAccessControl.ausentes.is_not(None),
        (AttendanceAccessControl.presentes + AttendanceAccessControl.ausentes)
        != AttendanceAccessControl.ingressos_validos,
    )
    if bad_sum > 0:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.access_control.reconcile_validos_presentes_ausentes",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.FAIL,
                message="Reconciliacao falhou: presentes + ausentes != ingressos_validos",
                details=f"bad_rows={bad_sum}",
            )
        )
    else:
        outcomes.append(
            CheckOutcome(
                check_key="canonical.access_control.reconcile_validos_presentes_ausentes",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.ERROR,
                status=DataQualityStatus.PASS,
                message="Reconciliacao OK (quando aplicavel)",
            )
        )

    return outcomes


def run_quality_checks_for_ingestion(
    session: Session,
    *,
    ingestion_id: int,
    clear_existing: bool = True,
) -> list[DataQualityResult]:
    """Run quality checks for a single ingestion and persist results."""
    ingestion = session.get(IngestionRun, ingestion_id)
    if ingestion is None:
        raise ValueError(f"Ingestion nao encontrada: {ingestion_id}")
    source = session.get(Source, ingestion.source_id)
    if source is None:
        raise ValueError(f"Source nao registrada: {ingestion.source_id}")

    if clear_existing:
        clear_quality_results(session, ingestion_id=ingestion_id)

    outcomes: list[CheckOutcome] = []

    # Drift detection (staging evidence), best-effort.
    outcomes.append(_layout_drift_outcome(session, ingestion=ingestion, source=source))

    # Base checks per source kind.
    if source.kind == SourceKind.XLSX:
        optin_rows = _count(session, OptinTransaction, OptinTransaction.ingestion_id == ingestion_id)
        lead_rows = _count(session, FestivalLead, FestivalLead.ingestion_id == ingestion_id)
        if optin_rows > 0:
            outcomes.extend(_optin_checks(session, ingestion_id=ingestion_id))
        if lead_rows > 0:
            outcomes.extend(_festival_leads_checks(session, ingestion_id=ingestion_id))
        if optin_rows == 0 and lead_rows == 0:
            outcomes.append(
                CheckOutcome(
                    check_key="canonical.xlsx.rows_nonzero",
                    scope=DataQualityScope.CANONICAL,
                    severity=DataQualitySeverity.ERROR,
                    status=DataQualityStatus.FAIL,
                    message="Fonte XLSX sem carga canonical (optin_transactions/festival_leads vazias)",
                )
            )

    elif source.kind == SourceKind.PDF:
        # Only access control has canonical loader at this stage.
        ac_rows = _count(
            session,
            AttendanceAccessControl,
            AttendanceAccessControl.ingestion_id == ingestion_id,
        )
        if ac_rows > 0:
            outcomes.extend(_access_control_checks(session, ingestion_id=ingestion_id))
        else:
            # Determine template type from evidence (if available) to set severity.
            ev = _first(
                session,
                select(IngestionEvidence)
                .where(IngestionEvidence.ingestion_id == ingestion_id)
                .order_by(IngestionEvidence.created_at.desc()),
            )
            template = None
            if ev and ev.stats_json:
                try:
                    template = (json.loads(ev.stats_json) or {}).get("template")
                except Exception:
                    template = None

            severity = DataQualitySeverity.ERROR if template == "access_control" else DataQualitySeverity.WARN
            outcomes.append(
                CheckOutcome(
                    check_key="canonical.pdf.rows_nonzero",
                    scope=DataQualityScope.CANONICAL,
                    severity=severity,
                    status=DataQualityStatus.FAIL,
                    message="Fonte PDF sem carga canonical (provavel template assistido nao preenchido ou loader ausente)",
                    details=f"template={template}",
                )
            )

    elif source.kind == SourceKind.PPTX:
        # No canonical loader yet; validate staging evidence stats when available.
        ev = _first(
            session,
            select(IngestionEvidence)
            .where(IngestionEvidence.ingestion_id == ingestion_id)
            .order_by(IngestionEvidence.created_at.desc()),
        )
        slides = None
        if ev and ev.stats_json:
            try:
                slides = (json.loads(ev.stats_json) or {}).get("slides")
            except Exception:
                slides = None
        if isinstance(slides, int) and slides > 0:
            outcomes.append(
                CheckOutcome(
                    check_key="staging.pptx.slides_nonzero",
                    scope=DataQualityScope.STAGING,
                    severity=DataQualitySeverity.ERROR,
                    status=DataQualityStatus.PASS,
                    message="PPTX extraido (slides > 0)",
                    details=f"slides={slides}",
                )
            )
        else:
            outcomes.append(
                CheckOutcome(
                    check_key="staging.pptx.slides_nonzero",
                    scope=DataQualityScope.STAGING,
                    severity=DataQualitySeverity.ERROR,
                    status=DataQualityStatus.FAIL,
                    message="PPTX sem slides extraidos (ou evidencia ausente)",
                    details=f"slides={slides}",
                )
            )
        outcomes.append(
            CheckOutcome(
                check_key="canonical.pptx.loader_present",
                scope=DataQualityScope.CANONICAL,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.SKIP,
                message="Loader canonical para PPTX ainda nao implementado",
            )
        )

    else:
        outcomes.append(
            CheckOutcome(
                check_key="dq.runner.kind_supported",
                scope=DataQualityScope.STAGING,
                severity=DataQualitySeverity.WARN,
                status=DataQualityStatus.SKIP,
                message=f"Checks nao implementados para kind={source.kind}",
            )
        )

    return persist_quality_results(
        session,
        ingestion_id=ingestion_id,
        source_id=source.source_id,
        outcomes=outcomes,
    )


def quality_gate_blocked(session: Session, *, ingestion_id: int) -> bool:
    """Return True when there is any ERROR/FAIL for the ingestion."""
    stmt = select(func.count()).select_from(DataQualityResult).where(
        DataQualityResult.ingestion_id == ingestion_id,
        DataQualityResult.severity == DataQualitySeverity.ERROR,
        DataQualityResult.status == DataQualityStatus.FAIL,
    )
    return int(session.exec(stmt).one()) > 0


def quality_summary(session: Session, *, ingestion_id: int) -> dict[str, int]:
    """Return simple counts of outcomes for an ingestion."""
    total = _count(session, DataQualityResult, DataQualityResult.ingestion_id == ingestion_id)
    err_fail = _count(
        session,
        DataQualityResult,
        DataQualityResult.ingestion_id == ingestion_id,
        DataQualityResult.severity == DataQualitySeverity.ERROR,
        DataQualityResult.status == DataQualityStatus.FAIL,
    )
    warn_fail = _count(
        session,
        DataQualityResult,
        DataQualityResult.ingestion_id == ingestion_id,
        DataQualityResult.severity == DataQualitySeverity.WARN,
        DataQualityResult.status == DataQualityStatus.FAIL,
    )
    passed = _count(
        session,
        DataQualityResult,
        DataQualityResult.ingestion_id == ingestion_id,
        DataQualityResult.status == DataQualityStatus.PASS,
    )
    return {
        "total": total,
        "error_fail": err_fail,
        "warn_fail": warn_fail,
        "passed": passed,
    }

