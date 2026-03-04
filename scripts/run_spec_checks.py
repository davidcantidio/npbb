"""Run local DOCX-as-spec checks end-to-end.

This script executes:
1. `spec:extract`
2. `spec:render-mapping`
3. `spec:gate`

Optionally, it updates snapshot golden files when `--update-snapshots` is
explicitly provided.
"""

from __future__ import annotations

import argparse
import subprocess
import shutil
import sys
from pathlib import Path

from etl.cli_spec import main as spec_cli_main


def _run_cli(args: list[str]) -> int:
    """Run CLI command and return its exit code."""
    return int(spec_cli_main(args))


def main(argv: list[str] | None = None) -> int:
    """Entrypoint for local spec checks runner.

    Args:
        argv: Optional CLI argument list.

    Returns:
        Exit code where non-zero means one of the checks failed.

    Raises:
        FileNotFoundError: If required DOCX or mapping files do not exist.
    """
    parser = argparse.ArgumentParser(prog="run_spec_checks")
    parser.add_argument(
        "--docx",
        default="tests/fixtures/docx/min_template.docx",
        help="Path to DOCX template to validate.",
    )
    parser.add_argument(
        "--mapping",
        default="tests/fixtures/spec/mapping_min.yml",
        help="Path to mapping YAML used by gate/render.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/analises/eventos/tamo_junto_2025/planning",
        help="Directory for generated artifacts.",
    )
    parser.add_argument(
        "--golden-dir",
        default="tests/golden/spec",
        help="Directory containing golden snapshot markdown files.",
    )
    parser.add_argument(
        "--required-section",
        action="append",
        default=None,
        help="Required section title for gate (repeatable).",
    )
    parser.add_argument(
        "--default-schema",
        default="public",
        help="Default schema used when mapping contains table.field references.",
    )
    parser.add_argument(
        "--update-snapshots",
        action="store_true",
        help="Update golden markdown snapshots after running extract/render.",
    )
    parser.add_argument(
        "--skip-lead-etl-contract",
        action="store_true",
        help="Skip canonical lead ETL contract gate check.",
    )

    args = parser.parse_args(argv)
    docx_path = Path(args.docx)
    mapping_path = Path(args.mapping)
    out_dir = Path(args.out_dir)
    golden_dir = Path(args.golden_dir)
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX not found: {docx_path}")
    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping YAML not found: {mapping_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    checklist_out = out_dir / "00_docx_as_spec.md"
    mapping_out = out_dir / "03_requirements_to_schema_mapping.md"

    rc_extract = _run_cli(
        [
            "spec:extract",
            "--docx",
            str(docx_path),
            "--out",
            str(checklist_out),
            "--format",
            "md",
        ]
    )
    if rc_extract != 0:
        return rc_extract

    rc_render = _run_cli(
        [
            "spec:render-mapping",
            "--docx",
            str(docx_path),
            "--mapping",
            str(mapping_path),
            "--out",
            str(mapping_out),
            "--default-schema",
            args.default_schema,
        ]
    )
    if rc_render != 0:
        return rc_render

    if args.update_snapshots:
        golden_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checklist_out, golden_dir / "00_docx_as_spec.md")
        shutil.copyfile(mapping_out, golden_dir / "03_requirements_to_schema_mapping.md")
        print(f"Snapshots atualizados em: {golden_dir}")

    gate_cmd = [
        "spec:gate",
        "--docx",
        str(docx_path),
        "--mapping",
        str(mapping_path),
        "--default-schema",
        args.default_schema,
    ]
    if args.required_section:
        for section in args.required_section:
            gate_cmd.extend(["--required-section", section])

    rc_gate = _run_cli(gate_cmd)
    if rc_gate != 0:
        return rc_gate

    if args.skip_lead_etl_contract:
        return 0

    contract_gate = Path(__file__).resolve().parent / "check_lead_etl_contracts.py"
    return int(subprocess.call([sys.executable, str(contract_gate)]))


if __name__ == "__main__":
    raise SystemExit(main())
