"""Testes para scripts de migracao F2.

Cobre contrato do artefato, atomicidade do pg_restore, prontidao de runtime na
consolidacao e o checklist final de validacao pos-carga. Usa mocks; nao requer
credenciais reais.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts import (
    backup_export_migracao,
    migracao_common,
    recarga_migracao,
    validacao_pos_carga_migracao,
)


def _configure_mock_engine(monkeypatch: pytest.MonkeyPatch, module: object) -> None:
    """Substitui create_engine por um mock com SELECT 1 funcional."""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__ = lambda self: mock_conn
    mock_engine.connect.return_value.__exit__ = lambda *a: None
    monkeypatch.setattr(module, "create_engine", lambda url: mock_engine)


def _configure_validator_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    direct_url: str = "postgresql://u:p@aws-0-xx.supabase.co:5432/postgres",
    runtime_url: str = "postgresql://u:p@aws-0-xx-pooler.supabase.co:6543/postgres",
) -> tuple[Path, Path]:
    """Monta um caminho feliz da validacao pos-carga usando apenas mocks."""
    backup = tmp_path / "backup_supabase.dump"
    export = tmp_path / "export_local.dump"
    backup.write_bytes(b"PGDMP")
    export.write_bytes(b"PGDMP")

    monkeypatch.setattr(validacao_pos_carga_migracao, "load_backend_env", lambda: None)
    monkeypatch.setattr(validacao_pos_carga_migracao, "check_binary", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(validacao_pos_carga_migracao, "_validate_pg_restore_help", lambda path: None)

    def get_env_value(names: tuple[str, ...], error_message: str) -> str:
        if "DATABASE_URL" in names:
            return runtime_url
        return direct_url

    def require_latest_artifact(prefix: str, guidance: str) -> Path:
        return backup if prefix == "backup_supabase" else export

    monkeypatch.setattr(validacao_pos_carga_migracao, "get_env_value", get_env_value)
    monkeypatch.setattr(validacao_pos_carga_migracao, "require_latest_artifact", require_latest_artifact)
    monkeypatch.setattr(
        validacao_pos_carga_migracao,
        "validate_dump_with_pg_restore",
        lambda pg_restore, path, label: "ok",
    )
    monkeypatch.setattr(validacao_pos_carga_migracao, "_validate_connectivity", lambda direct, runtime: None)
    monkeypatch.setattr(
        validacao_pos_carga_migracao,
        "_collect_public_snapshot",
        lambda url, selected_tables=None: (
            ["eventos", "users"],
            {"users": 12} if selected_tables else {"eventos": 1, "users": 12},
        ),
    )
    monkeypatch.setattr(
        validacao_pos_carga_migracao,
        "list_public_table_data_entries",
        lambda pg_restore, path: ["users"],
    )
    return backup, export


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
    assert "--exclude-table-data=public.alembic_version" in captured_cmd[0]


def test_validate_export_contract_blocks_when_dump_contains_alembic_version(
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
        migracao_common.validate_export_contract("/usr/bin/pg_restore", dump)


def test_validate_export_contract_passes_when_dump_excludes_alembic_version(
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

    migracao_common.validate_export_contract("/usr/bin/pg_restore", dump)


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
    assert "--single-transaction" in captured_cmd[0]


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


# --- T3: Prontidao de runtime na consolidacao ---


def test_run_consolidacao_blocks_when_database_url_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Consolidacao bloqueia quando DATABASE_URL nao configurada."""

    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "DIRECT_URL":
            return "postgresql://u:p@db.supabase.co:5432/db"
        return "" if k == "DATABASE_URL" else d

    monkeypatch.setattr("os.getenv", getenv)
    _configure_mock_engine(monkeypatch, recarga_migracao)

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
    _configure_mock_engine(monkeypatch, recarga_migracao)

    with pytest.raises(SystemExit, match="127.0.0.1|localhost"):
        recarga_migracao.run_consolidacao(
            supabase_url="postgresql://u:p@db.supabase.co:5432/db",
            backup_path=tmp_path / "backup.dump",
            export_path=tmp_path / "export.dump",
        )


def test_run_consolidacao_blocks_when_database_url_remote_divergent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Consolidacao bloqueia quando DATABASE_URL remota esta divergente do alvo."""

    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "DATABASE_URL":
            return "postgresql://u:p@db.example.com:5432/otherdb"
        return "postgresql://u:p@db.supabase.co:5432/postgres" if k == "DIRECT_URL" else d

    monkeypatch.setattr("os.getenv", getenv)
    _configure_mock_engine(monkeypatch, recarga_migracao)

    with pytest.raises(SystemExit, match="alvo|diferente|divergente"):
        recarga_migracao.run_consolidacao(
            supabase_url="postgresql://u:p@db.supabase.co:5432/postgres",
            backup_path=tmp_path / "backup.dump",
            export_path=tmp_path / "export.dump",
        )


def test_run_consolidacao_succeeds_when_database_url_apt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Consolidacao libera quando DATABASE_URL alinhada ao mesmo Supabase alvo da recarga."""

    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "DATABASE_URL":
            return "postgresql://u:p@aws-0-xx-pooler.supabase.co:6543/postgres"
        return "postgresql://u:p@aws-0-xx.supabase.co:5432/postgres" if k == "DIRECT_URL" else d

    monkeypatch.setattr("os.getenv", getenv)
    _configure_mock_engine(monkeypatch, recarga_migracao)

    recarga_migracao.run_consolidacao(
        supabase_url="postgresql://u:p@aws-0-xx.supabase.co:5432/postgres",
        backup_path=tmp_path / "backup.dump",
        export_path=tmp_path / "export.dump",
    )

    out = capsys.readouterr().out
    assert "Ambiente pronto para validacao pos-carga (ISSUE-F2-02-002)" in out
    assert "python -m scripts.validacao_pos_carga_migracao" in out


# --- T4: Validacao pos-carga e rollback ---


def test_run_validacao_pos_carga_blocks_when_artifact_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Validador falha cedo quando backup/export nao existem."""
    backup, _ = _configure_validator_success(monkeypatch, tmp_path)

    def require_latest_artifact(prefix: str, guidance: str) -> Path:
        if prefix == "backup_supabase":
            return backup
        raise SystemExit("ERRO: Artefato export_local nao encontrado.")

    monkeypatch.setattr(validacao_pos_carga_migracao, "require_latest_artifact", require_latest_artifact)

    with pytest.raises(SystemExit, match="export_local nao encontrado"):
        validacao_pos_carga_migracao.run_validacao_pos_carga()


def test_run_validacao_pos_carga_blocks_when_backup_unreadable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Validador bloqueia quando o backup preservado nao pode ser inspecionado."""
    _configure_validator_success(monkeypatch, tmp_path)

    def validate_dump(pg_restore: str, path: Path, label: str) -> str:
        if label == "backup do Supabase":
            raise SystemExit("ERRO: backup do Supabase ilegivel")
        return "ok"

    monkeypatch.setattr(validacao_pos_carga_migracao, "validate_dump_with_pg_restore", validate_dump)

    with pytest.raises(SystemExit, match="backup do Supabase ilegivel"):
        validacao_pos_carga_migracao.run_validacao_pos_carga()


def test_run_validacao_pos_carga_blocks_when_runtime_target_divergent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Validador bloqueia quando runtime e manutencao apontam para alvos diferentes."""
    _configure_validator_success(
        monkeypatch,
        tmp_path,
        direct_url="postgresql://u:p@aws-0-xx.supabase.co:5432/postgres",
        runtime_url="postgresql://u:p@db.example.com:5432/otherdb",
    )

    with pytest.raises(SystemExit, match="alvo diferente|mesmo projeto Supabase"):
        validacao_pos_carga_migracao.run_validacao_pos_carga()


def test_validacao_pos_carga_main_prints_checklist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Validador imprime checklist final quando o alvo esta coerente."""
    _configure_validator_success(monkeypatch, tmp_path)

    validacao_pos_carga_migracao.main()

    out = capsys.readouterr().out
    assert "=== Validacao Pos-Carga - Migracao F2 (Supabase) ===" in out
    assert "[x] Backup preservado e legivel:" in out
    assert "[x] DIRECT_URL e DATABASE_URL conectam e apontam para o mesmo Supabase alvo" in out
    assert "Criterios objetivos para rollback:" in out
    assert "Resultado: validacao pos-carga concluida." in out
