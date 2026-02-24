"""Generate TMJ 2025 closing report DOCX using the v2 template.

Usage (local/offline):
  Set-Location npbb\\backend
  $env:DATABASE_URL="sqlite:///./tmp_tmj.db"
  python -m scripts.generate_tmj2025_closing_report --template "C:\\Users\\NPBB\\Desktop\\Fechamento_TMJB2025_Modelo_NPBB_v2.docx"

Notes:
- The generator edits a copy of the template by anchoring on stable headings (Heading 1/2).
- It does not require `docxtpl` placeholders.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from sqlmodel import Session

from app.db.database import engine
from app.db.metadata import SQLModel
from app.reports.tmj2025_word import RenderOptions, generate_tmj2025_closing_report


def _parse_date_list(value: str | None) -> tuple[date, ...] | None:
    if not value:
        return None
    out: list[date] = []
    for part in str(value).split(","):
        part = part.strip()
        if not part:
            continue
        out.append(date.fromisoformat(part))
    return tuple(out) if out else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--template",
        type=str,
        default=r"C:\Users\NPBB\Desktop\Fechamento_TMJB2025_Modelo_NPBB_v2.docx",
        help="Caminho do template DOCX v2.",
    )
    ap.add_argument(
        "--output",
        type=str,
        default="",
        help="Caminho do DOCX de saida (default: npbb/reports/tmj2025/Fechamento_TMJB2025_auto.docx).",
    )
    ap.add_argument("--event-id", type=int, default=None)
    ap.add_argument("--session-key-prefix", type=str, default="TMJ2025_")
    ap.add_argument(
        "--expected-show-dates",
        type=str,
        default="",
        help="Lista CSV de datas (YYYY-MM-DD) esperadas para show (default: padrao TMJ 2025).",
    )
    ap.add_argument("--fail-on-dq-blocked", action="store_true")
    args = ap.parse_args(argv)

    template_path = Path(args.template).expanduser()
    if not template_path.exists():
        raise FileNotFoundError(f"Template nao encontrado: {template_path}")

    if args.output:
        output_path = Path(args.output).expanduser()
    else:
        output_path = (
            Path(__file__).resolve().parents[2]
            / "reports"
            / "tmj2025"
            / "Fechamento_TMJB2025_auto.docx"
        )

    expected = _parse_date_list(args.expected_show_dates)
    opts = RenderOptions(
        event_id=args.event_id,
        session_key_prefix=args.session_key_prefix,
        expected_show_dates=expected or RenderOptions().expected_show_dates,
        fail_on_dq_blocked=bool(args.fail_on_dq_blocked),
    )

    if engine.url.drivername.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        out = generate_tmj2025_closing_report(
            session,
            template_path=template_path,
            output_path=output_path,
            options=opts,
        )

    print(f"DOCX gerado em: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
