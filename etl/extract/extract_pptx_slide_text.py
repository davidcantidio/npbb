"""Extractor for PPTX: slide-by-slide text inventory.

We avoid external dependencies (python-pptx) by parsing the zipped PPTX XML.
This produces a robust raw staging that can be mapped to metrics later.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from npbb.etl.extract.common import (
    EvidenceEnvelope,
    snapshot_file,
    utc_now_iso,
    write_csv,
    write_json,
    write_jsonl,
)


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


@dataclass(frozen=True)
class SlideText:
    slide_number: int
    slide_filename: str
    slide_title: str
    text_items: List[str]

    def as_dict(self, *, source_id: str) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "slide_number": self.slide_number,
            "slide_filename": self.slide_filename,
            "slide_title": self.slide_title,
            "text_items": list(self.text_items),
        }


def _extract_text_items_from_slide_xml(xml_bytes: bytes) -> Tuple[str, List[str]]:
    """Return (title, text_items) from a slide xml."""
    root = ET.fromstring(xml_bytes)

    title = ""
    text_items: List[str] = []

    for sp in root.findall(".//p:sp", namespaces=NS):
        # Determine whether this shape is a title placeholder
        ph = sp.find(".//p:nvSpPr/p:nvPr/p:ph", namespaces=NS)
        ph_type = ph.attrib.get("type") if ph is not None else ""
        is_title = ph_type in {"title", "ctrTitle"}

        texts = [t.text for t in sp.findall(".//a:t", namespaces=NS) if (t.text or "").strip()]
        if not texts:
            continue
        joined = " ".join(x.strip() for x in texts if x and x.strip())
        if is_title and not title:
            title = joined
        else:
            text_items.append(joined)

    # Fallback: first text item as title when title placeholder is missing
    if not title and text_items:
        title = text_items[0]
        text_items = text_items[1:]

    return title, text_items


def extract_pptx_slide_text(
    *,
    source_id: str,
    pptx_path: Path,
    out_dir: Path,
) -> Dict[str, Any]:
    started = utc_now_iso()
    notes: List[str] = []

    snap = snapshot_file(pptx_path)

    slides: List[SlideText] = []

    with zipfile.ZipFile(pptx_path, "r") as zf:
        slide_files = [n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        slide_files.sort(key=lambda s: int(re.search(r"(\d+)", s).group(1)))

        for slide_fn in slide_files:
            slide_num = int(re.search(r"(\d+)", slide_fn).group(1))
            xml_bytes = zf.read(slide_fn)
            title, items = _extract_text_items_from_slide_xml(xml_bytes)
            slides.append(
                SlideText(
                    slide_number=slide_num,
                    slide_filename=slide_fn,
                    slide_title=title,
                    text_items=items,
                )
            )

    finished = utc_now_iso()

    staging_csv = out_dir / f"stg_pptx_slide_text__{source_id}.csv"
    staging_jsonl = out_dir / f"stg_pptx_slide_text__{source_id}.raw.jsonl"
    evidence_json = out_dir / f"evidence__stg_pptx_slide_text__{source_id}.json"

    # Flatten for CSV (avoid newlines)
    csv_rows: List[Dict[str, Any]] = []
    for s in slides:
        csv_rows.append(
            {
                "source_id": source_id,
                "slide_number": s.slide_number,
                "slide_filename": s.slide_filename,
                "slide_title": s.slide_title,
                "text": " | ".join(s.text_items),
            }
        )

    write_csv(
        staging_csv,
        csv_rows,
        fieldnames=["source_id", "slide_number", "slide_filename", "slide_title", "text"],
    )
    write_jsonl(staging_jsonl, [s.as_dict(source_id=source_id) for s in slides])

    env = EvidenceEnvelope(
        extractor="extract_pptx_slide_text",
        source_id=source_id,
        source_path=str(pptx_path),
        started_at=started,
        finished_at=finished,
        status="OK",
        notes=notes,
        stats={
            "file_snapshot": {"sha256": snap.sha256, "size_bytes": snap.size_bytes, "mtime_utc": snap.mtime_utc},
            "slides": len(slides),
            "outputs": {"csv": str(staging_csv), "jsonl": str(staging_jsonl)},
        },
    )
    write_json(evidence_json, env.to_dict())

    return {"csv": staging_csv, "jsonl": staging_jsonl, "evidence": evidence_json}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--pptx", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)

    extract_pptx_slide_text(
        source_id=args.source_id,
        pptx_path=Path(args.pptx),
        out_dir=Path(args.out_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
