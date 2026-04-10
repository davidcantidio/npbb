"""Canonical lead-event link helpers."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.lead_batch import LeadBatch
from app.models.models import (
    Ativacao,
    AtivacaoLead,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    TipoLead,
    TipoResponsavel,
)

_SOURCE_PRIORITY: dict[LeadEventoSourceKind, int] = {
    LeadEventoSourceKind.EVENT_NAME_BACKFILL: 1,
    LeadEventoSourceKind.LEAD_BATCH: 2,
    LeadEventoSourceKind.EVENT_DIRECT: 3,
    LeadEventoSourceKind.ACTIVATION: 4,
    LeadEventoSourceKind.MANUAL_RECONCILED: 5,
}


@dataclass(frozen=True)
class LeadEventoEnsureResult:
    lead_evento: LeadEvento
    action: str


@dataclass(frozen=True)
class EventNameResolution:
    status: str
    evento_id: int | None = None


@dataclass(frozen=True)
class LeadEventoBackfillReport:
    created: int = 0
    updated: int = 0
    existing: int = 0
    unresolved_missing_event: int = 0
    unresolved_ambiguous_event: int = 0


def normalize_event_name(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower()
    return normalized or None


def resolve_unique_evento_by_name(session: Session, event_name: str | None) -> EventNameResolution:
    normalized = normalize_event_name(event_name)
    if not normalized:
        return EventNameResolution(status="missing")

    eventos = session.exec(
        select(Evento.id, Evento.nome).where(Evento.nome.is_not(None))
    ).all()
    matches = [
        int(evento_id)
        for evento_id, evento_nome in eventos
        if normalize_event_name(str(evento_nome)) == normalized
    ]
    if not matches:
        return EventNameResolution(status="missing")
    unique_matches = sorted(set(matches))
    if len(unique_matches) > 1:
        return EventNameResolution(status="ambiguous")
    return EventNameResolution(status="resolved", evento_id=unique_matches[0])


def _should_upgrade_source(
    current: LeadEventoSourceKind,
    incoming: LeadEventoSourceKind,
) -> bool:
    return _SOURCE_PRIORITY[incoming] > _SOURCE_PRIORITY[current]


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _apply_lead_origin_metadata(
    lead_evento: LeadEvento,
    *,
    tipo_lead: TipoLead | None,
    responsavel_tipo: TipoResponsavel | None,
    responsavel_nome: str | None,
    responsavel_agencia_id: int | None,
) -> bool:
    changed = False
    if tipo_lead is not None and lead_evento.tipo_lead != tipo_lead:
        lead_evento.tipo_lead = tipo_lead
        changed = True
    if responsavel_tipo is not None and lead_evento.responsavel_tipo != responsavel_tipo:
        lead_evento.responsavel_tipo = responsavel_tipo
        changed = True
    if responsavel_nome is not None:
        normalized_responsavel_nome = _normalize_optional_text(responsavel_nome)
        if lead_evento.responsavel_nome != normalized_responsavel_nome:
            lead_evento.responsavel_nome = normalized_responsavel_nome
            changed = True
    if (
        responsavel_agencia_id is not None
        and lead_evento.responsavel_agencia_id != responsavel_agencia_id
    ):
        lead_evento.responsavel_agencia_id = responsavel_agencia_id
        changed = True
    return changed


def ensure_lead_event(
    session: Session,
    *,
    lead_id: int,
    evento_id: int,
    source_kind: LeadEventoSourceKind,
    source_ref_id: int | None = None,
    tipo_lead: TipoLead | None = None,
    responsavel_tipo: TipoResponsavel | None = None,
    responsavel_nome: str | None = None,
    responsavel_agencia_id: int | None = None,
) -> LeadEventoEnsureResult:
    existing = session.exec(
        select(LeadEvento)
        .where(LeadEvento.lead_id == lead_id)
        .where(LeadEvento.evento_id == evento_id)
    ).first()
    if existing is not None:
        changed = False
        if _should_upgrade_source(existing.source_kind, source_kind):
            existing.source_kind = source_kind
            existing.source_ref_id = source_ref_id
            changed = True
        elif existing.source_ref_id is None and source_ref_id is not None:
            existing.source_ref_id = source_ref_id
            changed = True
        changed = (
            _apply_lead_origin_metadata(
                existing,
                tipo_lead=tipo_lead,
                responsavel_tipo=responsavel_tipo,
                responsavel_nome=responsavel_nome,
                responsavel_agencia_id=responsavel_agencia_id,
            )
            or changed
        )
        if changed:
            session.add(existing)
            return LeadEventoEnsureResult(lead_evento=existing, action="updated")
        return LeadEventoEnsureResult(lead_evento=existing, action="existing")

    lead_evento = LeadEvento(
        lead_id=lead_id,
        evento_id=evento_id,
        source_kind=source_kind,
        source_ref_id=source_ref_id,
        tipo_lead=tipo_lead,
        responsavel_tipo=responsavel_tipo,
        responsavel_nome=_normalize_optional_text(responsavel_nome),
        responsavel_agencia_id=responsavel_agencia_id,
    )
    try:
        with session.begin_nested():
            session.add(lead_evento)
            session.flush()
    except IntegrityError:
        existing = session.exec(
            select(LeadEvento)
            .where(LeadEvento.lead_id == lead_id)
            .where(LeadEvento.evento_id == evento_id)
        ).first()
        if existing is None:
            raise
        if _apply_lead_origin_metadata(
            existing,
            tipo_lead=tipo_lead,
            responsavel_tipo=responsavel_tipo,
            responsavel_nome=responsavel_nome,
            responsavel_agencia_id=responsavel_agencia_id,
        ):
            session.add(existing)
            return LeadEventoEnsureResult(lead_evento=existing, action="updated")
        return LeadEventoEnsureResult(lead_evento=existing, action="existing")
    return LeadEventoEnsureResult(lead_evento=lead_evento, action="created")


def backfill_lead_event_links(session: Session) -> LeadEventoBackfillReport:
    created = 0
    updated = 0
    existing = 0
    unresolved_missing_event = 0
    unresolved_ambiguous_event = 0

    activation_rows = session.exec(
        select(AtivacaoLead.lead_id, Ativacao.evento_id, AtivacaoLead.id)
        .select_from(AtivacaoLead)
        .join(Ativacao, Ativacao.id == AtivacaoLead.ativacao_id)
    ).all()
    for lead_id, evento_id, ativacao_lead_id in activation_rows:
        result = ensure_lead_event(
            session,
            lead_id=int(lead_id),
            evento_id=int(evento_id),
            source_kind=LeadEventoSourceKind.ACTIVATION,
            source_ref_id=int(ativacao_lead_id),
        )
        if result.action == "created":
            created += 1
        elif result.action == "updated":
            updated += 1
        else:
            existing += 1

    batch_rows = session.exec(
        select(Lead.id, LeadBatch.evento_id, LeadBatch.id)
        .select_from(Lead)
        .join(LeadBatch, Lead.batch_id == LeadBatch.id)
        .where(LeadBatch.evento_id.is_not(None))
    ).all()
    for lead_id, evento_id, batch_id in batch_rows:
        result = ensure_lead_event(
            session,
            lead_id=int(lead_id),
            evento_id=int(evento_id),
            source_kind=LeadEventoSourceKind.LEAD_BATCH,
            source_ref_id=int(batch_id),
        )
        if result.action == "created":
            created += 1
        elif result.action == "updated":
            updated += 1
        else:
            existing += 1

    leads = session.exec(
        select(Lead.id, Lead.evento_nome)
        .where(Lead.evento_nome.is_not(None))
    ).all()
    for lead_id, event_name in leads:
        resolution = resolve_unique_evento_by_name(session, str(event_name))
        if resolution.status == "missing":
            unresolved_missing_event += 1
            continue
        if resolution.status == "ambiguous":
            unresolved_ambiguous_event += 1
            continue
        result = ensure_lead_event(
            session,
            lead_id=int(lead_id),
            evento_id=int(resolution.evento_id),
            source_kind=LeadEventoSourceKind.EVENT_NAME_BACKFILL,
        )
        if result.action == "created":
            created += 1
        elif result.action == "updated":
            updated += 1
        else:
            existing += 1

    return LeadEventoBackfillReport(
        created=created,
        updated=updated,
        existing=existing,
        unresolved_missing_event=unresolved_missing_event,
        unresolved_ambiguous_event=unresolved_ambiguous_event,
    )
