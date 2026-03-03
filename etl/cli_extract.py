"""CLI for running TMJ 2025 extractors.

This CLI is intentionally local/offline:
- writes staging artifacts to disk,
- writes evidence envelopes for audit,
- avoids requiring database connectivity at this stage.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

try:  # pragma: no cover - import style depends on execution context
    from npbb.etl.extract.extract_pdf_assisted import extract_pdf_assisted
    from npbb.etl.extract.extract_pptx_slide_text import extract_pptx_slide_text
    from npbb.etl.extract.extract_xlsx_leads_festival import extract_leads_xlsx
    from npbb.etl.extract.extract_xlsx_optin_aceitos import extract_optin_xlsx
except ModuleNotFoundError:  # local repo execution (cwd at repository root)
    from etl.extract.extract_pdf_assisted import extract_pdf_assisted
    from etl.extract.extract_pptx_slide_text import extract_pptx_slide_text
    from etl.extract.extract_xlsx_leads_festival import extract_leads_xlsx
    from etl.extract.extract_xlsx_optin_aceitos import extract_optin_xlsx


def _load_sources_config(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "sources" not in data:
        raise ValueError("Config must be a mapping with 'sources' list.")
    sources = data["sources"]
    if not isinstance(sources, list):
        raise ValueError("'sources' must be a list.")
    return sources


def run_extract_all(*, config_path: Path, out_dir: Path, include_pii: bool = False) -> None:
    sources = _load_sources_config(config_path)
    for s in sources:
        source_id = s["source_id"]
        kind = s["kind"]
        path = Path(s["path"])
        extractor = s.get("extractor", "")

        if extractor == "xlsx_optin_aceitos":
            extract_optin_xlsx(
                source_id=source_id,
                xlsx_path=path,
                out_dir=out_dir,
                sheet_name=s.get("sheet") or None,
                include_pii=include_pii,
            )
        elif extractor == "xlsx_leads_festival":
            extract_leads_xlsx(
                source_id=source_id,
                xlsx_path=path,
                out_dir=out_dir,
                sheet_name=s.get("sheet") or None,
                include_pii=include_pii,
            )
        elif extractor == "pptx_slide_text":
            extract_pptx_slide_text(source_id=source_id, pptx_path=path, out_dir=out_dir)
        elif extractor == "pdf_assisted":
            extract_pdf_assisted(
                source_id=source_id,
                pdf_path=path,
                out_dir=out_dir,
                template=s.get("template", "access_control"),
            )
        else:
            raise ValueError(f"Unknown extractor in config for {source_id}: {extractor} ({kind})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ex_all = sub.add_parser("tmj2025:extract-all", help="Run all extractors from a YAML config.")
    ex_all.add_argument("--config", required=True)
    ex_all.add_argument("--out-dir", required=True)
    ex_all.add_argument("--include-pii", action="store_true")

    args = ap.parse_args(argv)
    if args.cmd == "tmj2025:extract-all":
        run_extract_all(
            config_path=Path(args.config),
            out_dir=Path(args.out_dir),
            include_pii=bool(args.include_pii),
        )
        return 0

    ap.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
