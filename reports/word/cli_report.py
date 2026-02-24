"""CLI for Word report generation.

Examples (PowerShell):
  python -m reports.word.cli_report report:render --event-id 123 --template-path reports/Festival_TMJ_2025_relatorio.docx --output-path reports/tmj2025/Fechamento_TMJB2025_auto.docx
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Mapping

from etl.transform.agenda_loader import DEFAULT_AGENDA_MASTER_PATH, load_agenda_master
from etl.validate.cli_dq import run_dq_checks, run_show_coverage_report
from etl.validate.coverage_contract import DEFAULT_COVERAGE_CONTRACT_PATH
from etl.validate.framework import parse_fail_on
from .gate_policy import (
    evaluate_report_gate,
    load_report_gate_policy,
    merge_show_coverage_gaps,
)
from .placeholders_mapping import load_placeholders_mapping
from .render_gaps import load_dq_report
from .render_show_coverage import SHOW_COVERAGE_PLACEHOLDER_ID
from .renderer import WordReportRenderer
from .template_validate import find_placeholders, validate_template_placeholders


def _build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for report scaffold commands.

    Returns:
        Configured argument parser with `report:render` command.
    """

    parser = argparse.ArgumentParser(prog="npbb-report")
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser(
        "report:render",
        help="Render DOCX from template with placeholder validation.",
    )
    render.add_argument(
        "--event-id",
        type=int,
        required=True,
        help="Target event identifier.",
    )
    render.add_argument(
        "--template-path",
        required=True,
        help="Path to source template DOCX.",
    )
    render.add_argument(
        "--output-path",
        required=True,
        help="Path to generated DOCX output.",
    )
    render.add_argument(
        "--placeholders-mapping-path",
        required=False,
        help=(
            "Optional path to placeholders mapping YAML. "
            "Defaults to bundled config."
        ),
    )
    render.add_argument(
        "--text-payload-json",
        required=False,
        help=(
            "Optional JSON file with text payload by placeholder id. "
            "Example: {\"FONTES__SUMMARY__TEXT\": [\"linha 1\", \"linha 2\"]}"
        ),
    )
    render.add_argument(
        "--dq-report-json",
        required=False,
        help=(
            "Optional DQ report JSON path used to render GAP/INCONSISTENTE section."
        ),
    )
    render.add_argument(
        "--coverage-report-json",
        required=False,
        help=(
            "Optional show coverage JSON path used to render SHOW__COVERAGE__TABLE."
        ),
    )
    render.add_argument(
        "--gaps-placeholder-id",
        required=False,
        default="GAPS__SUMMARY__TEXT",
        help="Placeholder id used for GAP/INCONSISTENTE section rendering.",
    )
    render.add_argument(
        "--gate-policy-path",
        required=False,
        help=(
            "Optional report gate policy YAML path. "
            "Defaults to bundled reports/word/config/report_gate.yml."
        ),
    )
    render.add_argument(
        "--run-preflight",
        action="store_true",
        help=(
            "Run preflight wiring (dq:run + evaluate_coverage) before report render."
        ),
    )
    render.add_argument(
        "--ingestion-id",
        type=int,
        required=False,
        help="Ingestion run ID used by preflight DQ execution.",
    )
    render.add_argument(
        "--dq-out-json",
        required=False,
        help="Output path for generated preflight DQ JSON report.",
    )
    render.add_argument(
        "--coverage-out-json",
        required=False,
        help="Output path for generated preflight coverage JSON report.",
    )
    render.add_argument(
        "--dq-fail-on",
        choices=("error", "warning", "info", "none"),
        default="error",
        help="Fail threshold used when running preflight dq:run.",
    )
    render.add_argument(
        "--coverage-contract-path",
        required=False,
        help=(
            "Optional coverage contract YAML path. "
            "Defaults to etl/validate/config/coverage_contract.yml."
        ),
    )
    render.add_argument(
        "--agenda-master-path",
        required=False,
        help=(
            "Optional agenda master path used to register agenda version in manifest."
        ),
    )
    return parser


def _load_text_payload(path: Path | None) -> dict[str, object]:
    """Load optional text payload JSON for text placeholders.

    Args:
        path: Optional JSON file path.

    Returns:
        Dictionary payload keyed by placeholder id.

    Raises:
        FileNotFoundError: If payload file does not exist.
        ValueError: If JSON content is invalid or not an object.
    """

    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de payload nao encontrado: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalido em text-payload-json: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("text-payload-json deve conter um objeto JSON (dict).")

    return payload


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    """Load one JSON object from path with actionable validation errors.

    Args:
        path: JSON file path.
        label: Human-readable label used in error messages.

    Returns:
        Parsed JSON object.

    Raises:
        FileNotFoundError: If file path does not exist.
        ValueError: If JSON is invalid or root is not an object.
    """

    if not path.exists():
        raise FileNotFoundError(f"{label} nao encontrado: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalido em {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} deve conter objeto JSON (dict).")
    return dict(payload)


def _default_preflight_artifact_paths(output_path: Path) -> tuple[Path, Path]:
    """Return default preflight artifact paths based on report output path.

    Args:
        output_path: Target DOCX output path.

    Returns:
        Tuple `(dq_report_path, coverage_report_path)`.
    """

    base_dir = output_path.parent
    return (base_dir / "dq_report.json", base_dir / "coverage_report.json")


def _build_show_coverage_table_payload(coverage_report: Mapping[str, Any]) -> dict[str, Any]:
    """Build renderer payload for `SHOW__COVERAGE__TABLE` from coverage report.

    Args:
        coverage_report: Coverage evaluator JSON payload.

    Returns:
        Table payload with `columns` and `rows` keys.

    Raises:
        ValueError: If coverage report has invalid structure.
    """

    sessions = coverage_report.get("sessions")
    if not isinstance(sessions, list):
        raise ValueError(
            "coverage_report.json invalido: campo 'sessions' deve ser lista."
        )

    columns = [
        "dia",
        "sessao",
        "status_access_control",
        "status_optin",
        "status_ticket_sales",
        "observacoes",
    ]

    rows: list[dict[str, Any]] = []
    for session_item in sessions:
        if not isinstance(session_item, Mapping):
            continue
        observed = {
            str(item).strip().lower()
            for item in (session_item.get("observed_datasets") or [])
            if str(item).strip()
        }
        partial = {
            str(item).strip().lower()
            for item in (session_item.get("partial_datasets") or [])
            if str(item).strip()
        }
        missing = {
            str(item).strip().lower()
            for item in (session_item.get("missing_datasets") or [])
            if str(item).strip()
        }

        missing_inputs = session_item.get("missing_inputs")
        observations: list[str] = []
        if isinstance(missing_inputs, list):
            for missing_item in missing_inputs:
                if not isinstance(missing_item, Mapping):
                    continue
                dataset = str(missing_item.get("dataset", "")).strip()
                reason_code = str(missing_item.get("reason_code", "")).strip()
                reason = str(missing_item.get("reason", "")).strip()
                value = ":".join(
                    part for part in (dataset, reason_code or reason) if part
                ).strip(":")
                if value:
                    observations.append(value)

        def dataset_status(dataset_name: str) -> str:
            dataset_key = dataset_name.strip().lower()
            if dataset_key in missing:
                return "gap"
            if dataset_key in partial:
                return "partial"
            if dataset_key in observed:
                return "ok"
            return "gap"

        session_key = str(session_item.get("session_key", "")).strip()
        session_date = str(session_item.get("session_date", "")).strip()
        rows.append(
            {
                "dia": session_date,
                "sessao": session_key or str(session_item.get("session_id", "")),
                "status_access_control": dataset_status("access_control"),
                "status_optin": dataset_status("optin"),
                "status_ticket_sales": dataset_status("ticket_sales"),
                "observacoes": "; ".join(observations),
            }
        )

    rows.sort(key=lambda item: (str(item.get("dia", "")), str(item.get("sessao", ""))))
    return {"columns": columns, "rows": rows}


def _load_agenda_metadata(agenda_path: Path | None) -> dict[str, Any]:
    """Load agenda metadata for report manifest governance block.

    Args:
        agenda_path: Optional path to agenda master YAML/CSV.

    Returns:
        Dictionary with agenda version and source path.

    Raises:
        FileNotFoundError: If provided agenda path does not exist.
        ValueError: If agenda content is invalid.
    """

    resolved_path = agenda_path if agenda_path is not None else DEFAULT_AGENDA_MASTER_PATH
    agenda = load_agenda_master(resolved_path)
    return {
        "agenda_version": int(agenda.version),
        "agenda_source_path": str(agenda.source_path),
    }


def main(argv: list[str] | None = None) -> int:
    """Run CLI command `report:render`.

    Args:
        argv: Optional argument vector.

    Returns:
        Exit code (`0` on success, `1` on expected execution errors).
    """

    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.command != "report:render":
        parser.error(f"Unknown command: {args.command}")
        return 2

    try:
        mapping_path = (
            Path(args.placeholders_mapping_path)
            if args.placeholders_mapping_path
            else None
        )
        mapping = load_placeholders_mapping(mapping_path) if mapping_path else load_placeholders_mapping()

        template_placeholders = find_placeholders(Path(args.template_path))
        pre_findings = validate_template_placeholders(template_placeholders, mapping)
        if pre_findings:
            print("[ERROR] Template contem placeholders sem mapping:")
            for finding in pre_findings:
                print(f"- {finding.placeholder_id} | {finding.code} | {finding.message}")
            return 1

        text_payload_path = Path(args.text_payload_json) if args.text_payload_json else None
        text_payload = _load_text_payload(text_payload_path)
        table_payload: dict[str, Any] = {}
        coverage_governance: dict[str, Any] = {}
        gate_status_note: str | None = None
        dq_report: Mapping[str, Any] | None = None
        coverage_report: Mapping[str, Any] | None = None
        coverage_contract_path = (
            Path(args.coverage_contract_path)
            if args.coverage_contract_path
            else None
        )
        agenda_master_path = Path(args.agenda_master_path) if args.agenda_master_path else None

        if bool(args.run_preflight):
            if args.ingestion_id is None or int(args.ingestion_id) <= 0:
                raise ValueError(
                    "--run-preflight exige --ingestion-id inteiro positivo."
                )
            output_path = Path(args.output_path)
            default_dq_out, default_coverage_out = _default_preflight_artifact_paths(output_path)
            dq_out_path = Path(args.dq_out_json) if args.dq_out_json else default_dq_out
            coverage_out_path = (
                Path(args.coverage_out_json) if args.coverage_out_json else default_coverage_out
            )
            dq_exit_code = run_dq_checks(
                ingestion_id=int(args.ingestion_id),
                event_id=int(args.event_id),
                out_json=dq_out_path,
                fail_on=parse_fail_on(args.dq_fail_on),
            )
            dq_report = load_dq_report(dq_out_path)
            coverage_report = run_show_coverage_report(
                event_id=int(args.event_id),
                out_json=coverage_out_path,
                contract_path=(
                    coverage_contract_path
                    if coverage_contract_path is not None
                    else DEFAULT_COVERAGE_CONTRACT_PATH
                ),
            )
            print(
                "[INFO] Preflight concluido | "
                f"dq_exit_code={dq_exit_code} | "
                f"dq_report={dq_out_path} | "
                f"coverage_report={coverage_out_path}"
            )
            coverage_governance.update(
                {
                    "dq_report_path": str(dq_out_path),
                    "coverage_report_path": str(coverage_out_path),
                }
            )
        else:
            dq_report = load_dq_report(args.dq_report_json) if args.dq_report_json else None
            coverage_report = (
                _load_json_object(Path(args.coverage_report_json), label="coverage_report.json")
                if args.coverage_report_json
                else None
            )

        if coverage_report is not None:
            contract_version = coverage_report.get("contract_version")
            try:
                coverage_governance["coverage_contract_version"] = int(contract_version)
            except (TypeError, ValueError):
                coverage_governance["coverage_contract_version"] = None
            coverage_governance["coverage_contract_path"] = str(
                coverage_contract_path
                if coverage_contract_path is not None
                else DEFAULT_COVERAGE_CONTRACT_PATH
            )
            if "generated_at" in coverage_report:
                coverage_governance["coverage_generated_at"] = str(
                    coverage_report.get("generated_at")
                )
            if SHOW_COVERAGE_PLACEHOLDER_ID in template_placeholders:
                table_payload[SHOW_COVERAGE_PLACEHOLDER_ID] = _build_show_coverage_table_payload(
                    coverage_report
                )

        if bool(args.run_preflight) or agenda_master_path is not None:
            coverage_governance.update(_load_agenda_metadata(agenda_master_path))

        if dq_report is not None or coverage_report is not None:
            gate_policy = (
                load_report_gate_policy(args.gate_policy_path)
                if args.gate_policy_path
                else load_report_gate_policy()
            )
            dq_report_for_gate = merge_show_coverage_gaps(
                dq_report,
                coverage_report=coverage_report,
                policy=gate_policy,
            )
            decision = evaluate_report_gate(
                dq_report_for_gate,
                gate_policy,
                coverage_report=coverage_report,
                template_placeholders=sorted(template_placeholders),
            )
            if decision.status == "block":
                print(f"[ERROR] Gate de publicacao bloqueou o relatorio: {decision.reason}")
                for blocker in decision.blockers:
                    print(f"- bloqueio: {blocker}")
                return 1
            if decision.status == "partial":
                gate_status_note = decision.status_note or "PARCIAL"
                print(f"[WARN] Gate em modo parcial: {decision.reason}")
                for finding in decision.partial_findings[:5]:
                    print(f"- parcial: {finding}")
            dq_report = dq_report_for_gate

        renderer = WordReportRenderer(
            event_id=int(args.event_id),
            template_path=Path(args.template_path),
            output_path=Path(args.output_path),
            placeholders_mapping_path=mapping_path,
            text_payload_by_placeholder=text_payload,
            table_payload_by_placeholder=table_payload,
            dq_report=dq_report,
            gaps_placeholder_id=str(args.gaps_placeholder_id),
            report_status_note=gate_status_note,
            coverage_governance=coverage_governance,
        )
        result = renderer.render()

        unresolved = find_placeholders(result.output_path)
        if unresolved:
            unresolved_list = ", ".join(sorted(unresolved))
            print(
                "[ERROR] DOCX gerado com placeholders nao resolvidos: "
                f"{unresolved_list}. "
                "Como corrigir: preencher payload de texto e/ou implementar render "
                "para o render_type correspondente."
            )
            return 1
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(
        "[OK] report:render concluido | "
        f"event_id={result.event_id} | "
        f"template={result.template_path} | "
        f"output={result.output_path} | "
        f"manifest={result.manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
