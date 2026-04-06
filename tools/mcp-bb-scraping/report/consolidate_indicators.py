#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime, timezone
from glob import glob
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def resolve_root() -> Path:
    env = os.getenv("PIPELINE_ROOT") or os.getenv("MCP_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    base = Path(__file__).resolve().parent
    return base.parent if base.name == "report" else base


ROOT = resolve_root()
HANDLE_NAME_MAP: Optional[Dict[str, str]] = None


def resolve_path(value: str, root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def resolve_glob(pattern: str, root: Path) -> str:
    if Path(pattern).is_absolute():
        return pattern
    return str(root / pattern)


def to_rel_posix(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Falha ao ler arquivo: {path}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON invalido: {path}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"JSON invalido: esperado objeto na raiz: {path}")
    return data


def normalize_handle(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    return raw.lstrip("@")


def sanitize_label(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    safe = re.sub(r"[^a-z0-9._-]+", "_", raw).strip("_")
    return safe or None


def load_handle_name_map(root: Path) -> Dict[str, str]:
    global HANDLE_NAME_MAP
    if HANDLE_NAME_MAP is not None:
        return HANDLE_NAME_MAP
    mapping: Dict[str, str] = {}
    path = root / "config" / "instagram_handles.csv"
    if path.exists():
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
                        mapping[safe_handle] = name
        except OSError:
            mapping = {}
    HANDLE_NAME_MAP = mapping
    return mapping


def build_name_to_handle_map(handle_name_map: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for handle, name in handle_name_map.items():
        key = sanitize_label(name)
        if key and key not in out:
            out[key] = handle
    return out


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
            return normalize_handle(handle)
    if "_" in base:
        return normalize_handle(base.split("_")[-1])
    return normalize_handle(base)


def parse_pairs(items: Iterable[Any]) -> List[Tuple[Optional[str], Optional[Any]]]:
    out: List[Tuple[Optional[str], Optional[Any]]] = []
    for item in items:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append((item[0], item[1]))
    return out


def normalize_csv_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=True)
    return value


def detect_delimiter(path: Path) -> str:
    try:
        line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    except Exception:
        return ";"
    candidates = {";": line.count(";"), ",": line.count(","), "\t": line.count("\t")}
    best = max(candidates.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else ";"


def read_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
    delimiter = detect_delimiter(path)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        fieldnames = reader.fieldnames or []
        rows = [row for row in reader]
    return fieldnames, rows


def write_csv_rows(path: Path, rows: List[Dict[str, Any]], base_fields: Sequence[str]) -> None:
    extras = set()
    for row in rows:
        extras.update(row.keys())
    ordered_fields = list(base_fields) + sorted(k for k in extras if k not in base_fields)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ordered_fields, delimiter=";")
        writer.writeheader()
        for row in rows:
            clean = {k: normalize_csv_value(v) for k, v in row.items()}
            writer.writerow(clean)


def collect_monthly(handle: str, monthly: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    zero_rows: List[Dict[str, Any]] = []
    for row in monthly.get("rows", []) if isinstance(monthly, dict) else []:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "handle": handle,
                "month": row.get("month"),
                "posts_bb": row.get("posts_bb"),
                "posts_total": row.get("posts_total"),
            }
        )
    for month in monthly.get("zero_months", []) if isinstance(monthly, dict) else []:
        zero_rows.append({"handle": handle, "month": month})
    return rows, zero_rows


def collect_ranked_pairs(handle: str, items: Iterable[Any], label_key: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for idx, (label, count) in enumerate(parse_pairs(items), start=1):
        rows.append(
            {
                "handle": handle,
                "rank": idx,
                label_key: label,
                "posts": count,
            }
        )
    return rows


def collect_performance_format(handle: str, perf_format: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not isinstance(perf_format, dict):
        return rows
    for fmt, metrics in perf_format.items():
        if not isinstance(metrics, dict):
            continue
        row: Dict[str, Any] = {"handle": handle, "format": fmt}
        for key, value in metrics.items():
            row[str(key)] = value
        rows.append(row)
    return rows


def collect_posts_rows(
    files: Sequence[Path],
    root: Path,
    known_handles: Sequence[str],
    name_to_handle: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    rows: List[Dict[str, Any]] = []
    skipped: List[Dict[str, str]] = []
    for path in files:
        fieldnames, csv_rows = read_csv_rows(path)
        if not fieldnames:
            skipped.append({"path": to_rel_posix(path, root), "reason": "sem_cabecalho"})
            continue
        if "owner_username" not in fieldnames:
            skipped.append({"path": to_rel_posix(path, root), "reason": "nao_enriquecido"})
            continue

        handle = handle_from_posts_filename(path, known_handles)
        if not handle:
            dir_key = sanitize_label(path.parent.name)
            handle = name_to_handle.get(dir_key) if dir_key else None
        if not handle:
            handle = normalize_handle(path.parent.name)
        if not handle:
            skipped.append({"path": to_rel_posix(path, root), "reason": "handle_nao_detectado"})
            continue

        principal_handle = f"@{handle}"
        source_file = to_rel_posix(path, root)
        source_dir = path.parent.name

        for row in csv_rows:
            clean = {k: (v if v is not None else "") for k, v in row.items()}
            if "post_url" not in clean and "url" in clean:
                clean["post_url"] = clean.pop("url")
            if "shortcode" not in clean:
                clean["shortcode"] = ""
            out = {
                "handle": handle,
                "principal_handle": principal_handle,
                "source_dir": source_dir,
                "source_file": source_file,
            }
            out.update(clean)
            rows.append(out)
    return rows, skipped


def collect_posts_files_from_dirs(out_dir: Path) -> List[Path]:
    files: List[Path] = []
    try:
        entries = list(out_dir.iterdir())
    except OSError:
        return files
    for entry in entries:
        if not entry.is_dir():
            continue
        name = entry.name.lower()
        if name == "_duplicates" or name.startswith("consolidados"):
            continue
        files.extend(entry.glob("*_posts.csv"))
    return sorted({p for p in files})


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Consolida posts e indicadores para consumo no Power BI.")
    default_posts_glob = "out/*/*_posts.csv"
    parser.add_argument(
        "--posts-glob",
        default=default_posts_glob,
        help="Padrao de arquivos de posts (CSV). Default: arquivos *_posts.csv dentro de out/<pasta>.",
    )
    parser.add_argument(
        "--glob",
        "--indicators-glob",
        dest="indicators_glob",
        default="out/*/indicadores.json",
        help="Padrao de arquivos indicadores.json.",
    )
    parser.add_argument(
        "--out",
        default="out/indicadores_consolidados.json",
        help="Caminho do arquivo JSON consolidado.",
    )
    args = parser.parse_args(argv)

    root = ROOT
    handle_name_map = load_handle_name_map(root)
    name_to_handle = build_name_to_handle_map(handle_name_map)
    known_handles = sorted(handle_name_map.keys(), key=len, reverse=True)

    posts_pattern = resolve_glob(args.posts_glob, root)
    post_files: List[Path] = []
    if args.posts_glob == default_posts_glob:
        post_files = collect_posts_files_from_dirs(resolve_path("out", root))
        if not post_files:
            post_files = [Path(p) for p in sorted(set(glob(posts_pattern, recursive=True)))]
    else:
        post_files = [Path(p) for p in sorted(set(glob(posts_pattern, recursive=True)))]
    if not post_files and args.posts_glob == default_posts_glob:
        legacy_patterns = [
            resolve_glob("out/*/instagram_posts_enriched_*.csv", root),
            resolve_glob("data/instagram_posts_enriched_*.csv", root),
        ]
        for pattern in legacy_patterns:
            post_files.extend(Path(p) for p in glob(pattern, recursive=True))
        post_files = sorted({p for p in post_files})

    if not post_files:
        raise SystemExit(f"Nenhum arquivo de posts encontrado para o padrao: {args.posts_glob}")

    indicators_pattern = resolve_glob(args.indicators_glob, root)
    indicator_files = sorted(glob(indicators_pattern, recursive=True))

    summary_rows: List[Dict[str, Any]] = []
    monthly_rows: List[Dict[str, Any]] = []
    monthly_zero_rows: List[Dict[str, Any]] = []
    brands_top10_rows: List[Dict[str, Any]] = []
    bb_other_owners_rows: List[Dict[str, Any]] = []
    bb_co_mentions_rows: List[Dict[str, Any]] = []
    performance_format_rows: List[Dict[str, Any]] = []
    skipped: List[Dict[str, str]] = []

    summary_rows, skipped_posts = collect_posts_rows(post_files, root, known_handles, name_to_handle)
    skipped.extend(skipped_posts)

    for raw_path in indicator_files:
        path = Path(raw_path)
        data = load_json(path)
        principal_handle = None
        meta = data.get("meta")
        if isinstance(meta, dict):
            principal_handle = meta.get("principal_handle")
        handle = normalize_handle(principal_handle)
        if not handle:
            dir_key = sanitize_label(path.parent.name)
            handle = name_to_handle.get(dir_key) if dir_key else None
        if not handle:
            handle = normalize_handle(path.parent.name)

        monthly = data.get("monthly", {})
        rows, zero_rows = collect_monthly(handle or "", monthly if isinstance(monthly, dict) else {})
        monthly_rows.extend(rows)
        monthly_zero_rows.extend(zero_rows)

        brands = data.get("brands", {})
        if isinstance(brands, dict):
            brands_top10_rows.extend(collect_ranked_pairs(handle or "", brands.get("top10", []), "brand_handle"))

        bb_origin = data.get("bb_origin", {})
        if isinstance(bb_origin, dict):
            bb_other_owners_rows.extend(
                collect_ranked_pairs(handle or "", bb_origin.get("bb_other_owners_top", []), "owner_handle")
            )

        branding = data.get("branding", {})
        if isinstance(branding, dict):
            bb_co_mentions_rows.extend(
                collect_ranked_pairs(
                    handle or "", branding.get("bb_sponsored_co_mentions_top5", []), "brand_handle"
                )
            )

        performance_format_rows.extend(collect_performance_format(handle or "", data.get("performance_format")))

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "posts_glob": args.posts_glob,
        "posts_files_count": len(post_files),
        "indicators_glob": args.indicators_glob,
        "indicators_files_count": len(indicator_files),
        "summary_source": "posts",
        "summary": summary_rows,
        "monthly": monthly_rows,
        "monthly_zero_months": monthly_zero_rows,
        "brands_top10": brands_top10_rows,
        "bb_other_owners_top": bb_other_owners_rows,
        "bb_sponsored_co_mentions_top5": bb_co_mentions_rows,
        "performance_format": performance_format_rows,
        "skipped": skipped,
    }

    out_path = resolve_path(args.out, root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    base = out_path.with_suffix("")
    post_fields = [
        "handle",
        "principal_handle",
        "source_dir",
        "source_file",
        "post_url",
        "shortcode",
        "datetime",
        "date",
        "caption",
        "hashtags",
        "mentions",
        "is_bb_mention",
        "bb_connection_type",
        "bb_markers_count",
        "likes",
        "comments",
        "views",
        "owner_username",
        "is_owner_profile",
        "media_type",
        "is_collab",
        "coauthors",
        "paid_partnership",
        "paid_partner",
        "location",
        "plays_or_views",
        "scraped_at",
    ]
    write_csv_rows(base.with_name(base.name + "_summary.csv"), summary_rows, post_fields)
    write_csv_rows(base.with_name(base.name + "_monthly.csv"), monthly_rows, ["handle", "month", "posts_bb", "posts_total"])
    write_csv_rows(base.with_name(base.name + "_monthly_zero_months.csv"), monthly_zero_rows, ["handle", "month"])
    write_csv_rows(base.with_name(base.name + "_brands_top10.csv"), brands_top10_rows, ["handle", "rank", "brand_handle", "posts"])
    write_csv_rows(
        base.with_name(base.name + "_bb_other_owners_top.csv"),
        bb_other_owners_rows,
        ["handle", "rank", "owner_handle", "posts"],
    )
    write_csv_rows(
        base.with_name(base.name + "_bb_sponsored_co_mentions_top5.csv"),
        bb_co_mentions_rows,
        ["handle", "rank", "brand_handle", "posts"],
    )
    write_csv_rows(
        base.with_name(base.name + "_performance_format.csv"),
        performance_format_rows,
        ["handle", "format"],
    )
    write_csv_rows(base.with_name(base.name + "_skipped.csv"), skipped, ["path", "reason"])
    print(f"Arquivo consolidado: {out_path}")
    print(f"CSVs gerados: {base.name}_*.csv")
    print(f"Arquivos de posts: {len(post_files)}")
    print(f"Arquivos de indicadores: {len(indicator_files)}")
    print(f"Resumo (posts): {len(summary_rows)} registros")
    print(f"Mensal: {len(monthly_rows)} registros")
    print(f"Marcas top10: {len(brands_top10_rows)} registros")
    print(f"Outros owners BB: {len(bb_other_owners_rows)} registros")
    print(f"Co-mencoes BB: {len(bb_co_mentions_rows)} registros")
    print(f"Performance formato: {len(performance_format_rows)} registros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
