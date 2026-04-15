from app.models.lead_public_models import LeadEvento, LeadEventoSourceKind


def test_lead_evento_source_kind_uses_canonical_enum_values() -> None:
    enum_type = LeadEvento.__table__.c.source_kind.type
    assert list(enum_type.enums) == [member.value for member in LeadEventoSourceKind]
