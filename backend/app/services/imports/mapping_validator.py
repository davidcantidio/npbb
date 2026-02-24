"""Validacao reutilizavel de mapeamento por dominio."""

from __future__ import annotations

from collections import Counter

from app.services.imports.contracts import ImportDomainSpec, ImportValidationResult


def validate_mappings(
    domain_spec: ImportDomainSpec,
    mappings: list[object],
) -> ImportValidationResult:
    mapped_fields = [str(getattr(item, "campo", "") or "").strip() for item in mappings]
    mapped_fields = [field for field in mapped_fields if field]

    unknown_fields = tuple(sorted({field for field in mapped_fields if field not in domain_spec.field_names()}))
    duplicates_counter = Counter(mapped_fields)
    duplicated_fields = tuple(sorted(field for field, total in duplicates_counter.items() if total > 1))

    required_fields = {field.name for field in domain_spec.fields if field.required}
    missing_required_fields = tuple(sorted(required_fields - set(mapped_fields)))
    missing_required_key_fields = tuple(sorted(set(domain_spec.required_key_fields) - set(mapped_fields)))

    ok = not (
        unknown_fields
        or duplicated_fields
        or missing_required_fields
        or missing_required_key_fields
    )

    return ImportValidationResult(
        ok=ok,
        missing_required_fields=missing_required_fields,
        missing_required_key_fields=missing_required_key_fields,
        unknown_fields=unknown_fields,
        duplicated_fields=duplicated_fields,
    )
