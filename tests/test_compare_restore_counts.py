from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT_DIR / "scripts" / "compare_restore_counts.py"


def create_sqlite_db(path: Path, *, lead_count: int, evento_count: int, usuario_count: int) -> None:
    connection = sqlite3.connect(path)
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE lead (id INTEGER PRIMARY KEY)")
        cursor.execute("CREATE TABLE evento (id INTEGER PRIMARY KEY)")
        cursor.execute("CREATE TABLE usuario (id INTEGER PRIMARY KEY)")

        cursor.executemany("INSERT INTO lead DEFAULT VALUES", [()] * lead_count)
        cursor.executemany("INSERT INTO evento DEFAULT VALUES", [()] * evento_count)
        cursor.executemany("INSERT INTO usuario DEFAULT VALUES", [()] * usuario_count)
        connection.commit()
    finally:
        connection.close()


def run_compare(source_db: Path, target_db: Path, output_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--source-url",
            f"sqlite:///{source_db}",
            "--target-url",
            f"sqlite:///{target_db}",
            "--tables",
            "lead",
            "evento",
            "usuario",
            "--output",
            str(output_file),
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )


def test_compare_restore_counts_returns_zero_when_all_tables_match(tmp_path: Path) -> None:
    source_db = tmp_path / "source.db"
    target_db = tmp_path / "target.db"
    output_file = tmp_path / "table-counts.md"

    create_sqlite_db(source_db, lead_count=3, evento_count=2, usuario_count=1)
    create_sqlite_db(target_db, lead_count=3, evento_count=2, usuario_count=1)

    result = run_compare(source_db, target_db, output_file)

    assert result.returncode == 0
    content = output_file.read_text(encoding="utf-8")
    assert "`match`" in content
    assert "Decision: `promote-candidate`" in content


def test_compare_restore_counts_returns_one_when_any_table_mismatches(tmp_path: Path) -> None:
    source_db = tmp_path / "source.db"
    target_db = tmp_path / "target.db"
    output_file = tmp_path / "table-counts.md"

    create_sqlite_db(source_db, lead_count=3, evento_count=2, usuario_count=1)
    create_sqlite_db(target_db, lead_count=4, evento_count=2, usuario_count=1)

    result = run_compare(source_db, target_db, output_file)

    assert result.returncode == 1
    content = output_file.read_text(encoding="utf-8")
    assert "| `lead` | `3` | `4` | `mismatch` |" in content
    assert "Decision: `hold`" in content
