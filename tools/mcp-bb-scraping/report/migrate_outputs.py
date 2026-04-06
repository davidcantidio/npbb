#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

BASE_PREFIXES = [
    "indicadores_bb_por_mes",
    "top_hashtags_bb",
    "top_mentions_bb",
    "instagram_posts",
    "instagram_profile",
    "tiktok_profile",
    "tiktok_videos",
    "x_profile",
    "x_tweets",
    "summary",
    "indicadores",
    "ig_links",
    "tiktok_links",
    "run",
    "posts",
]
BASE_PREFIXES.sort(key=len, reverse=True)

OWNER_COLUMNS = [
    "owner_username",
    "owner",
    "handle",
    "username",
    "account",
    "account_name",
    "perfil",
    "user",
    "creator",
]

URL_COLUMNS = ["post_url", "url", "link", "permalink"]

URL_HANDLE_RE = re.compile(r"instagram\.com/([^/?#]+)/", re.IGNORECASE)


def resolve_root() -> Path:
    env = os.getenv("PIPELINE_ROOT") or os.getenv("MCP_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    base = Path(__file__).resolve().parent
    return base.parent if base.name == "report" else base


ROOT = resolve_root()


def resolve_path(value: str, root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def normalize_handle(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    raw = str(value).strip().lstrip("@")
    return raw or None


def sanitize_label(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    safe = re.sub(r"[^a-z0-9._-]+", "_", raw).strip("_")
    return safe or None


def sanitize_handle(value: Optional[str]) -> Optional[str]:
    return sanitize_label(normalize_handle(value))


def compact_handle(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return re.sub(r"[^a-z0-9]+", "", value.lower()) or None


def load_handle_maps(root: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    mapping: Dict[str, str] = {}
    path = root / "config" / "instagram_handles.csv"
    if not path.exists():
        return mapping, {}
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not isinstance(row, dict):
                    continue
                raw_handle = row.get("handle")
                raw_name = row.get("name")
                safe_handle = normalize_handle(raw_handle)
                name = str(raw_name or "").strip()
                if safe_handle and name:
                    mapping[safe_handle.lower()] = name
    except OSError:
        return mapping, {}

    compact_counts: Dict[str, int] = {}
    compact_map: Dict[str, str] = {}
    for handle in mapping:
        key = compact_handle(handle)
        if not key:
            continue
        compact_counts[key] = compact_counts.get(key, 0) + 1
        if key not in compact_map:
            compact_map[key] = handle
    for key, count in list(compact_counts.items()):
        if count != 1 and key in compact_map:
            compact_map.pop(key, None)
    return mapping, compact_map


def canonical_handle(
    value: Optional[str],
    handle_map: Dict[str, str],
    compact_map: Dict[str, str],
) -> Optional[str]:
    raw = normalize_handle(value)
    if not raw:
        return None
    lower = raw.lower()
    if lower in handle_map:
        return lower
    compact = compact_handle(lower)
    if compact and compact in compact_map:
        return compact_map[compact].lower()
    return lower


def handle_from_posts_filename(path: Path, known_handles: Sequence[str]) -> Optional[str]:
    stem = path.stem
    if not stem.lower().endswith("_posts"):
        return None
    base = stem[:-6]
    if not base:
        return None
    base_lower = base.lower()
    for handle in known_handles:
        handle_lower = handle.lower()
        if base_lower == handle_lower or base_lower.endswith("_" + handle_lower):
            return handle
    if "_" in base:
        return base.split("_")[-1]
    return base


def detect_delimiter(path: Path) -> str:
    try:
        line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    except Exception:
        return ";"
    candidates = {";": line.count(";"), ",": line.count(","), "\t": line.count("\t")}
    best = max(candidates.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else ";"


def parse_handle_from_url(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    match = URL_HANDLE_RE.search(str(value))
    return match.group(1) if match else None


def infer_handle_from_csv(path: Path) -> Optional[str]:
    delimiter = detect_delimiter(path)
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            for row in reader:
                if not isinstance(row, dict):
                    continue
                for key in OWNER_COLUMNS:
                    value = row.get(key)
                    if value:
                        return normalize_handle(value)
                for key in URL_COLUMNS:
                    value = row.get(key)
                    handle_value = parse_handle_from_url(value)
                    if handle_value:
                        return normalize_handle(handle_value)
                break
    except OSError:
        return None
    return None


def infer_handle_from_json(path: Path) -> Optional[str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    row = None
    if isinstance(data, list) and data:
        row = data[0]
    elif isinstance(data, dict):
        for key in ("rows", "posts", "data", "items"):
            if isinstance(data.get(key), list) and data[key]:
                row = data[key][0]
                break
    if not isinstance(row, dict):
        return None
    for key in OWNER_COLUMNS:
        value = row.get(key)
        if value:
            return normalize_handle(value)
    for key in URL_COLUMNS:
        value = row.get(key)
        handle_value = parse_handle_from_url(value)
        if handle_value:
            return normalize_handle(handle_value)
    return None


def infer_handle_from_posts(path: Path) -> Optional[str]:
    if path.suffix.lower() == ".csv":
        return infer_handle_from_csv(path)
    if path.suffix.lower() == ".json":
        return infer_handle_from_json(path)
    return None


def output_posts_filename(name: Optional[str], handle: Optional[str], ext: str) -> str:
    safe_name = sanitize_label(name)
    safe_handle = sanitize_handle(handle)
    parts = [safe_name, safe_handle, "posts"]
    parts = [p for p in parts if p]
    return f"{'_'.join(parts)}.{ext}"


def output_filename(prefix: str, handle: Optional[str], ext: str) -> str:
    safe_handle = sanitize_handle(handle)
    if safe_handle:
        return f"{prefix}_{safe_handle}.{ext}"
    return f"{prefix}.{ext}"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for idx in range(1, 1000):
        candidate = path.with_name(f"{stem}__dup{idx}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Falha ao gerar caminho unico para {path}")


def hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def files_identical(a: Path, b: Path) -> bool:
    try:
        if a.stat().st_size != b.stat().st_size:
            return False
    except OSError:
        return False
    return hash_file(a) == hash_file(b)


def iter_files(root: Path) -> Iterable[Path]:
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            if current.is_dir():
                if current.name == "_duplicates":
                    continue
                for child in current.iterdir():
                    stack.append(child)
            elif current.is_file():
                yield current
        except OSError:
            continue


def classify_file(path: Path, known_handles: Sequence[str]) -> Tuple[str, Optional[str], Optional[str]]:
    stem = path.stem
    lower = stem.lower()
    if lower.startswith("indicadores_consolidados"):
        return "consolidated", None, None
    if lower.startswith("instagram_posts_enriched"):
        handle = None
        if lower != "instagram_posts_enriched" and "_" in stem:
            handle = stem[len("instagram_posts_enriched_") :]
        return "legacy_posts", None, handle
    if lower.endswith("_posts"):
        handle = handle_from_posts_filename(path, known_handles)
        return "posts", None, handle
    for prefix in BASE_PREFIXES:
        if lower.startswith(prefix + "_"):
            handle = stem[len(prefix) + 1 :]
            return "base", prefix, handle
    return "skip", None, None


def move_with_conflict(
    src: Path,
    dest: Path,
    rel_src: Path,
    out_root: Path,
    duplicates_dir: Path,
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    if src == dest:
        stats["skipped"] += 1
        return
    if not dest.exists():
        stats["moved"] += 1
        if dry_run:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        return
    if files_identical(src, dest):
        stats["deduped"] += 1
        if dry_run:
            return
        src.unlink(missing_ok=True)
        return

    src_size = src.stat().st_size
    dest_size = dest.stat().st_size
    prefer_src = src_size > dest_size
    if prefer_src:
        backup_rel = dest.relative_to(out_root)
        backup_path = unique_path(duplicates_dir / backup_rel)
        stats["conflicts"] += 1
        if dry_run:
            return
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dest), str(backup_path))
        shutil.move(str(src), str(dest))
    else:
        backup_path = unique_path(duplicates_dir / rel_src)
        stats["conflicts"] += 1
        if dry_run:
            return
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(backup_path))


def remove_empty_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if not path.is_dir():
            continue
        if path.name == "_duplicates":
            continue
        try:
            next(path.iterdir())
        except StopIteration:
            path.rmdir()
        except OSError:
            continue


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Move outputs to out/<athlete> and rename enriched posts files.",
    )
    parser.add_argument("--out", default="out", help="Base output folder (relative to repo root).")
    parser.add_argument("--include-data", action="store_true", help="Also scan data/ for legacy outputs.")
    parser.add_argument("--dry-run", action="store_true", help="Only print actions without moving files.")
    args = parser.parse_args()

    out_root = resolve_path(args.out, ROOT)
    if not out_root.exists():
        raise SystemExit(f"Pasta de saida nao encontrada: {out_root}")

    handle_map, compact_map = load_handle_maps(ROOT)
    known_handles = sorted(handle_map.keys(), key=len, reverse=True)

    search_dirs = [out_root]
    if args.include_data:
        data_dir = resolve_path("data", ROOT)
        if data_dir.exists():
            search_dirs.append(data_dir)

    duplicates_dir = out_root / "_duplicates"

    stats = {"moved": 0, "skipped": 0, "deduped": 0, "conflicts": 0, "unresolved": 0}

    for root_dir in search_dirs:
        for path in iter_files(root_dir):
            rel_path = path.relative_to(root_dir)
            kind, prefix, raw_handle = classify_file(path, known_handles)
            if kind == "skip":
                continue

            if kind == "consolidated":
                dest = out_root / path.name
                move_with_conflict(path, dest, rel_path, out_root, duplicates_dir, args.dry_run, stats)
                continue

            handle = canonical_handle(raw_handle, handle_map, compact_map)
            if kind in {"posts", "legacy_posts"} and (not handle or handle not in handle_map):
                inferred = infer_handle_from_posts(path)
                inferred_handle = canonical_handle(inferred, handle_map, compact_map)
                if inferred_handle:
                    handle = inferred_handle
            if not handle:
                stats["unresolved"] += 1
                continue

            athlete_name = handle_map.get(handle)
            athlete_dir = sanitize_label(athlete_name) or sanitize_handle(handle)
            if not athlete_dir:
                stats["unresolved"] += 1
                continue

            dest_dir = out_root / athlete_dir
            ext = path.suffix.lstrip(".").lower()

            if kind in {"posts", "legacy_posts"}:
                dest_name = output_posts_filename(athlete_name, handle, ext)
            else:
                dest_name = output_filename(prefix or "", handle, ext)
            dest = dest_dir / dest_name

            move_with_conflict(path, dest, rel_path, out_root, duplicates_dir, args.dry_run, stats)

    if not args.dry_run:
        remove_empty_dirs(out_root)

    print(
        "Concluido."
        f" moved={stats['moved']}"
        f" deduped={stats['deduped']}"
        f" conflicts={stats['conflicts']}"
        f" skipped={stats['skipped']}"
        f" unresolved={stats['unresolved']}"
        f"{' (dry-run)' if args.dry_run else ''}"
    )


if __name__ == "__main__":
    main()
