"""Servico de alias generico por dominio de importacao."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.models import ImportAlias
from app.utils.text_normalize import normalize_text


def normalize_alias_value(value: str) -> str:
    return normalize_text(value or "")


def find_alias(
    session: Session,
    *,
    domain: str,
    field_name: str,
    source_value: str,
) -> ImportAlias | None:
    normalized = normalize_alias_value(source_value)
    if not normalized:
        return None
    return session.exec(
        select(ImportAlias).where(
            ImportAlias.domain == domain,
            ImportAlias.field_name == field_name,
            ImportAlias.source_normalized == normalized,
        )
    ).first()


def upsert_alias(
    session: Session,
    *,
    domain: str,
    field_name: str,
    source_value: str,
    canonical_value: str | None = None,
    canonical_ref_id: int | None = None,
) -> ImportAlias:
    source_clean = (source_value or "").strip()
    normalized = normalize_alias_value(source_clean)
    if not normalized:
        raise ValueError("source_value vazio")

    canonical_clean = (canonical_value or "").strip() or None
    current = session.exec(
        select(ImportAlias).where(
            ImportAlias.domain == domain,
            ImportAlias.field_name == field_name,
            ImportAlias.source_normalized == normalized,
        )
    ).first()
    if current:
        changed = False
        if current.source_value != source_clean:
            current.source_value = source_clean
            changed = True
        if current.canonical_value != canonical_clean:
            current.canonical_value = canonical_clean
            changed = True
        if current.canonical_ref_id != canonical_ref_id:
            current.canonical_ref_id = canonical_ref_id
            changed = True
        if changed:
            session.add(current)
            session.commit()
            session.refresh(current)
        return current

    created = ImportAlias(
        domain=domain,
        field_name=field_name,
        source_value=source_clean,
        source_normalized=normalized,
        canonical_value=canonical_clean,
        canonical_ref_id=canonical_ref_id,
    )
    session.add(created)
    session.commit()
    session.refresh(created)
    return created
