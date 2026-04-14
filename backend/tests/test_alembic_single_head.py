from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_single_head() -> None:
    """Verifica que existe apenas uma head de migration (single head)."""
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_ini = backend_dir / "alembic.ini"

    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(backend_dir / "alembic"))

    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()

    assert len(heads) == 1, f"Multiple heads found: {heads}. Run 'alembic merge' if needed."


def test_lead_evento_migration_exists() -> None:
    """Verifica que existe migration versionada para lead_evento (ISSUE-F1-01-002)."""
    backend_dir = Path(__file__).resolve().parents[1]
    versions_dir = backend_dir / "alembic" / "versions"

    migration_files = list(versions_dir.glob("*.py"))
    lead_evento_mentions = []

    for mf in migration_files:
        content = mf.read_text(encoding="utf-8")
        if "lead_evento" in content.lower() or "LeadEvento" in content or "20260317_add_lead_evento" in mf.name:
            lead_evento_mentions.append(mf.name)

    assert len(lead_evento_mentions) > 0, (
        "Nenhuma migration menciona 'lead_evento'. "
        "ISSUE-F1-01-002 requer migration versionada para a tabela."
    )


def test_lead_evento_canonical_origin_migration_exists() -> None:
    """Verifica que a migration canonica cobre enum legado, checks e triggers de ativacao."""
    backend_dir = Path(__file__).resolve().parents[1]
    versions_dir = backend_dir / "alembic" / "versions"

    matching_files: list[str] = []
    for migration_file in versions_dir.glob("*.py"):
        content = migration_file.read_text(encoding="utf-8")
        if (
            "validate_lead_evento_activation_link" in content
            and "prevent_ativacao_lead_delete_if_linked" in content
            and "ck_lead_evento_tipo_lead_proponente" in content
            and "ck_lead_evento_source_kind_ativacao_requires_tipo_lead" in content
            and "leadeventosourcekind" in content
        ):
            matching_files.append(migration_file.name)

    assert matching_files, (
        "Nenhuma migration encontrada para a canonicalizacao de origem do lead_evento "
        "(enum legado, checks e triggers de ativacao)."
    )
