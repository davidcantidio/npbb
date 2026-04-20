"""Corrige `Lead.evento_nome` contaminado por rotulos de origem.

Pre-requisitos:
- Executar a partir de `backend/`.
- Configurar `DIRECT_URL` ou `DATABASE_URL` para acesso ao banco.

Uso:
- Dry-run: `python -m scripts.fix_contaminated_lead_event_names`
- Dry-run explicito: `python -m scripts.fix_contaminated_lead_event_names --dry-run`
- Execucao real: `python -m scripts.fix_contaminated_lead_event_names --apply`
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sqlmodel import Session, select

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.lead_batch import LeadBatch  # noqa: E402
from app.models.models import Evento, Lead, LeadEvento, LeadEventoSourceKind  # noqa: E402
from app.utils.text_normalize import normalize_text  # noqa: E402
from scripts.seed_common import get_engine_for_scripts  # noqa: E402

CONTAMINATED_EVENT_NAME_LABELS = frozenset({"ativacao", "proponente"})
LEAD_EVENT_SOURCE_PRIORITY = {
    LeadEventoSourceKind.MANUAL_RECONCILED: 0,
    LeadEventoSourceKind.ACTIVATION: 1,
    LeadEventoSourceKind.EVENT_DIRECT: 2,
    LeadEventoSourceKind.LEAD_BATCH: 3,
    LeadEventoSourceKind.EVENT_NAME_BACKFILL: 4,
}


@dataclass(frozen=True)
class LeadEventNameFix:
    lead_id: int
    old_evento_nome: str | None
    new_evento_nome: str
    resolved_evento_id: int
    source: str


@dataclass(frozen=True)
class LeadEventNameManualReview:
    lead_id: int
    old_evento_nome: str | None
    reason: str


@dataclass(frozen=True)
class FixSummary:
    candidates: int
    fixed: int
    manual_review: int
    dry_run: bool


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Corrige leads com `evento_nome` contaminado por `Ativacao`/`Proponente`."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcula as correcoes sem persistir alteracoes.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Persiste as correcoes calculadas.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _is_contaminated_event_name(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    return normalize_text(value) in CONTAMINATED_EVENT_NAME_LABELS


def find_candidate_leads(session: Session) -> list[Lead]:
    leads = session.exec(select(Lead).where(Lead.evento_nome.is_not(None)).order_by(Lead.id)).all()
    return [lead for lead in leads if _is_contaminated_event_name(lead.evento_nome)]


def _event_name_by_id(session: Session, evento_id: int | None) -> str | None:
    if evento_id is None:
        return None
    evento = session.get(Evento, evento_id)
    if evento is None or not evento.nome or not evento.nome.strip():
        return None
    return evento.nome.strip()


def _preferred_lead_event_link(session: Session, lead_id: int) -> LeadEvento | None:
    lead_eventos = list(
        session.exec(select(LeadEvento).where(LeadEvento.lead_id == lead_id)).all()
    )
    ordered = sorted(
        lead_eventos,
        key=lambda item: (
            LEAD_EVENT_SOURCE_PRIORITY.get(item.source_kind, 99),
            -(item.created_at.timestamp() if item.created_at is not None else 0.0),
            -(item.id or 0),
        ),
    )
    for lead_evento in ordered:
        if _event_name_by_id(session, lead_evento.evento_id):
            return lead_evento
    return None


def _resolve_fix_for_lead(
    session: Session,
    lead: Lead,
) -> LeadEventNameFix | LeadEventNameManualReview:
    if lead.id is None:
        return LeadEventNameManualReview(
            lead_id=0,
            old_evento_nome=lead.evento_nome,
            reason="Lead sem ID nao pode ser corrigido.",
        )

    preferred_link = _preferred_lead_event_link(session, int(lead.id))
    if preferred_link is not None:
        event_name = _event_name_by_id(session, preferred_link.evento_id)
        if event_name and not _is_contaminated_event_name(event_name):
            return LeadEventNameFix(
                lead_id=int(lead.id),
                old_evento_nome=lead.evento_nome,
                new_evento_nome=event_name,
                resolved_evento_id=int(preferred_link.evento_id),
                source=f"lead_evento:{preferred_link.source_kind.value}",
            )

    batch = session.get(LeadBatch, lead.batch_id) if lead.batch_id is not None else None
    if batch is not None and batch.evento_id is not None:
        event_name = _event_name_by_id(session, batch.evento_id)
        if event_name and not _is_contaminated_event_name(event_name):
            return LeadEventNameFix(
                lead_id=int(lead.id),
                old_evento_nome=lead.evento_nome,
                new_evento_nome=event_name,
                resolved_evento_id=int(batch.evento_id),
                source="lead_batch",
            )

    return LeadEventNameManualReview(
        lead_id=int(lead.id),
        old_evento_nome=lead.evento_nome,
        reason="Sem LeadEvento ou LeadBatch com evento canonicamente resolvivel.",
    )


def build_fix_plan(
    session: Session,
    candidates: Sequence[Lead],
) -> tuple[list[LeadEventNameFix], list[LeadEventNameManualReview]]:
    fixes: list[LeadEventNameFix] = []
    manual_reviews: list[LeadEventNameManualReview] = []

    for lead in candidates:
        resolution = _resolve_fix_for_lead(session, lead)
        if isinstance(resolution, LeadEventNameFix):
            fixes.append(resolution)
        else:
            manual_reviews.append(resolution)

    return fixes, manual_reviews


def apply_updates(
    session: Session,
    fixes: Sequence[LeadEventNameFix],
    *,
    dry_run: bool,
) -> int:
    if not fixes:
        return 0

    updates_by_id = {fix.lead_id: fix for fix in fixes}
    leads = list(session.exec(select(Lead).where(Lead.id.in_(list(updates_by_id)))).all())

    try:
        for lead in leads:
            if lead.id is None:
                raise RuntimeError("Lead sem ID nao pode ser atualizado.")
            lead.evento_nome = updates_by_id[int(lead.id)].new_evento_nome
            session.add(lead)

        if dry_run:
            session.flush()
            session.rollback()
            return len(fixes)

        session.commit()
        return len(fixes)
    except Exception:
        session.rollback()
        raise


def execute_fix(
    session: Session,
    *,
    dry_run: bool,
) -> tuple[FixSummary, list[LeadEventNameFix], list[LeadEventNameManualReview]]:
    candidates = find_candidate_leads(session)
    fixes, manual_reviews = build_fix_plan(session, candidates)
    fixed = apply_updates(session, fixes, dry_run=dry_run)
    return (
        FixSummary(
            candidates=len(candidates),
            fixed=fixed,
            manual_review=len(manual_reviews),
            dry_run=dry_run,
        ),
        fixes,
        manual_reviews,
    )


def print_fixes(fixes: Sequence[LeadEventNameFix], *, dry_run: bool) -> None:
    prefix = "[DRY-RUN]" if dry_run else "[APPLY]"
    if not fixes:
        print(f"{prefix} Nenhuma correcao automatica encontrada.")
        return

    for fix in fixes:
        print(
            f"{prefix} lead_id={fix.lead_id} "
            f"evento_nome={fix.old_evento_nome or '<vazio>'} -> {fix.new_evento_nome} "
            f"(evento_id={fix.resolved_evento_id}, source={fix.source})"
        )


def print_manual_reviews(reviews: Sequence[LeadEventNameManualReview]) -> None:
    if not reviews:
        return
    print("[REVIEW] Leads que exigem revisao manual:")
    for review in reviews:
        print(
            f"  lead_id={review.lead_id} "
            f"evento_nome={review.old_evento_nome or '<vazio>'} "
            f"motivo={review.reason}"
        )


def print_summary(summary: FixSummary) -> None:
    mode = "DRY-RUN" if summary.dry_run else "EXECUCAO"
    print(f"{mode}: candidatos={summary.candidates}")
    print(f"Correcoes automaticas: {summary.fixed}")
    print(f"Revisao manual: {summary.manual_review}")
    if summary.dry_run:
        print("Nenhuma alteracao foi persistida.")
    else:
        print("Alteracoes persistidas com sucesso.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    dry_run = not args.apply
    engine = get_engine_for_scripts()

    with Session(engine) as session:
        summary, fixes, manual_reviews = execute_fix(session, dry_run=dry_run)

    print_fixes(fixes, dry_run=dry_run)
    print_manual_reviews(manual_reviews)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
