"""Testes dedicados para backup_export_migracao (ISSUE-F2-01-003).

Cobre precondicoes, ordem critica (backup -> export -> validacao final) e
bloqueio da mensagem de sucesso quando validacao falha. Usa mocks/doubles;
nao requer conexao real com Supabase ou PostgreSQL.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts import backup_export_migracao


def test_validate_preconditions_fails_without_supabase_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha antecipada quando SUPABASE_DIRECT_URL e DIRECT_URL nao configurados."""
    monkeypatch.setattr(backup_export_migracao, "_load_env", lambda: None)
    monkeypatch.setattr("os.getenv", lambda k, d=None: "" if k in ("SUPABASE_DIRECT_URL", "DIRECT_URL") else d)

    with pytest.raises(SystemExit):
        backup_export_migracao._validate_preconditions()


def test_validate_preconditions_fails_without_local_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha antecipada quando LOCAL_DIRECT_URL nao configurado."""
    monkeypatch.setattr(backup_export_migracao, "_load_env", lambda: None)

    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "SUPABASE_DIRECT_URL":
            return "postgresql://u:p@h:5432/db"
        if k == "LOCAL_DIRECT_URL":
            return ""
        return d

    monkeypatch.setattr("os.getenv", getenv)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/pg_dump")

    with pytest.raises(SystemExit):
        backup_export_migracao._validate_preconditions()


def test_validate_preconditions_fails_without_pg_dump(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha antecipada quando pg_dump nao esta no PATH."""
    monkeypatch.setattr(backup_export_migracao, "_load_env", lambda: None)

    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "SUPABASE_DIRECT_URL":
            return "postgresql://u:p@h:5432/db"
        if k == "LOCAL_DIRECT_URL":
            return "postgresql://u:p@127.0.0.1:5432/npbb"
        return d

    def which(cmd: str) -> str | None:
        return None if cmd == "pg_dump" else "/usr/bin/pg_restore"

    monkeypatch.setattr("os.getenv", getenv)
    monkeypatch.setattr("shutil.which", which)

    with pytest.raises(SystemExit):
        backup_export_migracao._validate_preconditions()


def test_validate_preconditions_fails_without_pg_restore(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha antecipada quando pg_restore nao esta no PATH."""
    monkeypatch.setattr(backup_export_migracao, "_load_env", lambda: None)

    def getenv(k: str, d: str | None = None) -> str | None:
        if k == "SUPABASE_DIRECT_URL":
            return "postgresql://u:p@h:5432/db"
        if k == "LOCAL_DIRECT_URL":
            return "postgresql://u:p@127.0.0.1:5432/npbb"
        return d

    def which(cmd: str) -> str | None:
        return None if cmd == "pg_restore" else "/usr/bin/pg_dump"

    monkeypatch.setattr("os.getenv", getenv)
    monkeypatch.setattr("shutil.which", which)

    with pytest.raises(SystemExit):
        backup_export_migracao._validate_preconditions()


def test_validate_dump_fails_for_missing_file() -> None:
    """Validacao falha quando o arquivo nao existe."""
    with pytest.raises(SystemExit, match="artefato nao encontrado"):
        backup_export_migracao._validate_dump("/usr/bin/pg_restore", Path("/nao/existe.dump"))


def test_validate_dump_fails_for_empty_file(tmp_path: Path) -> None:
    """Validacao falha quando o arquivo tem tamanho zero."""
    empty = tmp_path / "vazio.dump"
    empty.touch()
    with pytest.raises(SystemExit, match="artefato vazio"):
        backup_export_migracao._validate_dump("/usr/bin/pg_restore", empty)


def test_validate_dump_fails_for_invalid_dump(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Validacao falha quando pg_restore --list retorna erro (dump ilegivel)."""
    dump = tmp_path / "invalido.dump"
    dump.write_bytes(b"lixo nao e dump")
    mock_run = MagicMock(return_value=MagicMock(returncode=1, stdout="", stderr="invalid format"))
    monkeypatch.setattr("subprocess.run", mock_run)

    with pytest.raises(SystemExit, match="dump invalido ou ilegivel"):
        backup_export_migracao._validate_dump("/usr/bin/pg_restore", dump)


def test_validate_dump_succeeds_for_valid_dump(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Validacao passa quando arquivo existe, tem tamanho > 0 e pg_restore --list OK."""
    dump = tmp_path / "valido.dump"
    dump.write_bytes(b"PGDMP")  # header minimo de dump custom
    monkeypatch.setattr("subprocess.run", lambda *a, **k: MagicMock(returncode=0, stdout="", stderr=""))

    backup_export_migracao._validate_dump("/usr/bin/pg_restore", dump)
    # nao levanta


def test_main_fails_before_success_message_when_validation_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Mensagem de sucesso nao aparece quando validacao falha apos backup e export."""
    monkeypatch.setattr(backup_export_migracao, "_validate_preconditions", lambda: ("/pg_dump", "/pg_restore", "x", "y"))
    monkeypatch.setattr(
        backup_export_migracao,
        "run_backup_supabase",
        lambda *a, **k: Path("/tmp/backup.dump"),
    )
    monkeypatch.setattr(
        backup_export_migracao,
        "run_export_local",
        lambda *a, **k: Path("/tmp/export.dump"),
    )

    def validate_raise(*a: object, **k: object) -> None:
        raise SystemExit("ERRO: dump invalido")

    monkeypatch.setattr(backup_export_migracao, "_validate_dump", validate_raise)
    monkeypatch.setattr(backup_export_migracao, "ARTIFACTS_DIR", Path("/tmp"))

    with pytest.raises(SystemExit):
        backup_export_migracao.main()

    out = capsys.readouterr().out
    assert "Artefatos prontos para a recarga controlada" not in out


def test_main_order_backup_export_validation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ordem do fluxo: backup -> export -> validacao final -> mensagem de sucesso."""
    call_order: list[str] = []
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    backup_file = artifacts_dir / "backup_supabase_20260101_120000.dump"
    export_file = artifacts_dir / "export_local_20260101_120001.dump"
    backup_file.write_bytes(b"PGDMP")
    export_file.write_bytes(b"PGDMP")

    def fake_backup(*a: object, **k: object) -> Path:
        call_order.append("backup")
        return backup_file

    def fake_export(*a: object, **k: object) -> Path:
        call_order.append("export")
        return export_file

    def fake_validate(pg_restore: str, path: Path) -> None:
        call_order.append("validate")
        # nao levanta

    monkeypatch.setattr(backup_export_migracao, "_validate_preconditions", lambda: ("/pg_dump", "/pg_restore", "x", "y"))
    monkeypatch.setattr(backup_export_migracao, "run_backup_supabase", fake_backup)
    monkeypatch.setattr(backup_export_migracao, "run_export_local", fake_export)
    monkeypatch.setattr(backup_export_migracao, "_validate_dump", fake_validate)
    monkeypatch.setattr(backup_export_migracao, "ARTIFACTS_DIR", artifacts_dir)

    backup_export_migracao.main()

    assert call_order == ["backup", "export", "validate", "validate"]
    out = capsys.readouterr().out
    assert "Artefatos prontos para a recarga controlada (ISSUE-F2-02)." in out
