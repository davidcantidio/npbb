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
