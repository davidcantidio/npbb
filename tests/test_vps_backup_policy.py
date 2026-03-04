from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKUP_SCRIPT = ROOT_DIR / "Infra" / "production" / "backup" / "backup.sh"


def make_fake_pg_dump(bin_dir: Path) -> None:
    script = bin_dir / "pg_dump"
    script.write_text(
        """#!/bin/sh
set -eu

output=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--file" ]; then
    output="$2"
    shift 2
    continue
  fi
  shift
done

printf 'fake dump for %s\\n' "${output}" > "${output}"
""",
        encoding="utf-8",
    )
    script.chmod(0o755)


def build_env(tmp_path: Path, *, timestamp: str, external_dir: Path, force_weekly: bool = False) -> dict[str, str]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    make_fake_pg_dump(fake_bin)

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "PGHOST": "db",
            "PGDATABASE": "npbb",
            "PGUSER": "npbb",
            "PGPASSWORD": "secret",
            "BACKUP_DIR": str(backup_dir),
            "BACKUP_EXTERNAL_DIR": str(external_dir),
            "BACKUP_FILE_PREFIX": "npbb",
            "BACKUP_DAILY_RETENTION": "7",
            "BACKUP_WEEKLY_RETENTION": "4",
            "BACKUP_WEEKLY_DAY": "7",
            "BACKUP_FORCE_WEEKLY": "true" if force_weekly else "false",
            "BACKUP_TIMESTAMP": timestamp,
            "PATH": f"{fake_bin}:{env['PATH']}",
        }
    )
    return env


def run_backup(tmp_path: Path, *, timestamp: str, external_dir: Path, force_weekly: bool = False) -> subprocess.CompletedProcess[str]:
    env = build_env(tmp_path, timestamp=timestamp, external_dir=external_dir, force_weekly=force_weekly)
    return subprocess.run(
        ["/bin/sh", str(BACKUP_SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_backup_generates_checksum_and_external_copy(tmp_path: Path) -> None:
    external_dir = tmp_path / "archive"
    external_dir.mkdir()

    result = run_backup(
        tmp_path,
        timestamp="20260303_010101",
        external_dir=external_dir,
        force_weekly=False,
    )

    assert result.returncode == 0
    assert "starting dump" in result.stdout
    assert "completed file=" in result.stdout

    local_daily = tmp_path / "backups" / "daily"
    external_daily = external_dir / "daily"
    dump = local_daily / "npbb_20260303_010101.dump"
    checksum = local_daily / "npbb_20260303_010101.dump.sha256"

    assert dump.exists()
    assert checksum.exists()
    assert (external_daily / dump.name).exists()
    assert (external_daily / checksum.name).exists()


def test_backup_enforces_daily_and_weekly_retention(tmp_path: Path) -> None:
    external_dir = tmp_path / "archive"
    external_dir.mkdir()

    for index in range(1, 10):
        timestamp = f"20260303_01010{index}"
        result = run_backup(
            tmp_path,
            timestamp=timestamp,
            external_dir=external_dir,
            force_weekly=True,
        )
        assert result.returncode == 0

    local_daily = sorted((tmp_path / "backups" / "daily").glob("*.dump"))
    local_weekly = sorted((tmp_path / "backups" / "weekly").glob("*.dump"))
    external_daily = sorted((external_dir / "daily").glob("*.dump"))
    external_weekly = sorted((external_dir / "weekly").glob("*.dump"))

    assert len(local_daily) == 7
    assert len(local_weekly) == 4
    assert len(external_daily) == 7
    assert len(external_weekly) == 4
    assert local_daily[-1].name == "npbb_20260303_010109.dump"
    assert local_weekly[-1].name == "npbb_20260303_010109.dump"


def test_backup_fails_when_external_directory_is_unavailable(tmp_path: Path) -> None:
    external_dir = tmp_path / "archive-file"
    external_dir.write_text("not a directory", encoding="utf-8")

    result = run_backup(
        tmp_path,
        timestamp="20260303_020202",
        external_dir=external_dir,
        force_weekly=False,
    )

    assert result.returncode != 0
    assert "failed status=" in result.stdout
