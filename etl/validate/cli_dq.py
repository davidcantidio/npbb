"""CLI for data-quality framework execution (`dq:run`).

Examples (PowerShell):
  python -m etl.validate.cli_dq dq:run --ingestion-id 42 --out-json out/dq.json --out-md out/dq.md
  python -m etl.validate.cli_dq dq:run --ingestion-id 42 --out-json out/dq.json --fail-on warning
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from sqlmodel import Session, select

from .framework import (
    Check,
    CheckContext,
    CheckResult,
    CheckRunner,
    CheckStatus,
    Severity,
    parse_fail_on,
)
from .alerts import alerts_to_dicts, generate_alerts, render_alerts_markdown
from .coverage_matrix import build_coverage_matrix_payload
from .request_list import (
    build_missing_artifacts_list,
    render_missing_artifacts_csv,
    render_missing_artifacts_markdown,
)
from .render_dq_report import render_dq_report, render_dq_report_json
from .show_coverage_evaluator import evaluate_coverage
from .coverage_contract import DEFAULT_COVERAGE_CONTRACT_PATH

try:  # pragma: no cover - import style depends on caller cwd
    from app.db.database import engine
    from app.models.etl_registry import IngestionRun, IngestionStatus
    from app.services.etl_health_queries import (
        list_source_health_status,
        source_health_rows_to_dicts,
        source_health_summary_to_dict,
        summarize_source_health,
    )
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.db.database import engine
    from app.models.etl_registry import IngestionRun, IngestionStatus
    from app.services.etl_health_queries import (
        list_source_health_status,
        source_health_rows_to_dicts,
        source_health_summary_to_dict,
        summarize_source_health,
    )


class IngestionIdPositiveCheck(Check):
    """Validate `ingestion_id` is a positive integer."""

    check_id = "dq.ingestion_id_positive"
    description = "Valida que ingestion_id e inteiro positivo."

    def run(self, context: CheckContext) -> CheckResult:
        """Execute positive-ingestion-id validation.

        Args:
            context: Check execution context.

        Returns:
            Pass/fail result with actionable message.
        """

        ingestion_id = context.ingestion_id
        if ingestion_id is None or ingestion_id <= 0:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message=(
                    "ingestion_id invalido. Como corrigir: informar valor inteiro maior que zero."
                ),
                ingestion_id=ingestion_id,
                evidence={"ingestion_id": ingestion_id},
            )
        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="ingestion_id valido.",
            ingestion_id=ingestion_id,
            evidence={"ingestion_id": ingestion_id},
        )


class IngestionExistsCheck(Check):
    """Validate ingestion run exists in registry table."""

    check_id = "dq.ingestion_exists"
    description = "Valida existencia do run na tabela ingestions."

    def run(self, context: CheckContext) -> CheckResult:
        """Execute ingestion-existence validation against database.

        Args:
            context: Check execution context with DB session resource.

        Returns:
            Pass/fail result and cached run metadata in context.
        """

        session = context.require_resource("session")
        ingestion = session.exec(
            select(IngestionRun).where(IngestionRun.id == context.ingestion_id)
        ).first()
        if ingestion is None:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.FAIL,
                severity=Severity.ERROR,
                message=(
                    "Ingestion run nao encontrado. Como corrigir: validar ID e registro no catalogo."
                ),
                ingestion_id=context.ingestion_id,
                evidence={"table": "ingestions", "ingestion_id": context.ingestion_id},
            )

        context.metadata["ingestion_run"] = ingestion
        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Ingestion run encontrado no catalogo.",
            ingestion_id=context.ingestion_id,
            evidence={
                "source_pk": ingestion.source_pk,
                "status": _status_value(ingestion.status),
                "extractor_name": ingestion.extractor_name,
            },
            lineage={"source_pk": ingestion.source_pk},
        )


class IngestionStatusCheck(Check):
    """Emit operational warning for non-success ingestion status."""

    check_id = "dq.ingestion_status"
    description = "Valida status final da ingestao para uso em gates."

    def run(self, context: CheckContext) -> CheckResult:
        """Check ingestion status and return warning when not successful.

        Args:
            context: Check execution context with cached ingestion run.

        Returns:
            Result classified as pass, fail-warning or skip.
        """

        ingestion = context.metadata.get("ingestion_run")
        if ingestion is None:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.SKIP,
                severity=Severity.INFO,
                message="Check ignorado: ingestion run nao disponivel no contexto.",
                ingestion_id=context.ingestion_id,
                evidence={"reason": "missing_ingestion_run"},
            )

        status_value = _status_value(ingestion.status)
        if status_value == IngestionStatus.SUCCESS.value:
            return CheckResult(
                check_id=self.check_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Status de ingestao indica execucao bem-sucedida.",
                ingestion_id=context.ingestion_id,
                evidence={"status": status_value},
            )

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message=(
                "Status de ingestao nao-sucedido. Como corrigir: revisar notas/erros e rerodar extractor."
            ),
            ingestion_id=context.ingestion_id,
            evidence={
                "status": status_value,
                "notes": ingestion.notes,
                "error_message": ingestion.error_message,
            },
            lineage={"source_pk": ingestion.source_pk},
        )


def _status_value(value: IngestionStatus | str | None) -> str:
    """Normalize ingestion status to lowercase value."""

    if value is None:
        return ""
    if isinstance(value, IngestionStatus):
        return value.value
    return str(value).strip().lower()


def run_dq_checks(
    *,
    ingestion_id: int,
    event_id: int | None = None,
    out_json: Path | None = None,
    out_md: Path | None = None,
    out_request_md: Path | None = None,
    out_request_csv: Path | None = None,
    request_include_partial: bool = False,
    fail_on: Severity | None = Severity.ERROR,
) -> int:
    """Run DQ checks for one ingestion and persist report outputs.

    Args:
        ingestion_id: Ingestion run identifier.
        event_id: Optional event identifier for coverage/request generation.
        out_json: Optional JSON output path.
        out_md: Optional Markdown output path.
        out_request_md: Optional Markdown request-list output path.
        out_request_csv: Optional CSV request-list output path.
        request_include_partial: Include partial coverage findings in request list.
        fail_on: Failure severity threshold (`None` disables gate failure).

    Returns:
        Exit code computed by check runner.

    Raises:
        ValueError: If no output destination is provided.
        OSError: If output write fails.
    """

    if (
        out_json is None
        and out_md is None
        and out_request_md is None
        and out_request_csv is None
    ):
        raise ValueError(
            "Informe ao menos um destino: --out-json, --out-md, --out-request-md ou --out-request-csv."
        )

    checks: tuple[Check, ...] = (
        IngestionIdPositiveCheck(),
        IngestionExistsCheck(),
        IngestionStatusCheck(),
    )

    with Session(engine) as session:
        context = CheckContext(
            ingestion_id=ingestion_id,
            resources={"session": session},
        )
        report = CheckRunner(checks, fail_on=fail_on).run(context)
        health_rows = list_source_health_status(session)
        health_payload = {
            "summary": source_health_summary_to_dict(summarize_source_health(health_rows)),
            "items": source_health_rows_to_dicts(health_rows),
        }
        coverage_payload = build_coverage_matrix_payload(session, event_id=event_id)
        request_items = []
        if out_request_md is not None or out_request_csv is not None:
            coverage_report = evaluate_coverage(session, event_id=event_id)
            request_items = build_missing_artifacts_list(
                coverage_report,
                include_partial=request_include_partial,
            )
        alerts = generate_alerts(health_payload, coverage_payload)

    if out_json is not None:
        json_payload = render_dq_report_json(report, coverage_section=coverage_payload)
        json_payload["alerts"] = alerts_to_dicts(alerts)
        if out_request_md is not None or out_request_csv is not None:
            json_payload["request_list"] = [item.to_dict() for item in request_items]
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(
            json.dumps(
                json_payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if out_md is not None:
        markdown = render_dq_report(report, coverage_section=coverage_payload)
        markdown = markdown.rstrip() + "\n\n" + render_alerts_markdown(alerts)
        if out_request_md is not None or out_request_csv is not None:
            markdown = markdown.rstrip() + "\n\n" + render_missing_artifacts_markdown(
                request_items
            )
        markdown = markdown.rstrip() + "\n"
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(
            markdown,
            encoding="utf-8",
        )
    if out_request_md is not None:
        out_request_md.parent.mkdir(parents=True, exist_ok=True)
        out_request_md.write_text(
            render_missing_artifacts_markdown(request_items),
            encoding="utf-8",
        )
    if out_request_csv is not None:
        out_request_csv.parent.mkdir(parents=True, exist_ok=True)
        out_request_csv.write_text(
            render_missing_artifacts_csv(request_items),
            encoding="utf-8",
        )

    return report.exit_code


def run_show_coverage_report(
    *,
    event_id: int | None,
    out_json: Path,
    contract_path: Path | str = DEFAULT_COVERAGE_CONTRACT_PATH,
) -> dict[str, object]:
    """Evaluate show/session coverage and write JSON report artifact.

    Args:
        event_id: Optional event identifier filter.
        out_json: Output JSON file path for coverage report.
        contract_path: Coverage contract YAML path used by evaluator.

    Returns:
        JSON-friendly coverage report payload.

    Raises:
        FileNotFoundError: If coverage contract path does not exist.
        ValueError: If contract content is invalid.
        OSError: If output file cannot be written.
    """

    with Session(engine) as session:
        payload = evaluate_coverage(
            session,
            event_id=event_id,
            contract_path=contract_path,
        ).to_dict()

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return dict(payload)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for data-quality framework runner."""

    parser = argparse.ArgumentParser(prog="npbb-dq")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("dq:run", help="Run data-quality checks for one ingestion run.")
    run.add_argument("--ingestion-id", type=int, required=True, help="Target ingestion run ID.")
    run.add_argument(
        "--event-id",
        type=int,
        default=None,
        help="Optional event ID used by coverage/request list generation.",
    )
    run.add_argument("--out-json", default=None, help="Optional output JSON report path.")
    run.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    run.add_argument(
        "--out-request-md",
        default=None,
        help="Optional output Markdown path for request list (gaps de show).",
    )
    run.add_argument(
        "--out-request-csv",
        default=None,
        help="Optional output CSV path for request list (gaps de show).",
    )
    run.add_argument(
        "--request-include-partial",
        action="store_true",
        help="Include partial findings in request list in addition to gaps.",
    )
    run.add_argument(
        "--fail-on",
        choices=("error", "warning", "info", "none"),
        default="error",
        help="Fail threshold for exit code.",
    )

    args = parser.parse_args(argv)
    if args.command != "dq:run":
        parser.error(f"Unknown command: {args.command}")
        return 2

    return run_dq_checks(
        ingestion_id=int(args.ingestion_id),
        event_id=int(args.event_id) if args.event_id is not None else None,
        out_json=Path(args.out_json) if args.out_json else None,
        out_md=Path(args.out_md) if args.out_md else None,
        out_request_md=Path(args.out_request_md) if args.out_request_md else None,
        out_request_csv=Path(args.out_request_csv) if args.out_request_csv else None,
        request_include_partial=bool(args.request_include_partial),
        fail_on=parse_fail_on(args.fail_on),
    )


if __name__ == "__main__":
    raise SystemExit(main())
