"""CLI for the DOCX-as-spec workflow.

Examples (PowerShell):
  python -m npbb.etl.cli_spec spec:extract --docx C:\\path\\template.docx --out out.md
  python -m npbb.etl.cli_spec spec:extract --docx C:\\path\\template.docx --out out.json --format json
  python -m npbb.etl.cli_spec spec:render-mapping --docx C:\\path\\template.docx --mapping core\\spec\\mapping_schema.yml --out 03_requirements_to_schema_mapping.md
  python -m npbb.etl.cli_spec spec:diff --old-docx old.docx --new-docx new.docx --out-md spec_diff.md --out-json spec_diff.json
  python -m npbb.etl.cli_spec spec:gate --docx template.docx --mapping core\\spec\\mapping_schema.yml
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:  # pragma: no cover - import style depends on execution context
    from npbb.core.spec.docx_figures_tables import extract_figures_from_docx, extract_tables_from_docx
    from npbb.core.spec.docx_sections import DocxSectionExtractor
    from npbb.core.spec.mapping_loader import load_mapping
    from npbb.core.spec.render_mapping_md import render_mapping_md
    from npbb.core.spec.render_markdown import build_initial_checklist_rows, render_docx_as_spec_md
    from npbb.core.spec.spec_diff import diff_specs, render_diff_json, render_diff_markdown
    from npbb.core.spec.spec_gate import evaluate_spec_gate, render_spec_gate_summary
    from npbb.core.spec.spec_models import DocxSpec
except ModuleNotFoundError:  # local repo execution (cwd at repository root)
    from core.spec.docx_figures_tables import extract_figures_from_docx, extract_tables_from_docx
    from core.spec.docx_sections import DocxSectionExtractor
    from core.spec.mapping_loader import load_mapping
    from core.spec.render_mapping_md import render_mapping_md
    from core.spec.render_markdown import build_initial_checklist_rows, render_docx_as_spec_md
    from core.spec.spec_diff import diff_specs, render_diff_json, render_diff_markdown
    from core.spec.spec_gate import evaluate_spec_gate, render_spec_gate_summary
    from core.spec.spec_models import DocxSpec


def _build_spec(docx_path: Path) -> DocxSpec:
    """Build a DocxSpec from a template DOCX.

    Args:
        docx_path: Path to the template file.

    Returns:
        Extracted DocxSpec including sections, figures and tables.
    """
    extractor = DocxSectionExtractor()
    sections = extractor.extract_sections(docx_path)
    figures = extract_figures_from_docx(docx_path, sections)
    tables = extract_tables_from_docx(docx_path)
    return DocxSpec(
        source_path=str(docx_path),
        extracted_at=datetime.now(timezone.utc),
        sections=sections,
        figures=figures,
        tables=tables,
    )


def _write_spec_output(spec: DocxSpec, out_path: Path, output_format: str) -> None:
    """Write extracted spec to the requested output format.

    Args:
        spec: Extracted DOCX specification.
        out_path: Destination file path.
        output_format: One of `md` or `json`.

    Raises:
        ValueError: If `output_format` is not supported.
        OSError: If writing to disk fails.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        out_path.write_text(json.dumps(spec.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
        return
    if output_format == "md":
        out_path.write_text(render_docx_as_spec_md(spec), encoding="utf-8")
        return
    raise ValueError(f"Unsupported output format: {output_format}")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    ap = argparse.ArgumentParser(prog="npbb-spec")
    sub = ap.add_subparsers(dest="command", required=True)

    ex = sub.add_parser("spec:extract", help="Extract a DOCX template into a spec (md/json).")
    ex.add_argument("--docx", required=True, help="Path to the template .docx")
    ex.add_argument("--out", required=True, help="Output path (.md or .json)")
    ex.add_argument(
        "--format",
        default="md",
        choices=("md", "json"),
        help="Output format: md (planning checklist) or json (raw extracted spec).",
    )
    rm = sub.add_parser(
        "spec:render-mapping",
        help="Render requirements-to-schema mapping markdown from DOCX checklist + mapping YAML.",
    )
    rm.add_argument("--docx", required=True, help="Path to template .docx used to derive checklist.")
    rm.add_argument("--mapping", required=True, help="Path to mapping YAML.")
    rm.add_argument("--out", required=True, help="Output markdown path.")
    rm.add_argument(
        "--default-schema",
        default="public",
        help="Default schema for references in table.field format.",
    )
    df = sub.add_parser("spec:diff", help="Diff two DOCX specs and output markdown + json.")
    df.add_argument("--old-docx", required=True, help="Path to old/base DOCX template.")
    df.add_argument("--new-docx", required=True, help="Path to new/candidate DOCX template.")
    df.add_argument("--out-md", required=True, help="Markdown diff output path.")
    df.add_argument("--out-json", required=True, help="JSON diff output path.")
    gt = sub.add_parser("spec:gate", help="Run spec gate (checks + mapping coverage).")
    gt.add_argument("--docx", required=True, help="Path to DOCX template.")
    gt.add_argument("--mapping", required=True, help="Path to mapping YAML.")
    gt.add_argument(
        "--default-schema",
        default="public",
        help="Default schema for references in table.field format.",
    )
    gt.add_argument(
        "--required-section",
        action="append",
        default=None,
        help="Required section title (repeatable).",
    )

    args = ap.parse_args(argv)

    if args.command == "spec:extract":
        docx_path = Path(args.docx)
        out_path = Path(args.out)
        spec = _build_spec(docx_path)
        _write_spec_output(spec, out_path, args.format)
        return 0
    if args.command == "spec:render-mapping":
        docx_path = Path(args.docx)
        mapping_path = Path(args.mapping)
        out_path = Path(args.out)
        spec = _build_spec(docx_path)
        checklist = build_initial_checklist_rows(spec)
        mapping = load_mapping(mapping_path, default_schema=args.default_schema)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render_mapping_md(checklist, mapping), encoding="utf-8")
        return 0
    if args.command == "spec:diff":
        old_docx = Path(args.old_docx)
        new_docx = Path(args.new_docx)
        out_md = Path(args.out_md)
        out_json = Path(args.out_json)
        old_spec = _build_spec(old_docx)
        new_spec = _build_spec(new_docx)
        report = diff_specs(old_spec, new_spec)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_diff_markdown(report), encoding="utf-8")
        out_json.write_text(render_diff_json(report), encoding="utf-8")
        return 0
    if args.command == "spec:gate":
        exit_code, findings = evaluate_spec_gate(
            args.docx,
            args.mapping,
            required_sections=args.required_section,
            default_schema=args.default_schema,
        )
        print(render_spec_gate_summary(findings))
        return exit_code

    ap.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
