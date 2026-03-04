from __future__ import annotations

import argparse
from pathlib import Path

from .ppt_audit import PptAuditConfig, audit_presentation
from .pipeline import PipelineConfig, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lead_pipeline",
        description="Pipeline ETL para consolidacao e validacao de leads.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Executa pipeline do lote.")
    run_parser.add_argument("--lote", required=True, help="Identificador do lote.")
    run_parser.add_argument(
        "--inputs",
        nargs="+",
        help="Lista de arquivos de entrada.",
    )
    run_parser.add_argument(
        "--scan-root",
        help="Diretorio raiz para descoberta automatica de fontes.",
    )
    run_parser.add_argument(
        "--output-root",
        default="./eventos",
        help="Diretorio raiz para gravacao dos artefatos do lote.",
    )

    audit_parser = subparsers.add_parser("audit-ppt", help="Audita apresentacao PPT contra fonte de verdade.")
    audit_parser.add_argument("--lote", required=True, help="Identificador do lote.")
    audit_parser.add_argument("--ppt", required=True, help="Arquivo PowerPoint a ser auditado.")
    audit_parser.add_argument("--truth-csv", required=True, help="CSV fonte de verdade.")
    audit_parser.add_argument(
        "--output-root",
        default="./eventos",
        help="Diretorio raiz para gravacao dos artefatos do lote.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        if not args.inputs and not args.scan_root:
            parser.error("Use --inputs ou --scan-root.")

        config = PipelineConfig(
            lote_id=args.lote,
            input_files=[Path(path) for path in (args.inputs or [])],
            scan_root=Path(args.scan_root) if args.scan_root else None,
            output_root=Path(args.output_root),
        )
        result = run_pipeline(config)
        print(f"Status: {result.status}")
        print(f"Decision: {result.decision}")
        print(f"Output: {result.output_dir}")
        return result.exit_code

    if args.command == "audit-ppt":
        config = PptAuditConfig(
            lote_id=args.lote,
            ppt_path=Path(args.ppt),
            truth_csv_path=Path(args.truth_csv),
            output_root=Path(args.output_root),
        )
        result = audit_presentation(config)
        print(f"Status: {result.status}")
        print(f"Decision: {result.decision}")
        print(f"Output: {result.output_dir}")
        return result.exit_code

    parser.print_help()
    return 1
