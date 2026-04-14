"""Canonical lead-event link helpers."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.lead_batch import LeadBatch
from app.models.models import (
    Agencia,
    Ativacao,
    AtivacaoLead,
    Diretoria,
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
_NON_ACTIVATION_SOURCE_KINDS = frozenset(
    {
        LeadEventoSourceKind.EVENT_DIRECT,
        LeadEventoSourceKind.LEAD_BATCH,
        LeadEventoSourceKind.EVENT_NAME_BACKFILL,
        LeadEventoSourceKind.MANUAL_RECONCILED,
    }
)


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


@dataclass(frozen=True)
class CanonicalLeadOriginMetadata:
    tipo_lead: TipoLead
    responsavel_tipo: TipoResponsavel
    responsavel_nome: str
    responsavel_agencia_id: int | None


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


def _get_evento_or_raise(session: Session, evento_id: int) -> Evento:
    evento = session.get(Evento, evento_id)
    if evento is None:
        raise ValueError(f"Evento {evento_id} nao encontrado para canonicalizacao de LeadEvento.")
    return evento


def _resolve_agencia_nome(session: Session, evento: Evento) -> str | None:
    agencia_nome = _normalize_optional_text(getattr(getattr(evento, "agencia", None), "nome", None))
    if agencia_nome:
        return agencia_nome
    if evento.agencia_id is None:
        return None
    agencia = session.get(Agencia, evento.agencia_id)
    if agencia is None:
        return None
    return _normalize_optional_text(agencia.nome)


def _resolve_proponente_nome(session: Session, evento: Evento) -> str | None:
    diretoria_nome = _normalize_optional_text(
        getattr(getattr(evento, "diretoria", None), "nome", None)
    )
    if diretoria_nome:
        return diretoria_nome
    if evento.diretoria_id is not None:
        diretoria = session.get(Diretoria, evento.diretoria_id)
        if diretoria is not None:
            diretoria_nome = _normalize_optional_text(diretoria.nome)
            if diretoria_nome:
                return diretoria_nome
    return _normalize_optional_text(evento.nome)


def _validate_activation_source_ref(
    session: Session,
    *,
    lead_id: int,
    evento_id: int,
    source_ref_id: int | None,
) -> None:
    if source_ref_id is None:
        raise ValueError(
            "LeadEvento de ativacao exige source_ref_id apontando para ativacao_lead.id."
        )
    ativacao_lead = session.get(AtivacaoLead, source_ref_id)
    if ativacao_lead is None:
        raise ValueError(
            f"LeadEvento de ativacao exige AtivacaoLead valido em source_ref_id={source_ref_id}."
        )
    if ativacao_lead.lead_id != lead_id:
        raise ValueError(
            f"AtivacaoLead {source_ref_id} pertence ao lead {ativacao_lead.lead_id}, "
            f"mas o LeadEvento referencia lead_id={lead_id}."
        )
    ativacao = session.get(Ativacao, ativacao_lead.ativacao_id)
    if ativacao is None or ativacao.evento_id != evento_id:
        raise ValueError(
            f"AtivacaoLead {source_ref_id} nao corresponde ao evento {evento_id} do LeadEvento."
        )


def _derive_canonical_lead_origin(
    session: Session,
    *,
    lead_id: int,
    evento_id: int,
    source_kind: LeadEventoSourceKind,
    source_ref_id: int | None,
    tipo_lead: TipoLead | None,
) -> CanonicalLeadOriginMetadata:
    evento = _get_evento_or_raise(session, evento_id)

    if source_kind == LeadEventoSourceKind.ACTIVATION:
        _validate_activation_source_ref(
            session,
            lead_id=lead_id,
            evento_id=evento_id,
            source_ref_id=source_ref_id,
        )
        if evento.agencia_id is None:
            raise ValueError(
                f"Evento {evento_id} precisa de agencia_id para canonicalizar LeadEvento de ativacao."
            )
        agencia_nome = _resolve_agencia_nome(session, evento)
        if agencia_nome is None:
            raise ValueError(
                f"Evento {evento_id} precisa de agencia.nome para canonicalizar LeadEvento de ativacao."
            )
        return CanonicalLeadOriginMetadata(
            tipo_lead=TipoLead.ATIVACAO,
            responsavel_tipo=TipoResponsavel.AGENCIA,
            responsavel_nome=agencia_nome,
            responsavel_agencia_id=evento.agencia_id,
        )

    if source_kind not in _NON_ACTIVATION_SOURCE_KINDS:
        raise ValueError(f"source_kind={source_kind!s} nao suportado para LeadEvento.")

    responsavel_nome = _resolve_proponente_nome(session, evento)
    if responsavel_nome is None:
        raise ValueError(
            f"Evento {evento_id} precisa de Diretoria.nome ou Evento.nome para canonicalizar LeadEvento."
        )

    resolved_tipo_lead = (
        TipoLead.BILHETERIA if tipo_lead == TipoLead.BILHETERIA else TipoLead.ENTRADA_EVENTO
    )
    return CanonicalLeadOriginMetadata(
        tipo_lead=resolved_tipo_lead,
        responsavel_tipo=TipoResponsavel.PROPONENTE,
        responsavel_nome=responsavel_nome,
        responsavel_agencia_id=None,
    )


def _apply_source_metadata(
    lead_evento: LeadEvento,
    *,
    source_kind: LeadEventoSourceKind,
    source_ref_id: int | None,
) -> bool:
    changed = False
    if _should_upgrade_source(lead_evento.source_kind, source_kind):
        if lead_evento.source_kind != source_kind:
            lead_evento.source_kind = source_kind
            changed = True
        if lead_evento.source_ref_id != source_ref_id:
            lead_evento.source_ref_id = source_ref_id
            changed = True
        return changed

    if lead_evento.source_kind == source_kind and source_ref_id is not None:
        if lead_evento.source_ref_id != source_ref_id:
            lead_evento.source_ref_id = source_ref_id
            changed = True
        return changed

    if lead_evento.source_ref_id is None and source_ref_id is not None:
        lead_evento.source_ref_id = source_ref_id
        changed = True
    return changed


def _resolve_effective_origin_request(
    existing: LeadEvento,
    *,
    source_kind: LeadEventoSourceKind,
    source_ref_id: int | None,
    tipo_lead: TipoLead | None,
) -> tuple[LeadEventoSourceKind, int | None, TipoLead | None]:
    if _should_upgrade_source(existing.source_kind, source_kind):
        return source_kind, source_ref_id, tipo_lead or existing.tipo_lead

    if existing.source_kind == source_kind:
        return (
            existing.source_kind,
            source_ref_id if source_ref_id is not None else existing.source_ref_id,
            tipo_lead or existing.tipo_lead,
        )

    return existing.source_kind, existing.source_ref_id, existing.tipo_lead


def _apply_lead_origin_metadata(
    lead_evento: LeadEvento,
    *,
    tipo_lead: TipoLead,
    responsavel_tipo: TipoResponsavel,
    responsavel_nome: str,
    responsavel_agencia_id: int | None,
) -> bool:
    changed = False
    if lead_evento.tipo_lead != tipo_lead:
        lead_evento.tipo_lead = tipo_lead
        changed = True
    if lead_evento.responsavel_tipo != responsavel_tipo:
        lead_evento.responsavel_tipo = responsavel_tipo
        changed = True
    normalized_responsavel_nome = _normalize_optional_text(responsavel_nome)
    if lead_evento.responsavel_nome != normalized_responsavel_nome:
        lead_evento.responsavel_nome = normalized_responsavel_nome
        changed = True
    if lead_evento.responsavel_agencia_id != responsavel_agencia_id:
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
        (
            effective_source_kind,
            effective_source_ref_id,
            effective_tipo_lead,
        ) = _resolve_effective_origin_request(
            existing,
            source_kind=source_kind,
            source_ref_id=source_ref_id,
            tipo_lead=tipo_lead,
        )
        canonical_origin = _derive_canonical_lead_origin(
            session,
            lead_id=lead_id,
            evento_id=evento_id,
            source_kind=effective_source_kind,
            source_ref_id=effective_source_ref_id,
            tipo_lead=effective_tipo_lead,
        )
        changed = _apply_source_metadata(
            existing,
            source_kind=source_kind,
            source_ref_id=source_ref_id,
        )
        changed = (
            _apply_lead_origin_metadata(
                existing,
                tipo_lead=canonical_origin.tipo_lead,
                responsavel_tipo=canonical_origin.responsavel_tipo,
                responsavel_nome=canonical_origin.responsavel_nome,
                responsavel_agencia_id=canonical_origin.responsavel_agencia_id,
            )
            or changed
        )
        if changed:
            session.add(existing)
            return LeadEventoEnsureResult(lead_evento=existing, action="updated")
        return LeadEventoEnsureResult(lead_evento=existing, action="existing")

    canonical_origin = _derive_canonical_lead_origin(
        session,
        lead_id=lead_id,
        evento_id=evento_id,
        source_kind=source_kind,
        source_ref_id=source_ref_id,
        tipo_lead=tipo_lead,
    )
    lead_evento = LeadEvento(
        lead_id=lead_id,
        evento_id=evento_id,
        source_kind=source_kind,
        source_ref_id=source_ref_id,
        tipo_lead=canonical_origin.tipo_lead,
        responsavel_tipo=canonical_origin.responsavel_tipo,
        responsavel_nome=canonical_origin.responsavel_nome,
        responsavel_agencia_id=canonical_origin.responsavel_agencia_id,
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
        (
            effective_source_kind,
            effective_source_ref_id,
            effective_tipo_lead,
        ) = _resolve_effective_origin_request(
            existing,
            source_kind=source_kind,
            source_ref_id=source_ref_id,
            tipo_lead=tipo_lead,
        )
        canonical_origin = _derive_canonical_lead_origin(
            session,
            lead_id=lead_id,
            evento_id=evento_id,
            source_kind=effective_source_kind,
            source_ref_id=effective_source_ref_id,
            tipo_lead=effective_tipo_lead,
        )
        changed = _apply_source_metadata(
            existing,
            source_kind=source_kind,
            source_ref_id=source_ref_id,
        )
        if (
            _apply_lead_origin_metadata(
                existing,
                tipo_lead=canonical_origin.tipo_lead,
                responsavel_tipo=canonical_origin.responsavel_tipo,
                responsavel_nome=canonical_origin.responsavel_nome,
                responsavel_agencia_id=canonical_origin.responsavel_agencia_id,
            )
            or changed
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
