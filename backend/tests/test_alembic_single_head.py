from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_single_head() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_ini = backend_dir / "alembic.ini"

    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(backend_dir / "alembic"))

    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()

    assert len(heads) == 1
