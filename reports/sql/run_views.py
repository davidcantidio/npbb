"""Apply and validate `mart_report_*` SQL views from local contracts.

This runner provides an offline workflow for dev/test:
1. apply SQL scripts under `reports/sql/marts/`;
2. validate resulting view columns/types against `contracts.yml`.

Current implementation supports SQLite URLs (`sqlite:///...`) to keep local
validation deterministic and dependency-light.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3
from typing import Iterable, Mapping

import yaml


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TYPE_STRIP_RE = re.compile(r"\(.*\)")
_TYPE_ALIASES: dict[str, set[str]] = {
    "text": {"text", "varchar", "char", "nvarchar"},
    "integer": {"integer", "int", "bigint", "smallint"},
    "real": {"real", "float", "double", "double precision"},
    "numeric": {"numeric", "decimal"},
    "boolean": {"boolean", "bool"},
}


@dataclass(frozen=True)
class ColumnContract:
    """One expected output column for a mart view.

    Args:
        name: Output column name.
        dtype: Expected SQL type declared in contract.
    """

    name: str
    dtype: str


@dataclass(frozen=True)
class ViewContract:
    """Contract describing one mart view output schema.

    Args:
        name: View name, expected to start with `mart_report_`.
        columns: Ordered output columns and types.
        description: Optional human-readable note.
    """

    name: str
    columns: tuple[ColumnContract, ...]
    description: str | None = None


@dataclass(frozen=True)
class ValidationFinding:
    """Validation finding emitted while checking one view contract."""

    view_name: str
    code: str
    message: str


@dataclass(frozen=True)
class RunSummary:
    """Summary of one view runner execution."""

    applied_files: tuple[str, ...]
    validated_views: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]


class ViewRunnerError(ValueError):
    """Raised when runner inputs are invalid or unsupported."""


def _ensure_identifier(name: str, *, field_name: str) -> str:
    """Validate SQL identifier used by contracts and PRAGMA queries.

    Args:
        name: Candidate SQL identifier.
        field_name: Source field used for actionable error messages.

    Returns:
        Stripped identifier.

    Raises:
        ViewRunnerError: If identifier is empty or unsafe.
    """

    clean = str(name or "").strip()
    if not clean:
        raise ViewRunnerError(f"{field_name} obrigatorio no contrato.")
    if not _IDENTIFIER_RE.match(clean):
        raise ViewRunnerError(
            f"{field_name} invalido: {clean!r}. Como corrigir: usar apenas [A-Za-z0-9_]."
        )
    return clean


def _normalize_type(value: str) -> str:
    """Normalize SQL type strings for compatibility checks."""

    clean = _TYPE_STRIP_RE.sub("", str(value or "").strip().casefold())
    return " ".join(clean.split())


def _is_type_compatible(expected: str, actual: str) -> bool:
    """Return whether actual SQL type is compatible with expected type."""

    expected_norm = _normalize_type(expected)
    actual_norm = _normalize_type(actual)
    if expected_norm == actual_norm:
        return True
    expected_aliases = _TYPE_ALIASES.get(expected_norm)
    if expected_aliases is None:
        return False
    return actual_norm in expected_aliases


def load_view_contracts(path: Path | str) -> dict[str, ViewContract]:
    """Load contracts YAML for mart views.

    Args:
        path: YAML file path containing `views` contracts.

    Returns:
        Mapping of `view_name -> ViewContract`.

    Raises:
        ViewRunnerError: If contract format is invalid.
    """

    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, Mapping):
        raise ViewRunnerError("Arquivo de contratos deve ser objeto YAML.")

    views = raw.get("views")
    if not isinstance(views, list) or not views:
        raise ViewRunnerError("Campo 'views' obrigatorio e deve conter lista nao vazia.")

    contracts: dict[str, ViewContract] = {}
    for idx, item in enumerate(views):
        row_path = f"views[{idx}]"
        if not isinstance(item, Mapping):
            raise ViewRunnerError(f"{row_path} deve ser objeto.")

        name = _ensure_identifier(str(item.get("name", "")), field_name=f"{row_path}.name")
        if not name.startswith("mart_report_"):
            raise ViewRunnerError(
                f"{row_path}.name invalido: {name!r}. Como corrigir: prefixar com 'mart_report_'."
            )

        cols = item.get("columns")
        if not isinstance(cols, list) or not cols:
            raise ViewRunnerError(f"{row_path}.columns obrigatorio e deve conter lista nao vazia.")

        parsed_columns: list[ColumnContract] = []
        for col_idx, col in enumerate(cols):
            col_path = f"{row_path}.columns[{col_idx}]"
            if not isinstance(col, Mapping):
                raise ViewRunnerError(f"{col_path} deve ser objeto.")
            col_name = _ensure_identifier(str(col.get("name", "")), field_name=f"{col_path}.name")
            col_type = str(col.get("type", "")).strip()
            if not col_type:
                raise ViewRunnerError(f"{col_path}.type obrigatorio.")
            parsed_columns.append(ColumnContract(name=col_name, dtype=col_type))

        contracts[name] = ViewContract(
            name=name,
            columns=tuple(parsed_columns),
            description=str(item.get("description", "")).strip() or None,
        )
    return contracts


def discover_sql_files(sql_dir: Path | str) -> tuple[Path, ...]:
    """Discover SQL files to apply in deterministic order.

    Args:
        sql_dir: Directory containing `.sql` view scripts.

    Returns:
        Sorted tuple of SQL file paths.

    Raises:
        ViewRunnerError: If directory does not exist.
    """

    base_dir = Path(sql_dir)
    if not base_dir.exists():
        raise ViewRunnerError(f"Diretorio SQL nao encontrado: {base_dir}")
    return tuple(sorted(base_dir.glob("*.sql")))


def connect_sqlite(db_url: str) -> sqlite3.Connection:
    """Create SQLite connection from URL.

    Args:
        db_url: Database URL in format `sqlite:///path/to/db.sqlite`.

    Returns:
        Open `sqlite3.Connection`.

    Raises:
        ViewRunnerError: If URL format is unsupported.
    """

    prefix = "sqlite:///"
    if not str(db_url).startswith(prefix):
        raise ViewRunnerError(
            "Apenas SQLite e suportado neste runner. Como corrigir: usar URL sqlite:///... ."
        )

    target = str(db_url)[len(prefix) :]
    if target in {"", ":memory:"}:
        return sqlite3.connect(":memory:")

    db_path = Path(target)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def apply_sql_files(connection: sqlite3.Connection, sql_files: Iterable[Path]) -> tuple[str, ...]:
    """Apply SQL scripts sequentially in one transaction-safe flow.

    Args:
        connection: Open SQLite connection.
        sql_files: SQL scripts to execute.

    Returns:
        Tuple of applied SQL file names.

    Raises:
        ViewRunnerError: If one SQL script fails.
    """

    applied: list[str] = []
    for sql_path in sql_files:
        script = sql_path.read_text(encoding="utf-8")
        try:
            connection.executescript(script)
        except sqlite3.DatabaseError as exc:
            raise ViewRunnerError(
                f"Falha ao aplicar SQL {sql_path.name}. Como corrigir: revisar sintaxe/ordem."
            ) from exc
        applied.append(sql_path.name)
    connection.commit()
    return tuple(applied)


def get_view_columns(connection: sqlite3.Connection, view_name: str) -> tuple[tuple[str, str], ...]:
    """Fetch ordered view columns and types using SQLite PRAGMA.

    Args:
        connection: Open SQLite connection.
        view_name: View name to introspect.

    Returns:
        Ordered tuple `(column_name, column_type)`.
    """

    safe_name = _ensure_identifier(view_name, field_name="view_name")
    rows = connection.execute(f"PRAGMA table_info('{safe_name}')").fetchall()
    return tuple((str(row[1]), str(row[2])) for row in rows)


def validate_view_contracts(
    connection: sqlite3.Connection,
    contracts: Mapping[str, ViewContract],
) -> tuple[ValidationFinding, ...]:
    """Validate actual view outputs against declared contracts.

    Args:
        connection: Open SQLite connection.
        contracts: Expected view contracts.

    Returns:
        Tuple of validation findings. Empty means all contracts passed.
    """

    findings: list[ValidationFinding] = []
    for view_name, contract in contracts.items():
        actual_columns = get_view_columns(connection, view_name)
        if not actual_columns:
            findings.append(
                ValidationFinding(
                    view_name=view_name,
                    code="VIEW_MISSING",
                    message="View nao encontrada no banco apos apply.",
                )
            )
            continue

        expected_names = [col.name for col in contract.columns]
        actual_names = [name for name, _ in actual_columns]
        if expected_names != actual_names:
            findings.append(
                ValidationFinding(
                    view_name=view_name,
                    code="VIEW_COLUMNS_MISMATCH",
                    message=f"Colunas esperadas={expected_names} atuais={actual_names}.",
                )
            )
            continue

        for column_contract, (_, actual_type) in zip(contract.columns, actual_columns, strict=True):
            if _is_type_compatible(column_contract.dtype, actual_type):
                continue
            findings.append(
                ValidationFinding(
                    view_name=view_name,
                    code="VIEW_COLUMN_TYPE_MISMATCH",
                    message=(
                        f"Coluna {column_contract.name} esperada tipo={column_contract.dtype} "
                        f"atual tipo={actual_type!r}."
                    ),
                )
            )
    return tuple(findings)


def run_view_pipeline(
    *,
    db_url: str,
    sql_dir: Path | str = Path("reports/sql/marts"),
    contracts_path: Path | str = Path("reports/sql/marts/contracts.yml"),
    validate_only: bool = False,
    selected_views: tuple[str, ...] | None = None,
) -> RunSummary:
    """Apply and validate mart views according to local contracts.

    Args:
        db_url: Target SQLite URL (`sqlite:///...`).
        sql_dir: Directory containing SQL files.
        contracts_path: Contracts YAML path.
        validate_only: Skip SQL apply phase when `True`.
        selected_views: Optional subset of view names to validate.

    Returns:
        `RunSummary` with applied files, validated views, and findings.

    Raises:
        ViewRunnerError: If selected view is absent from contracts.
    """

    contracts = load_view_contracts(contracts_path)
    if selected_views:
        requested = {_ensure_identifier(name, field_name="selected_views") for name in selected_views}
        missing = sorted(name for name in requested if name not in contracts)
        if missing:
            raise ViewRunnerError(
                "View(s) sem contrato: "
                + ", ".join(missing)
                + ". Como corrigir: adicionar em contracts.yml."
            )
        contracts = {name: contracts[name] for name in sorted(requested)}

    sql_files = discover_sql_files(sql_dir)
    with connect_sqlite(db_url) as connection:
        applied_files: tuple[str, ...] = ()
        if not validate_only:
            applied_files = apply_sql_files(connection, sql_files)
        findings = validate_view_contracts(connection, contracts)

    return RunSummary(
        applied_files=applied_files,
        validated_views=tuple(contracts.keys()),
        findings=findings,
    )


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for view apply/validate runner."""

    parser = argparse.ArgumentParser(prog="run_views")
    parser.add_argument(
        "--db-url",
        default="sqlite:///reports/tmj2025/tmj_marts_dev.db",
        help="SQLite URL alvo para aplicar/validar views.",
    )
    parser.add_argument(
        "--sql-dir",
        default="reports/sql/marts",
        help="Diretorio com scripts SQL de views.",
    )
    parser.add_argument(
        "--contracts",
        default="reports/sql/marts/contracts.yml",
        help="Arquivo YAML com contrato de colunas por view.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Apenas valida contratos sem aplicar SQL.",
    )
    parser.add_argument(
        "--view",
        action="append",
        default=None,
        help="Nome de view especifica para validar (repetivel).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for mart SQL runner.

    Args:
        argv: Optional argument list.

    Returns:
        Exit code (`0` success, `1` when findings/errors exist).
    """

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_view_pipeline(
            db_url=str(args.db_url),
            sql_dir=Path(args.sql_dir),
            contracts_path=Path(args.contracts),
            validate_only=bool(args.validate_only),
            selected_views=tuple(args.view) if args.view else None,
        )
    except ViewRunnerError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if summary.applied_files:
        print("SQL aplicado:")
        for file_name in summary.applied_files:
            print(f"- {file_name}")

    print("Views validadas:")
    for view_name in summary.validated_views:
        print(f"- {view_name}")

    if summary.findings:
        print("Findings:")
        for finding in summary.findings:
            print(f"- [{finding.code}] {finding.view_name}: {finding.message}")
        return 1

    print("Validacao concluida sem findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
