"""Testes para scripts de migracao F2 (ISSUE-F2-02-003).

Cobre contrato do artefato (alembic_version), atomicidade do pg_restore e
prontidao de runtime na consolidacao. Usa mocks; nao requer credenciais reais.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts import backup_export_migracao, recarga_migracao


# --- T1: Contrato do artefato ---


def test_run_export_local_excludes_alembic_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Export local usa --exclude-table-data=public.alembic_version (contrato F1)."""
    captured_cmd: list[list[str]] = []

    def capture_run(cmd: list[str], *a: object, **k: object) -> MagicMock:
        captured_cmd.append(list(cmd))
        if "-f" in cmd:
            idx = cmd.index("-f") + 1
            Path(cmd[idx]).write_bytes(b"PGDMP")
        return MagicMock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", capture_run)

    backup_export_migracao.run_export_local(
        pg_dump="/usr/bin/pg_dump",
        local_url="postgresql://u:p@127.0.0.1:5432/npbb",
        out_dir=tmp_path,
    )

    assert len(captured_cmd) == 1
    cmd = captured_cmd[0]
    assert "--exclude-table-data=public.alembic_version" in cmd


def test_validate_artifact_contract_blocks_when_dump_contains_alembic_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Recarga bloqueia quando pg_restore --list indica alembic_version no artefato."""
    dump = tmp_path / "export_local.dump"
    dump.write_bytes(b"PGDMP")

    def mock_run(cmd: list[str], *a: object, **k: object) -> MagicMock:
        return MagicMock(
            returncode=0,
            stdout="1234; 1259 16384 TABLE DATA public alembic_version postgres",
            stderr="",
        )

    monkeypatch.setattr("subprocess.run", mock_run)

    with pytest.raises(SystemExit, match="alembic_version|incompativel"):
        recarga_migracao._validate_artifact_contract("/usr/bin/pg_restore", dump)


def test_validate_artifact_contract_passes_when_dump_excludes_alembic_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Recarga prossegue quando artefato nao contem alembic_version."""
    dump = tmp_path / "export_local.dump"
    dump.write_bytes(b"PGDMP")

    def mock_run(cmd: list[str], *a: object, **k: object) -> MagicMock:
        return MagicMock(
            returncode=0,
            stdout="1234; 1259 16384 TABLE DATA public users postgres",
            stderr="",
        )

    monkeypatch.setattr("subprocess.run", mock_run)

    recarga_migracao._validate_artifact_contract("/usr/bin/pg_restore", dump)
    # nao levanta


# --- T2: Atomicidade do pg_restore ---


def test_run_importacao_uses_single_transaction(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Importacao usa --single-transaction para atomicidade (fail-fast)."""
    dump = tmp_path / "export_local.dump"
    dump.write_bytes(b"PGDMP")
    captured_cmd: list[list[str]] = []

    def capture_run(cmd: list[str], *a: object, **k: object) -> MagicMock:
        captured_cmd.append(list(cmd))
        return MagicMock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", capture_run)

    recarga_migracao.run_importacao(
        pg_restore_path="/usr/bin/pg_restore",
        supabase_url="postgresql://u:p@h:5432/db",
        export_path=dump,
    )

    assert len(captured_cmd) == 1
    cmd = captured_cmd[0]
    assert "--single-transaction" in cmd


def test_run_importacao_raises_on_nonzero_return(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Importacao interrompe imediatamente quando pg_restore retorna nao zero."""
    dump = tmp_path / "export_local.dump"
    dump.write_bytes(b"PGDMP")

    def mock_run(cmd: list[str], *a: object, **k: object) -> MagicMock:
        return MagicMock(returncode=1, stdout="", stderr="ERROR: constraint violation")

    monkeypatch.setattr("subprocess.run", mock_run)

    with pytest.raises(SystemExit, match="Importacao falhou|stderr"):
        recarga_migracao.run_importacao(
            pg_restore_path="/usr/bin/pg_restore",
            supabase_url="postgresql://u:p@h:5432/db",
            export_path=dump,
        )


# --- T3: Prontidao de runtime ---


def test_run_consolidacao_blocks_when_database_url_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Consolidacao bloqueia quando DATABASE_URL nao configurada."""
    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "DIRECT_URL":
            return "postgresql://u:p@db.supabase.co:5432/db"
        return "" if k == "DATABASE_URL" else d

    monkeypatch.setattr("os.getenv", getenv)

    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__ = lambda self: mock_conn
    mock_engine.connect.return_value.__exit__ = lambda *a: None
    monkeypatch.setattr(recarga_migracao, "create_engine", lambda url: mock_engine)

    with pytest.raises(SystemExit, match="DATABASE_URL nao configurada"):
        recarga_migracao.run_consolidacao(
            supabase_url="postgresql://u:p@db.supabase.co:5432/db",
            backup_path=tmp_path / "backup.dump",
            export_path=tmp_path / "export.dump",
        )


def test_run_consolidacao_blocks_when_database_url_points_to_local(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Consolidacao bloqueia quando DATABASE_URL aponta para PostgreSQL local."""
    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "DATABASE_URL":
            return "postgresql://u:p@127.0.0.1:5432/npbb"
        return "postgresql://u:p@db.supabase.co:5432/db" if k == "DIRECT_URL" else d

    monkeypatch.setattr("os.getenv", getenv)

    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__ = lambda self: mock_conn
    mock_engine.connect.return_value.__exit__ = lambda *a: None
    monkeypatch.setattr(recarga_migracao, "create_engine", lambda url: mock_engine)

    with pytest.raises(SystemExit, match="127.0.0.1|localhost"):
        recarga_migracao.run_consolidacao(
            supabase_url="postgresql://u:p@db.supabase.co:5432/db",
            backup_path=tmp_path / "backup.dump",
            export_path=tmp_path / "export.dump",
        )


def test_run_consolidacao_succeeds_when_database_url_apt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Consolidacao libera quando DATABASE_URL apta para Supabase."""
    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "DATABASE_URL":
            return "postgresql://u:p@aws-0-xx.supabase.co:6543/postgres"
        return "postgresql://u:p@db.supabase.co:5432/db" if k == "DIRECT_URL" else d

    monkeypatch.setattr("os.getenv", getenv)

    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__ = lambda self: mock_conn
    mock_engine.connect.return_value.__exit__ = lambda *a: None
    monkeypatch.setattr(recarga_migracao, "create_engine", lambda url: mock_engine)

    recarga_migracao.run_consolidacao(
        supabase_url="postgresql://u:p@db.supabase.co:5432/db",
        backup_path=tmp_path / "backup.dump",
        export_path=tmp_path / "export.dump",
    )

    out = capsys.readouterr().out
    assert "Ambiente pronto para validacao pos-carga (ISSUE-F2-02-002)" in out
    assert "DATABASE_URL" in out or "runtime" in out
