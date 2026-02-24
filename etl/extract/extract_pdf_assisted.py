"""Assisted extractor for PDFs when no robust PDF table library is available.

This writes a template staging artifact and an evidence note marking the source
as MANUAL. The operator can fill the template and later stages can load it.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from npbb.etl.extract.common import EvidenceEnvelope, snapshot_file, utc_now_iso, write_csv, write_json


def _approx_pdf_page_count(pdf_bytes: bytes) -> int:
    # Best-effort page count heuristic; may over/under count in some PDFs.
    return pdf_bytes.count(b"/Type /Page") - pdf_bytes.count(b"/Type /Pages")


def build_access_control_template_rows(source_id: str) -> List[Dict[str, Any]]:
    # Template has no data by default.
    return []


def write_access_control_template(*, source_id: str, out_dir: Path) -> Path:
    out_path = out_dir / f"stg_access_control_template__{source_id}.csv"
    fields = [
        "source_id",
        "session_name",
        "ingressos_validos",
        "invalidos",
        "bloqueados",
        "presentes",
        "ausentes",
        "comparecimento_pct",
        "pdf_page",
        "evidence",
    ]
    write_csv(out_path, build_access_control_template_rows(source_id), fieldnames=fields)
    return out_path


def write_dimac_template(*, source_id: str, out_dir: Path) -> Path:
    out_path = out_dir / f"stg_dimac_manual_template__{source_id}.json"
    payload = {
        "source_id": source_id,
        "template_kind": "DIMAC",
        "requested_items": [
            {
                "metric_key": "dimac.profile.age_distribution",
                "description": "Age distribution table (percent/total) as shown in the report.",
                "location_raw": "",
                "evidence": "",
                "value_raw": None,
            },
            {
                "metric_key": "dimac.profile.gender_distribution",
                "description": "Gender distribution table (percent/total) as shown in the report.",
                "location_raw": "",
                "evidence": "",
                "value_raw": None,
            },
            {
                "metric_key": "dimac.satisfaction.overall",
                "description": "Overall satisfaction indicators (percent) as shown in the report.",
                "location_raw": "",
                "evidence": "",
                "value_raw": None,
            },
        ],
        "notes": [
            "This is an assisted template. Fill location_raw with page reference and evidence with table/figure title.",
            "If microdata exists, prefer ingesting the microdata instead of copying aggregates from PDF.",
        ],
    }
    write_json(out_path, payload)
    return out_path


def write_mtc_template(*, source_id: str, out_dir: Path) -> Path:
    out_path = out_dir / f"stg_mtc_manual_template__{source_id}.json"
    payload = {
        "source_id": source_id,
        "template_kind": "MTC",
        "requested_items": [
            {
                "metric_key": "mtc.press.clippings_summary",
                "description": "Press/clipping summary KPIs and breakdowns shown in the report.",
                "location_raw": "",
                "evidence": "",
                "value_raw": None,
            }
        ],
        "notes": [
            "This is an assisted template. Fill location_raw with page reference and evidence with table/figure title.",
            "If a detailed clipping base exists, prefer ingesting the detailed base instead of copying aggregates.",
        ],
    }
    write_json(out_path, payload)
    return out_path


def extract_pdf_assisted(
    *,
    source_id: str,
    pdf_path: Path,
    out_dir: Path,
    template: str,
) -> Dict[str, Any]:
    started = utc_now_iso()
    notes: List[str] = []

    snap = snapshot_file(pdf_path)

    try:
        pdf_bytes = pdf_path.read_bytes()
        page_count = _approx_pdf_page_count(pdf_bytes)
    except Exception:
        page_count = -1
        notes.append("Failed to read pdf bytes for page count heuristic.")

    if template == "access_control":
        artifact = write_access_control_template(source_id=source_id, out_dir=out_dir)
    elif template == "dimac":
        artifact = write_dimac_template(source_id=source_id, out_dir=out_dir)
    elif template == "mtc":
        artifact = write_mtc_template(source_id=source_id, out_dir=out_dir)
    else:
        raise ValueError("Unknown template: " + template)

    finished = utc_now_iso()
    evidence_json = out_dir / f"evidence__pdf_assisted__{source_id}.json"

    env = EvidenceEnvelope(
        extractor="extract_pdf_assisted",
        source_id=source_id,
        source_path=str(pdf_path),
        started_at=started,
        finished_at=finished,
        status="MANUAL",
        notes=notes
        + [
            "No PDF parsing library is available in the current environment.",
            "Template artifact generated for operator-assisted extraction.",
        ],
        stats={
            "file_snapshot": {"sha256": snap.sha256, "size_bytes": snap.size_bytes, "mtime_utc": snap.mtime_utc},
            "template": template,
            "approx_page_count": page_count,
            "artifact": str(artifact),
        },
    )
    write_json(evidence_json, env.to_dict())

    return {"artifact": artifact, "evidence": evidence_json}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument(
        "--template",
        required=True,
        choices=("access_control", "dimac", "mtc"),
    )
    args = ap.parse_args(argv)

    extract_pdf_assisted(
        source_id=args.source_id,
        pdf_path=Path(args.pdf),
        out_dir=Path(args.out_dir),
        template=args.template,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
