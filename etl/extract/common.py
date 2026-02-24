"""Common helpers for extractors.

We standardize:
- output folder layout (staging + evidence),
- JSON evidence envelopes,
- basic PII hashing utilities (optional).
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def utc_now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write JSON UTF-8 to disk."""
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    """Write JSON Lines UTF-8 to disk."""
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")


def write_csv(path: Path, rows: List[Dict[str, Any]], *, fieldnames: List[str]) -> None:
    """Write a CSV file (UTF-8) with a fixed set of fieldnames."""
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in fieldnames})


def get_pii_salt() -> str:
    """Return PII salt used for hashing.

    Uses env vars in order:
    - PII_SALT
    - SECRET_KEY
    - fallback: constant (not recommended, but keeps scripts runnable)
    """
    return (
        os.getenv("PII_SALT")
        or os.getenv("SECRET_KEY")
        or "npbb-local-dev-salt"
    )


def hash_pii(value: str, *, salt: Optional[str] = None) -> str:
    """Hash a PII value with sha256(salt + normalized_value).

    Args:
        value: Raw value (cpf/email/phone).
        salt: Optional salt override.

    Returns:
        Hex sha256 digest.
    """
    s = (salt or get_pii_salt()).encode("utf-8")
    v = (value or "").strip().lower().encode("utf-8")
    return hashlib.sha256(s + b"|" + v).hexdigest()


@dataclass(frozen=True)
class FileSnapshot:
    """Snapshot of a local file for versioning (sha256/size/mtime)."""

    sha256: str
    size_bytes: int
    mtime_utc: str


def compute_sha256(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Compute sha256 of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_file(path: Path) -> FileSnapshot:
    """Create a FileSnapshot for a path."""
    st = path.stat()
    return FileSnapshot(
        sha256=compute_sha256(path),
        size_bytes=int(st.st_size),
        mtime_utc=datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
    )


@dataclass(frozen=True)
class EvidenceEnvelope:
    """Standard evidence payload written by extractors."""

    extractor: str
    source_id: str
    source_path: str
    started_at: str
    finished_at: str
    status: str  # OK | PARTIAL | MANUAL | FAILED
    notes: List[str]
    stats: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "extractor": self.extractor,
            "source_id": self.source_id,
            "source_path": self.source_path,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "notes": list(self.notes),
            "stats": dict(self.stats),
        }
