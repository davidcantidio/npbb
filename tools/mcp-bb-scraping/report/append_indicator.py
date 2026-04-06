#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import re
import statistics
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PostRow:
    post_url: str
    dt_utc: Optional[datetime]
    caption: str
    hashtags: List[str]
    mentions: List[str]
    is_bb_mention: bool
    bb_connection_type: Optional[str]
    bb_markers_count: Optional[int]
    likes: Optional[int]
    comments: Optional[int]
    views: Optional[int]
    owner_username: Optional[str]
    is_owner_profile: bool
    media_type: str
    shortcode: str
    is_collab: bool
    coauthors: List[str]
    paid_partnership: bool
    paid_partner: Optional[str]
    location: Optional[str]
    plays_or_views: Optional[int]
    scraped_at_utc: Optional[datetime]
    raw_datetime: str
    raw_date: str
    raw_scraped_at: str


TRUE_VALUES = {"true", "1", "yes", "y", "sim"}
FALSE_VALUES = {"false", "0", "no", "n", "nao", "não"}
TARGET_HANDLE: Optional[str] = None


def resolve_root() -> Path:
    env = os.getenv("PIPELINE_ROOT") or os.getenv("MCP_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    base = Path(__file__).resolve().parent
    return base.parent if base.name == "report" else base


ROOT = resolve_root()
KNOWN_HANDLES: Optional[List[str]] = None


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def normalize_handle(value: Optional[str]) -> Optional[str]:
    raw = (value or "").strip()
    if not raw:
        return None
    raw = raw.lstrip("@")
    safe = re.sub(r"[^a-z0-9._-]+", "_", raw, flags=re.IGNORECASE)
    safe = safe.strip("_")
    return safe.lower() or None


def load_known_handles() -> List[str]:
    global KNOWN_HANDLES
    if KNOWN_HANDLES is not None:
        return KNOWN_HANDLES
    handles: List[str] = []
    path = ROOT / "config" / "instagram_handles.csv"
    if path.exists():
        try:
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    name = row.get("handle") if isinstance(row, dict) else None
                    safe = normalize_handle(name)
                    if safe:
                        handles.append(safe)
        except OSError:
            handles = []
    KNOWN_HANDLES = sorted(set(handles), key=len, reverse=True)
    return KNOWN_HANDLES


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


def handle_from_filename(path: Path) -> Optional[str]:
    m = re.match(r"instagram_posts_enriched_(.+)\.csv$", path.name, flags=re.IGNORECASE)
    if m:
        return normalize_handle(m.group(1))
    return handle_from_posts_filename(path, load_known_handles())


def list_search_dirs() -> List[Path]:
    dirs = [ROOT, ROOT / "data", ROOT / "out"]
    out_root = ROOT / "out"
    if out_root.exists():
        for entry in out_root.iterdir():
            if entry.is_dir():
                dirs.append(entry)
    seen = set()
    unique: List[Path] = []
    for d in dirs:
        if d in seen:
            continue
        seen.add(d)
        unique.append(d)
    return unique


def list_handle_csvs(dirs: Sequence[Path]) -> List[Path]:
    out: List[Path] = []
    seen = set()
    for d in dirs:
        if not d.exists():
            continue
        for p in d.glob("instagram_posts_enriched_*.csv"):
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
        for p in d.glob("*_posts.csv"):
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
    return sorted(out, key=lambda p: p.name)


def resolve_csv_path(explicit: Optional[str], handle: Optional[str]) -> Tuple[str, Optional[str]]:
    if explicit:
        path = resolve_path(explicit)
        return str(path), handle or handle_from_filename(path)

    dirs = list_search_dirs()
    safe_handle = normalize_handle(handle)

    if safe_handle:
        for d in dirs:
            candidate = d / f"instagram_posts_enriched_{safe_handle}.csv"
            if candidate.exists():
                return str(candidate), safe_handle
            post_candidates = sorted(d.glob(f"*_{safe_handle}_posts.csv"))
            if post_candidates:
                if len(post_candidates) > 1:
                    lines = [
                        "Mais de um CSV encontrado para posts (novo padrao):",
                        *[f"- {p}" for p in post_candidates],
                        "Use --handle/--profile ou --csv para escolher.",
                    ]
                    raise SystemExit("\n".join(lines))
                return str(post_candidates[0]), safe_handle
            candidate = d / f"{safe_handle}_posts.csv"
            if candidate.exists():
                return str(candidate), safe_handle

    matches = list_handle_csvs(dirs)
    if len(matches) == 1:
        detected_handle = handle_from_filename(matches[0])
        return str(matches[0]), safe_handle or detected_handle
    if len(matches) > 1:
        lines = [
            "Mais de um CSV encontrado para posts:",
            *[f"- {p}" for p in matches],
            "Use --handle/--profile ou --csv para escolher.",
        ]
        raise SystemExit("\n".join(lines))

    legacy = [ROOT / "instagram_posts_enriched.csv", ROOT / "data" / "instagram_posts_enriched.csv"]
    for p in legacy:
        if p.exists():
            return str(p), safe_handle

    raise SystemExit("CSV nao encontrado. Use --handle/--profile ou --csv.")


def default_out_path(handle: Optional[str]) -> str:
    safe = normalize_handle(handle)
    if safe:
        return f"indicadores_{safe}.csv"
    return "indicadores.csv"


def monthly_out_filename(handle: Optional[str]) -> str:
    safe = normalize_handle(handle)
    if safe:
        return f"indicadores_bb_por_mes_{safe}.csv"
    return "indicadores_bb_por_mes.csv"


def resolve_monthly_out_path(out_path: str, handle: Optional[str]) -> str:
    base_dir = Path(out_path).resolve().parent
    return str(base_dir / monthly_out_filename(handle))


def detect_owner_handle(rows: Sequence["PostRow"]) -> Optional[str]:
    counts: Dict[str, int] = {}
    for r in rows:
        if not r.is_owner_profile:
            continue
        if not r.owner_username:
            continue
        counts[r.owner_username] = counts.get(r.owner_username, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]


def resolve_target_handle(rows: Sequence["PostRow"]) -> Optional[str]:
    if TARGET_HANDLE:
        return TARGET_HANDLE
    return detect_owner_handle(rows)


def parse_bool(value: Optional[str]) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return False
    if v in TRUE_VALUES:
        return True
    if v in FALSE_VALUES:
        return False
    return False


def parse_int(value: Optional[str]) -> Optional[int]:
    raw = (value or "").strip()
    if not raw:
        return None
    clean = re.sub(r"[^\d-]", "", raw)
    if clean in {"", "-"}:
        return None
    try:
        return int(clean)
    except ValueError:
        return None


def parse_iso_datetime_utc(value: str) -> Optional[datetime]:
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_fallback_date_utc(value: str) -> Optional[datetime]:
    raw = value.strip()
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_best_datetime_utc(datetime_value: str, date_value: str) -> Optional[datetime]:
    dt = parse_iso_datetime_utc(datetime_value)
    if dt is not None:
        return dt
    return parse_fallback_date_utc(date_value)


def split_list(value: Optional[str]) -> List[str]:
    raw = (value or "").strip()
    if not raw:
        return []
    parts = [p.strip().lower() for p in raw.split("|")]
    parts = [p for p in parts if p]
    return unique_in_order(parts)


def unique_in_order(items: Sequence[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def default_csv_path(handle: Optional[str] = None) -> str:
    path, _ = resolve_csv_path(None, handle)
    return path


def read_rows(csv_path: str) -> List[PostRow]:
    path = Path(csv_path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = reader.fieldnames or []
        has_owner_profile = "is_owner_profile" in fieldnames
        has_bb_connection = "bb_connection_type" in fieldnames
        has_bb_markers = "bb_markers_count" in fieldnames
        rows: List[PostRow] = []
        for r in reader:
            raw_datetime = str(r.get("datetime", "") or "")
            raw_date = str(r.get("date", "") or "")
            raw_scraped_at = str(r.get("scraped_at", "") or "")

            dt_utc = parse_best_datetime_utc(raw_datetime, raw_date)
            scraped_at_utc = parse_iso_datetime_utc(raw_scraped_at) if raw_scraped_at.strip() else None

            owner = (str(r.get("owner_username", "") or "").strip().lower() or None)
            media_type = str(r.get("media_type", "") or "").strip().lower() or "unknown"
            bb_connection_type = (
                (str(r.get("bb_connection_type", "") or "").strip().lower() or None) if has_bb_connection else None
            )
            bb_markers_count = parse_int(r.get("bb_markers_count")) if has_bb_markers else None
            if bb_markers_count is None:
                bb_markers_count = 0
            if has_owner_profile:
                is_owner_profile = parse_bool(r.get("is_owner_profile"))
            else:
                is_owner_profile = parse_bool(r.get("is_owner_filipe"))

            rows.append(
                PostRow(
                    post_url=str(r.get("post_url", "") or "").strip(),
                    dt_utc=dt_utc,
                    caption=str(r.get("caption", "") or "").strip(),
                    hashtags=split_list(r.get("hashtags")),
                    mentions=split_list(r.get("mentions")),
                    is_bb_mention=parse_bool(r.get("is_bb_mention")),
                    bb_connection_type=bb_connection_type,
                    bb_markers_count=bb_markers_count,
                    likes=parse_int(r.get("likes")),
                    comments=parse_int(r.get("comments")),
                    views=parse_int(r.get("views")),
                    owner_username=owner,
                    is_owner_profile=is_owner_profile,
                    media_type=media_type,
                    shortcode=str(r.get("shortcode", "") or "").strip(),
                    is_collab=parse_bool(r.get("is_collab")),
                    coauthors=split_list(r.get("coauthors")),
                    paid_partnership=parse_bool(r.get("paid_partnership")),
                    paid_partner=(str(r.get("paid_partner", "") or "").strip() or None),
                    location=(str(r.get("location", "") or "").strip() or None),
                    plays_or_views=parse_int(r.get("plays_or_views")),
                    scraped_at_utc=scraped_at_utc,
                    raw_datetime=raw_datetime,
                    raw_date=raw_date,
                    raw_scraped_at=raw_scraped_at,
                )
            )
    return rows


def fmt_pct(n: int, d: int) -> str:
    if d <= 0:
        return "N/A"
    return f"{(100.0 * n / d):.1f}% ({n}/{d})"


def fmt_ratio(n: int, d: int, *, decimals: int = 3) -> str:
    if d <= 0:
        return "N/A"
    return f"{(n / d):.{decimals}f} ({n}/{d})"


def fmt_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return "N/A"
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def fmt_date(dt: Optional[datetime]) -> str:
    if not dt:
        return "N/A"
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def median_or_na(values: List[int]) -> Optional[float]:
    if not values:
        return None
    return float(statistics.median(values))


def mean_or_na(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return float(statistics.fmean(values))


def safe_div(n: int, d: int) -> Optional[float]:
    if d <= 0:
        return None
    return n / d


def month_key(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m")


def top_n_counter(items: Iterable[str], n: int) -> List[Tuple[str, int]]:
    counts: Dict[str, int] = {}
    for item in items:
        k = item or ""
        if not k:
            continue
        counts[k] = counts.get(k, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def md_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def set_value(values: "OrderedDict[str, str]", key: str, value: Optional[object]) -> None:
    if key in values:
        return
    if value is None:
        values[key] = ""
    else:
        values[key] = str(value)


def fmt_float(value: Optional[float], decimals: int = 1) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def indicador_0(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Resumo da base"
    definition = (
        "Visão geral do dataset (todas as contas), cobertura de campos e principais owners. "
        "Assunções: `is_collab=true` é proxy de patrocinado; posts de outras contas entram; plays/views podem estar ausentes."
    )
    formula = "Contagens e percentuais simples sobre N_total; min/max de datas válidas; top owners por volume."

    total = len(rows)
    dates = [r.dt_utc for r in rows if r.dt_utc is not None]
    min_dt = min(dates) if dates else None
    max_dt = max(dates) if dates else None

    likes_filled = sum(1 for r in rows if r.likes is not None)
    comments_filled = sum(1 for r in rows if r.comments is not None)
    mentions_filled = sum(1 for r in rows if len(r.mentions) > 0)
    plays_filled = sum(1 for r in rows if r.plays_or_views is not None)

    owners = [r.owner_username or "(desconhecido)" for r in rows]
    top_owners = top_n_counter(owners, 5)

    gen_dt = datetime.now(timezone.utc)
    lines: List[str] = [
        f"- Total de linhas: {total}",
        f"- Intervalo de datas (min/max): {fmt_date(min_dt)} até {fmt_date(max_dt)}",
        f"- Likes preenchidos: {fmt_pct(likes_filled, total)}",
        f"- Comments preenchidos: {fmt_pct(comments_filled, total)}",
        f"- Mentions preenchidos: {fmt_pct(mentions_filled, total)}",
        f"- Plays/Views (plays_or_views) preenchidos: {fmt_pct(plays_filled, total)}",
        "",
        "Top 5 owners por volume (owner_username):",
        md_table(["owner_username", "posts"], [[o, str(c)] for o, c in top_owners]),
        "",
        f"- Data de geração (UTC): {fmt_dt(gen_dt)}",
    ]

    result = "\n".join(lines).rstrip()
    return title, definition, formula, [result]


def indicador_1(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Volume total de posts (geral)"
    definition = "Total de posts na base, sem filtrar por owner."
    formula = "N_total = total de linhas."
    total = len(rows)
    result = f"- N_total: {total}"
    return title, definition, formula, [result]


def indicador_2(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Posts que mencionam Banco do Brasil (geral)"
    definition = "Quantidade e share de posts com `is_bb_mention=true`, sem filtrar por owner."
    formula = "N_BB = count(is_bb_mention=true); Share_BB_total = N_BB / N_total."
    total = len(rows)
    n_bb = sum(1 for r in rows if r.is_bb_mention)
    share = fmt_pct(n_bb, total)
    result = "\n".join([f"- N_BB: {n_bb}", f"- Share_BB_total: {share}"])
    return title, definition, formula, [result]


def indicador_3(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Recência da última menção ao BB"
    definition = "Dias desde a última menção ao BB até a data de referência."
    formula = "last_bb_dt = max(dt | is_bb); ref_dt = max(scraped_at) se existir, senão now(); dias = (ref_dt - last_bb_dt).days."

    bb_dates = [r.dt_utc for r in rows if r.is_bb_mention and r.dt_utc is not None]
    last_bb = max(bb_dates) if bb_dates else None
    ref_candidates = [r.scraped_at_utc for r in rows if r.scraped_at_utc is not None]
    ref_dt = max(ref_candidates) if ref_candidates else datetime.now(timezone.utc)

    if last_bb is None:
        result = "\n".join([f"- last_bb_dt: N/A", f"- ref_dt: {fmt_dt(ref_dt)}", "- dias_desde_ultima_mencao: N/A"])
        return title, definition, formula, [result]

    delta_days = (ref_dt - last_bb).days
    result = "\n".join([f"- last_bb_dt: {fmt_dt(last_bb)}", f"- ref_dt: {fmt_dt(ref_dt)}", f"- dias: {delta_days}"])
    return title, definition, formula, [result]


def indicador_4(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Menções ao BB por mês"
    definition = "Distribuição mensal de posts BB, com total mensal para contexto."
    formula = "Agrupar por YYYY-MM usando dt; BB_mes = count(is_bb); Total_mes = count(all)."

    month_total: Dict[str, int] = {}
    month_bb: Dict[str, int] = {}
    for r in rows:
        if r.dt_utc is None:
            continue
        mk = month_key(r.dt_utc)
        month_total[mk] = month_total.get(mk, 0) + 1
        if r.is_bb_mention:
            month_bb[mk] = month_bb.get(mk, 0) + 1

    keys = sorted(month_total.keys())
    table_rows = [[k, str(month_bb.get(k, 0)), str(month_total.get(k, 0))] for k in keys]
    result = md_table(["mês", "posts_bb", "posts_total"], table_rows) if table_rows else "N/A (sem datas válidas)"
    return title, definition, formula, [result]


def indicador_5(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Consistência: intervalo entre menções ao BB"
    definition = "Mede o intervalo típico entre menções ao BB (dias)."
    formula = "Ordenar datas BB; diffs = delta em dias entre menções consecutivas; reportar median(diff) e mean(diff)."

    bb_dates = sorted([r.dt_utc for r in rows if r.is_bb_mention and r.dt_utc is not None])
    if len(bb_dates) < 2:
        return title, definition, formula, ["N/A (menos de 2 menções BB com data)"]

    diffs = [(bb_dates[i] - bb_dates[i - 1]).total_seconds() / 86400.0 for i in range(1, len(bb_dates))]
    med = median_or_na([int(round(x)) for x in diffs])
    mean = mean_or_na(diffs)

    lines = [
        f"- N_mencoes_bb_com_data: {len(bb_dates)}",
        f"- N_intervalos: {len(diffs)}",
        f"- median(diff_em_dias): {('N/A' if med is None else f'{med:.1f}')}",
        f"- mean(diff_em_dias): {('N/A' if mean is None else f'{mean:.1f}')}",
    ]
    return title, definition, formula, ["\n".join(lines)]


def indicador_6(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Posts patrocinados (proxy is_collab)"
    definition = "Quantidade e share de posts patrocinados usando `is_collab=true` como proxy."
    formula = "N_pat = count(is_collab=true); Share_pat = N_pat / N_total."
    total = len(rows)
    n_pat = sum(1 for r in rows if r.is_collab)
    result = "\n".join([f"- N_pat: {n_pat}", f"- Share_pat: {fmt_pct(n_pat, total)}"])
    return title, definition, formula, [result]


def indicador_7(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Share do BB entre patrocinados"
    definition = "Share de menções BB dentro dos posts patrocinados (proxy)."
    formula = "N_pat_BB = count(is_collab=true AND is_bb=true); Share_BB_pat = N_pat_BB / N_pat."
    pat = [r for r in rows if r.is_collab]
    n_pat = len(pat)
    n_pat_bb = sum(1 for r in pat if r.is_bb_mention)
    result = "\n".join([f"- N_pat: {n_pat}", f"- N_pat_BB: {n_pat_bb}", f"- Share_BB_pat: {fmt_pct(n_pat_bb, n_pat)}"])
    return title, definition, formula, [result]


def indicador_8(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "BB orgânico vs patrocinado"
    definition = "Separação de menções BB em orgânicas (não patrocinadas) vs patrocinadas."
    formula = "N_BB_org = count(is_bb=true AND is_collab=false); %_BB_org_do_total_BB = N_BB_org / N_BB."
    bb = [r for r in rows if r.is_bb_mention]
    n_bb = len(bb)
    n_bb_org = sum(1 for r in bb if not r.is_collab)
    result = "\n".join([f"- N_BB: {n_bb}", f"- N_BB_org: {n_bb_org}", f"- %_BB_org_do_total_BB: {fmt_pct(n_bb_org, n_bb)}"])
    return title, definition, formula, [result]


def sponsored_brand_counts(rows: List[PostRow]) -> Tuple[int, Dict[str, int]]:
    pat = [r for r in rows if r.is_collab]
    n_pat = len(pat)
    counts: Dict[str, int] = {}
    for r in pat:
        handles = {m for m in r.mentions if m.startswith("@")}
        for h in handles:
            counts[h] = counts.get(h, 0) + 1
    return n_pat, counts


def indicador_9(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Ranking de marcas em posts patrocinados (Top 10)"
    definition = "Top 10 handles (@...) mais mencionados em posts patrocinados (proxy), contando ocorrência por post."
    formula = "Dentro de is_collab=true: para cada post, deduplicar mentions e contar posts por handle; share = posts_handle / N_pat."
    n_pat, counts = sponsored_brand_counts(rows)
    top10 = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    table_rows = [[h, str(c), (fmt_pct(c, n_pat) if n_pat else "N/A")] for h, c in top10]
    result = md_table(["handle", "posts", "share_dentro_patrocinados"], table_rows) if top10 else "N/A (sem posts patrocinados ou sem mentions)"
    return title, definition, formula, [result]


def indicador_10(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Posição do BB no ranking + razão vs líder"
    definition = "Mostra a posição do @bancodobrasil no ranking de marcas patrocinadas e a razão vs líder."
    formula = "rank(@bancodobrasil) no top; leader = 1º; razão = bb_posts / leader_posts."

    n_pat, counts = sponsored_brand_counts(rows)
    ranking = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    leader_handle, leader_posts = (ranking[0] if ranking else ("N/A", 0))

    bb_posts = counts.get("@bancodobrasil", 0)
    bb_rank = next((i + 1 for i, (h, _) in enumerate(ranking) if h == "@bancodobrasil"), None)
    ratio = safe_div(bb_posts, leader_posts) if leader_posts else None

    lines = [
        f"- N_pat: {n_pat}",
        f"- leader_handle: {leader_handle}",
        f"- leader_posts: {leader_posts}",
        f"- bb_posts (@bancodobrasil): {bb_posts}",
        f"- bb_rank: {('N/A' if bb_rank is None else bb_rank)}",
        f"- razão (bb_posts / leader_posts): {('N/A' if ratio is None else f'{ratio:.3f}')}",
    ]
    return title, definition, formula, ["\n".join(lines)]


def indicador_11(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Concentração de patrocínios"
    definition = "Concentração de marcas no universo patrocinado (proxy) via shares Top1/Top3/Top5."
    formula = "Share_TopK = (somatório posts dos K handles) / N_pat."

    n_pat, counts = sponsored_brand_counts(rows)
    ranking = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def sum_top(k: int) -> int:
        return sum(c for _, c in ranking[:k])

    top1 = sum_top(1)
    top3 = sum_top(3)
    top5 = sum_top(5)

    lines = [
        f"- N_pat: {n_pat}",
        f"- Share_Top1: {fmt_pct(top1, n_pat)}",
        f"- Share_Top3: {fmt_pct(top3, n_pat)}",
        f"- Share_Top5: {fmt_pct(top5, n_pat)}",
    ]
    obs = [
        "Observação: como uma publicação pode mencionar múltiplos handles, a soma dos TopK pode exceder 100% (proxy por menções)."
    ]
    return title, definition, formula, ["\n".join(lines)], obs[:1]


def indicador_12(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Mix de formato: reels vs não-reels"
    definition = "Proporção de reels no total e em recortes (BB, patrocinados, BB patrocinado)."
    formula = "Percentuais de media_type=reel em cada subconjunto."

    total = len(rows)
    bb = [r for r in rows if r.is_bb_mention]
    pat = [r for r in rows if r.is_collab]
    bb_pat = [r for r in rows if r.is_bb_mention and r.is_collab]

    reels_total = sum(1 for r in rows if r.media_type == "reel")
    reels_bb = sum(1 for r in bb if r.media_type == "reel")
    reels_pat = sum(1 for r in pat if r.media_type == "reel")
    reels_bb_pat = sum(1 for r in bb_pat if r.media_type == "reel")

    lines = [
        f"- % reels no total: {fmt_pct(reels_total, total)}",
        f"- % reels no BB: {fmt_pct(reels_bb, len(bb))}",
        f"- % reels nos patrocinados: {fmt_pct(reels_pat, len(pat))}",
        f"- % reels no BB patrocinado: {fmt_pct(reels_bb_pat, len(bb_pat))}",
    ]
    return title, definition, formula, ["\n".join(lines)]


def indicador_13(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Share do BB em reels patrocinados"
    definition = "Share de BB dentro do recorte (is_collab=true AND media_type=reel)."
    formula = "count(is_collab AND media_type=reel AND is_bb) / count(is_collab AND media_type=reel)."
    reels_pat = [r for r in rows if r.is_collab and r.media_type == "reel"]
    denom = len(reels_pat)
    num = sum(1 for r in reels_pat if r.is_bb_mention)
    result = f"- Share_BB_reels_patrocinados: {fmt_pct(num, denom)}"
    return title, definition, formula, [result]


def indicador_14(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Qualidade de tagging do BB"
    definition = "Percentual dos posts BB cujo campo mentions contém @bancodobrasil."
    formula = "% = count(is_bb=true AND '@bancodobrasil' em mentions) / N_BB."
    bb = [r for r in rows if r.is_bb_mention]
    denom = len(bb)
    num = sum(1 for r in bb if "@bancodobrasil" in set(r.mentions))
    result = f"- % posts BB com @bancodobrasil em mentions: {fmt_pct(num, denom)}"
    return title, definition, formula, [result]


def indicador_15(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Exclusividade do BB em posts patrocinados"
    definition = "Dentro de (is_bb AND is_collab), mede quando o BB é o único handle de marca mencionado (proxy)."
    target_handle = resolve_target_handle(rows)
    target_label = f"@{target_handle}" if target_handle else "@owner_alvo"
    formula = (
        f"BB solo: apos remover {target_label} e coauthors do set de mentions, o set resultante == {{@bancodobrasil}}. "
        "% = BB_solo / N(is_bb AND is_collab)."
    )

    subset = [r for r in rows if r.is_bb_mention and r.is_collab]
    denom = len(subset)
    solo = 0

    for r in subset:
        mentions = {m for m in r.mentions if m.startswith("@")}
        remove = {target_label} if target_handle else set()
        for c in r.coauthors:
            if c:
                remove.add("@" + c.lstrip("@"))
        mentions -= remove
        if mentions == {"@bancodobrasil"}:
            solo += 1

    lines = [f"- N(is_bb AND is_collab): {denom}", f"- BB_solo: {solo}", f"- % BB_solo: {fmt_pct(solo, denom)}"]
    return title, definition, formula, ["\n".join(lines)]


def indicador_16(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Performance mediana (likes/comments) em patrocinados: BB vs não-BB"
    definition = "Comparação de mediana de likes/comments dentro de posts patrocinados (proxy), entre BB e não-BB."
    formula = "Dentro de is_collab=true: mediana(likes/comments) para BB e para não-BB (ignorando vazios)."

    pat = [r for r in rows if r.is_collab]
    bb = [r for r in pat if r.is_bb_mention]
    non = [r for r in pat if not r.is_bb_mention]

    bb_likes = [r.likes for r in bb if r.likes is not None]
    bb_comments = [r.comments for r in bb if r.comments is not None]
    non_likes = [r.likes for r in non if r.likes is not None]
    non_comments = [r.comments for r in non if r.comments is not None]

    def fmt_med(values: List[Optional[int]]) -> str:
        ints = [v for v in values if v is not None]
        if not ints:
            return "N/A"
        return f"{statistics.median(ints):.1f} (n={len(ints)})"

    lines = [
        f"- Patrocinados (N_pat): {len(pat)}",
        f"- BB patrocinados (N_pat_BB): {len(bb)}",
        f"- Mediana likes (BB): {fmt_med(bb_likes)}",
        f"- Mediana comments (BB): {fmt_med(bb_comments)}",
        f"- Mediana likes (não-BB): {fmt_med(non_likes)}",
        f"- Mediana comments (não-BB): {fmt_med(non_comments)}",
    ]
    return title, definition, formula, ["\n".join(lines)]


def indicador_17(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Top 5 entregas do BB por likes"
    definition = "Top 5 posts com `is_bb=true` ordenados por likes (desc)."
    formula = "Selecionar is_bb=true com likes preenchidos; ordenar por likes desc; pegar top 5."

    bb = [r for r in rows if r.is_bb_mention and r.likes is not None]
    bb_sorted = sorted(bb, key=lambda r: (-int(r.likes or 0), fmt_dt(r.dt_utc), r.post_url))[:5]

    if not bb_sorted:
        return title, definition, formula, ["N/A (sem posts BB com likes preenchidos)"]

    table_rows = []
    for r in bb_sorted:
        dt_str = r.raw_datetime.strip() or r.raw_date.strip() or fmt_date(r.dt_utc)
        table_rows.append(
            [
                dt_str,
                r.post_url,
                str(r.likes or ""),
                str(r.comments or ""),
                r.owner_username or "",
                r.media_type or "",
                "true" if r.is_collab else "false",
            ]
        )

    result = md_table(["datetime/date", "post_url", "likes", "comments", "owner", "media_type", "is_collab"], table_rows)
    return title, definition, formula, [result]


def indicador_18(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Distribuição por owner e BB"
    target_handle = resolve_target_handle(rows)
    target_owner = target_handle or "owner_alvo"
    definition = f"Distribuicao do volume por owner ({target_owner} vs outros) e participacao de BB por owner."
    formula = f"% owner={target_owner} = count(owner={target_owner}) / N_total; BB por owner = count_bb_owner e share dentro do BB."

    total = len(rows)
    if target_handle:
        owner_target = sum(1 for r in rows if (r.owner_username or "") == target_handle)
    else:
        owner_target = sum(1 for r in rows if r.is_owner_profile)
    other = total - owner_target

    bb = [r for r in rows if r.is_bb_mention]
    n_bb = len(bb)
    bb_by_owner: Dict[str, int] = {}
    for r in bb:
        o = r.owner_username or "(desconhecido)"
        bb_by_owner[o] = bb_by_owner.get(o, 0) + 1
    bb_sorted = sorted(bb_by_owner.items(), key=lambda kv: (-kv[1], kv[0]))
    table_rows = [[o, str(c), (fmt_pct(c, n_bb) if n_bb else "N/A")] for o, c in bb_sorted[:15]]

    lines = [
        f"- % posts owner={target_owner}: {fmt_pct(owner_target, total)}",
        f"- % posts outros owners: {fmt_pct(other, total)}",
        "",
        "BB por owner (top 15):",
        md_table(["owner_username", "bb_posts", "share_dentro_bb"], table_rows) if table_rows else "N/A",
    ]
    return title, definition, formula, ["\n".join(lines).rstrip()]


def indicador_19(rows: List[PostRow]) -> Tuple[str, str, str, List[str]]:
    title = "Limitações da base (automático)"
    definition = "Resumo automático de limitações/cobertura dos campos."
    formula = "Percentuais de cobertura (plays/views, caption, mentions/hashtags) e notas fixas de proxy."

    total = len(rows)
    plays_cov = sum(1 for r in rows if r.plays_or_views is not None)
    views_cov = sum(1 for r in rows if r.views is not None)
    caption_empty = sum(1 for r in rows if not (r.caption or "").strip())
    mentions_empty = sum(1 for r in rows if not r.mentions)
    hashtags_empty = sum(1 for r in rows if not r.hashtags)

    bullets = [
        f"- Cobertura plays_or_views: {fmt_pct(plays_cov, total)}",
        f"- Cobertura views (coluna views): {fmt_pct(views_cov, total)}",
        f"- % captions vazias: {fmt_pct(caption_empty, total)}",
        f"- % posts sem mentions: {fmt_pct(mentions_empty, total)}",
        f"- % posts sem hashtags: {fmt_pct(hashtags_empty, total)}",
        "- Nota: `is_collab=true` é tratado como proxy de post patrocinado (pode ter falsos positivos/negativos).",
        "- Nota: contagens de marcas usam `mentions` (@handles) como proxy; ausência de mentions reduz a cobertura.",
    ]
    return title, definition, formula, ["\n".join(bullets)]


INDICATORS = {
    0: indicador_0,
    1: indicador_1,
    2: indicador_2,
    3: indicador_3,
    4: indicador_4,
    5: indicador_5,
    6: indicador_6,
    7: indicador_7,
    8: indicador_8,
    9: indicador_9,
    10: indicador_10,
    11: indicador_11,
    12: indicador_12,
    13: indicador_13,
    14: indicador_14,
    15: indicador_15,
    16: indicador_16,
    17: indicador_17,
    18: indicador_18,
    19: indicador_19,
}


def indicator_exists(md_text: str, n: int) -> bool:
    return re.search(rf"^##\s+Indicador\s+{re.escape(str(n))}\b", md_text, flags=re.MULTILINE) is not None


def append_indicator(md_path: str, n: int, title: str, definition: str, formula: str, results: List[str], obs: Optional[List[str]]) -> None:
    lines: List[str] = []
    lines.append(f"## Indicador {n} — {title}")
    lines.append(f"- Definição: {definition}")
    lines.append(f"- Fórmula: {formula}")
    lines.append("- Resultado (com números):")
    for chunk in results:
        for l in chunk.splitlines():
            if l.strip():
                lines.append(f"  {l}")
            else:
                lines.append("")
    if obs:
        lines.append("- Observações:")
        for o in obs[:2]:
            lines.append(f"  - {o}")
    section = "\n".join(lines).rstrip() + "\n"

    path = Path(md_path)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        if path.stat().st_size > 0:
            f.write("\n")
        f.write(section)


def parse_indicator_args(values: Sequence[str]) -> List[int]:
    out: List[int] = []
    for raw in values:
        for part in str(raw).split(","):
            value = part.strip()
            if not value:
                continue
            try:
                out.append(int(value))
            except ValueError as exc:
                raise SystemExit(f"Indicador invalido: {value}") from exc
    return out


def collect_indicator_values(
    rows: List[PostRow], indicators: Sequence[int], handle: Optional[str]
) -> Tuple["OrderedDict[str, str]", List[Tuple[str, int, int]]]:
    selected = set(indicators)
    values: "OrderedDict[str, str]" = OrderedDict()
    values["handler"] = handle or ""
    monthly_rows: List[Tuple[str, int, int]] = []

    total = len(rows)
    dates = [r.dt_utc for r in rows if r.dt_utc is not None]
    min_dt = min(dates) if dates else None
    max_dt = max(dates) if dates else None

    bb_rows = [r for r in rows if r.is_bb_mention]
    pat_rows = [r for r in rows if r.is_collab]
    bb_pat_rows = [r for r in rows if r.is_bb_mention and r.is_collab]

    if 0 in selected:
        likes_filled = sum(1 for r in rows if r.likes is not None)
        comments_filled = sum(1 for r in rows if r.comments is not None)
        mentions_filled = sum(1 for r in rows if len(r.mentions) > 0)
        plays_filled = sum(1 for r in rows if r.plays_or_views is not None)

        set_value(values, "posts_total", total)
        set_value(values, "date_min", fmt_date(min_dt))
        set_value(values, "date_max", fmt_date(max_dt))
        set_value(values, "likes_filled_pct", fmt_pct(likes_filled, total))
        set_value(values, "comments_filled_pct", fmt_pct(comments_filled, total))
        set_value(values, "mentions_filled_pct", fmt_pct(mentions_filled, total))
        set_value(values, "plays_or_views_filled_pct", fmt_pct(plays_filled, total))

        owners = [r.owner_username or "(desconhecido)" for r in rows]
        top_owners = top_n_counter(owners, 5)
        for idx in range(5):
            if idx < len(top_owners):
                owner, count = top_owners[idx]
                set_value(values, f"top_owner_{idx + 1}", owner)
                set_value(values, f"top_owner_{idx + 1}_posts", count)
            else:
                set_value(values, f"top_owner_{idx + 1}", "")
                set_value(values, f"top_owner_{idx + 1}_posts", "")

        set_value(values, "generated_at_utc", fmt_dt(datetime.now(timezone.utc)))

    if 1 in selected:
        set_value(values, "posts_total", total)

    if 2 in selected:
        n_bb = len(bb_rows)
        set_value(values, "bb_posts_total", n_bb)
        set_value(values, "bb_share_total", fmt_pct(n_bb, total))

    if 3 in selected:
        bb_dates = [r.dt_utc for r in rows if r.is_bb_mention and r.dt_utc is not None]
        last_bb = max(bb_dates) if bb_dates else None
        ref_candidates = [r.scraped_at_utc for r in rows if r.scraped_at_utc is not None]
        ref_dt = max(ref_candidates) if ref_candidates else datetime.now(timezone.utc)

        if last_bb is None:
            set_value(values, "bb_last_dt", "N/A")
            set_value(values, "bb_ref_dt", fmt_dt(ref_dt))
            set_value(values, "bb_days_since_last", "N/A")
        else:
            set_value(values, "bb_last_dt", fmt_dt(last_bb))
            set_value(values, "bb_ref_dt", fmt_dt(ref_dt))
            set_value(values, "bb_days_since_last", (ref_dt - last_bb).days)

    if 4 in selected:
        month_total: Dict[str, int] = {}
        month_bb: Dict[str, int] = {}
        for r in rows:
            if r.dt_utc is None:
                continue
            mk = month_key(r.dt_utc)
            month_total[mk] = month_total.get(mk, 0) + 1
            if r.is_bb_mention:
                month_bb[mk] = month_bb.get(mk, 0) + 1
        for mk in sorted(month_total.keys()):
            monthly_rows.append((mk, month_bb.get(mk, 0), month_total.get(mk, 0)))

    if 5 in selected:
        bb_dates = sorted([r.dt_utc for r in rows if r.is_bb_mention and r.dt_utc is not None])
        if len(bb_dates) < 2:
            set_value(values, "bb_mentions_with_date", len(bb_dates))
            set_value(values, "bb_intervals_count", 0)
            set_value(values, "bb_interval_median_days", "N/A")
            set_value(values, "bb_interval_mean_days", "N/A")
        else:
            diffs = [(bb_dates[i] - bb_dates[i - 1]).total_seconds() / 86400.0 for i in range(1, len(bb_dates))]
            med = median_or_na([int(round(x)) for x in diffs])
            mean = mean_or_na(diffs)
            set_value(values, "bb_mentions_with_date", len(bb_dates))
            set_value(values, "bb_intervals_count", len(diffs))
            set_value(values, "bb_interval_median_days", fmt_float(med))
            set_value(values, "bb_interval_mean_days", fmt_float(mean))

    if 6 in selected:
        n_pat = len(pat_rows)
        set_value(values, "sponsored_posts_total", n_pat)
        set_value(values, "sponsored_share_total", fmt_pct(n_pat, total))

    if 7 in selected:
        n_pat = len(pat_rows)
        n_pat_bb = sum(1 for r in pat_rows if r.is_bb_mention)
        set_value(values, "sponsored_posts_total", n_pat)
        set_value(values, "sponsored_bb_posts", n_pat_bb)
        set_value(values, "sponsored_bb_share", fmt_pct(n_pat_bb, n_pat))

    if 8 in selected:
        n_bb = len(bb_rows)
        n_bb_org = sum(1 for r in bb_rows if not r.is_collab)
        set_value(values, "bb_posts_total", n_bb)
        set_value(values, "bb_posts_org", n_bb_org)
        set_value(values, "bb_org_share_of_bb", fmt_pct(n_bb_org, n_bb))

    need_brand_counts = bool(selected.intersection({9, 10, 11}))
    brand_counts: Dict[str, int] = {}
    brand_ranking: List[Tuple[str, int]] = []
    n_pat_brands = 0
    if need_brand_counts:
        n_pat_brands, brand_counts = sponsored_brand_counts(rows)
        brand_ranking = sorted(brand_counts.items(), key=lambda kv: (-kv[1], kv[0]))

    if 9 in selected:
        top10 = brand_ranking[:10]
        for idx in range(10):
            if idx < len(top10):
                handle_name, count = top10[idx]
                set_value(values, f"sponsored_brand_top{idx + 1}_handle", handle_name)
                set_value(values, f"sponsored_brand_top{idx + 1}_posts", count)
                set_value(values, f"sponsored_brand_top{idx + 1}_share", fmt_pct(count, n_pat_brands))
            else:
                set_value(values, f"sponsored_brand_top{idx + 1}_handle", "")
                set_value(values, f"sponsored_brand_top{idx + 1}_posts", "")
                set_value(values, f"sponsored_brand_top{idx + 1}_share", "")

    if 10 in selected:
        leader_handle, leader_posts = (brand_ranking[0] if brand_ranking else ("", 0))
        bb_posts = brand_counts.get("@bancodobrasil", 0)
        bb_rank = next((i + 1 for i, (h, _) in enumerate(brand_ranking) if h == "@bancodobrasil"), None)
        ratio = safe_div(bb_posts, leader_posts) if leader_posts else None

        set_value(values, "sponsored_posts_total", n_pat_brands)
        set_value(values, "sponsored_brand_leader_handle", leader_handle)
        set_value(values, "sponsored_brand_leader_posts", leader_posts)
        set_value(values, "bb_brand_posts_in_sponsored", bb_posts)
        set_value(values, "bb_brand_rank_in_sponsored", ("N/A" if bb_rank is None else bb_rank))
        set_value(values, "bb_vs_leader_ratio", fmt_float(ratio, 3))

    if 11 in selected:
        top1 = sum(c for _, c in brand_ranking[:1])
        top3 = sum(c for _, c in brand_ranking[:3])
        top5 = sum(c for _, c in brand_ranking[:5])
        set_value(values, "sponsored_posts_total", n_pat_brands)
        set_value(values, "sponsored_brand_share_top1", fmt_pct(top1, n_pat_brands))
        set_value(values, "sponsored_brand_share_top3", fmt_pct(top3, n_pat_brands))
        set_value(values, "sponsored_brand_share_top5", fmt_pct(top5, n_pat_brands))

    if 12 in selected:
        reels_total = sum(1 for r in rows if r.media_type == "reel")
        reels_bb = sum(1 for r in bb_rows if r.media_type == "reel")
        reels_pat = sum(1 for r in pat_rows if r.media_type == "reel")
        reels_bb_pat = sum(1 for r in bb_pat_rows if r.media_type == "reel")

        set_value(values, "reels_share_total", fmt_pct(reels_total, total))
        set_value(values, "reels_share_bb", fmt_pct(reels_bb, len(bb_rows)))
        set_value(values, "reels_share_sponsored", fmt_pct(reels_pat, len(pat_rows)))
        set_value(values, "reels_share_bb_sponsored", fmt_pct(reels_bb_pat, len(bb_pat_rows)))

    if 13 in selected:
        reels_pat = [r for r in pat_rows if r.media_type == "reel"]
        denom = len(reels_pat)
        num = sum(1 for r in reels_pat if r.is_bb_mention)
        set_value(values, "bb_share_in_sponsored_reels", fmt_pct(num, denom))

    if 14 in selected:
        denom = len(bb_rows)
        num = sum(1 for r in bb_rows if "@bancodobrasil" in set(r.mentions))
        set_value(values, "bb_posts_with_official_tag_share", fmt_pct(num, denom))

    if 15 in selected:
        target_handle = resolve_target_handle(rows)
        target_label = f"@{target_handle}" if target_handle else None
        subset = [r for r in rows if r.is_bb_mention and r.is_collab]
        denom = len(subset)
        solo = 0

        for r in subset:
            mentions = {m for m in r.mentions if m.startswith("@")}
            remove: set[str] = set()
            if target_label:
                remove.add(target_label)
            for c in r.coauthors:
                if c:
                    remove.add("@" + c.lstrip("@"))
            mentions -= remove
            if mentions == {"@bancodobrasil"}:
                solo += 1

        set_value(values, "bb_sponsored_posts_total", denom)
        set_value(values, "bb_sponsored_solo_count", solo)
        set_value(values, "bb_sponsored_solo_share", fmt_pct(solo, denom))

    if 16 in selected:
        bb_pat = [r for r in pat_rows if r.is_bb_mention]
        non_bb_pat = [r for r in pat_rows if not r.is_bb_mention]

        bb_likes = [r.likes for r in bb_pat if r.likes is not None]
        bb_comments = [r.comments for r in bb_pat if r.comments is not None]
        non_likes = [r.likes for r in non_bb_pat if r.likes is not None]
        non_comments = [r.comments for r in non_bb_pat if r.comments is not None]

        bb_median_likes = statistics.median(bb_likes) if bb_likes else None
        bb_median_comments = statistics.median(bb_comments) if bb_comments else None
        non_median_likes = statistics.median(non_likes) if non_likes else None
        non_median_comments = statistics.median(non_comments) if non_comments else None

        set_value(values, "sponsored_posts_total", len(pat_rows))
        set_value(values, "sponsored_bb_posts_total", len(bb_pat))
        set_value(values, "sponsored_bb_median_likes", fmt_float(bb_median_likes))
        set_value(values, "sponsored_bb_median_comments", fmt_float(bb_median_comments))
        set_value(values, "sponsored_nonbb_median_likes", fmt_float(non_median_likes))
        set_value(values, "sponsored_nonbb_median_comments", fmt_float(non_median_comments))

    if 17 in selected:
        bb_with_likes = [r for r in rows if r.is_bb_mention and r.likes is not None]
        bb_sorted = sorted(bb_with_likes, key=lambda r: (-int(r.likes or 0), fmt_dt(r.dt_utc), r.post_url))[:5]
        for idx in range(5):
            url = bb_sorted[idx].post_url if idx < len(bb_sorted) else ""
            set_value(values, f"bb_top_post_url_{idx + 1}", url)

    if 18 in selected:
        target_handle = resolve_target_handle(rows)
        set_value(values, "owner_target_handle", target_handle or "")
        if target_handle:
            owner_target = sum(1 for r in rows if (r.owner_username or "") == target_handle)
        else:
            owner_target = sum(1 for r in rows if r.is_owner_profile)
        other = total - owner_target

        set_value(values, "owner_target_share_total", fmt_pct(owner_target, total))
        set_value(values, "owner_other_share_total", fmt_pct(other, total))

        bb_by_owner: Dict[str, int] = {}
        for r in bb_rows:
            o = r.owner_username or "(desconhecido)"
            bb_by_owner[o] = bb_by_owner.get(o, 0) + 1
        bb_sorted = sorted(bb_by_owner.items(), key=lambda kv: (-kv[1], kv[0]))
        for idx in range(15):
            if idx < len(bb_sorted):
                owner, count = bb_sorted[idx]
                set_value(values, f"bb_owner_top{idx + 1}", owner)
                set_value(values, f"bb_owner_top{idx + 1}_posts", count)
                set_value(values, f"bb_owner_top{idx + 1}_share", fmt_pct(count, len(bb_rows)))
            else:
                set_value(values, f"bb_owner_top{idx + 1}", "")
                set_value(values, f"bb_owner_top{idx + 1}_posts", "")
                set_value(values, f"bb_owner_top{idx + 1}_share", "")

    if 19 in selected:
        plays_cov = sum(1 for r in rows if r.plays_or_views is not None)
        views_cov = sum(1 for r in rows if r.views is not None)
        caption_empty = sum(1 for r in rows if not (r.caption or "").strip())
        mentions_empty = sum(1 for r in rows if not r.mentions)
        hashtags_empty = sum(1 for r in rows if not r.hashtags)

        set_value(values, "plays_or_views_coverage", fmt_pct(plays_cov, total))
        set_value(values, "views_coverage", fmt_pct(views_cov, total))
        set_value(values, "captions_empty_pct", fmt_pct(caption_empty, total))
        set_value(values, "mentions_empty_pct", fmt_pct(mentions_empty, total))
        set_value(values, "hashtags_empty_pct", fmt_pct(hashtags_empty, total))

    return values, monthly_rows


def write_indicators_csv(path: str, values: "OrderedDict[str, str]") -> None:
    out_path = Path(path)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(list(values.keys()))
        writer.writerow(list(values.values()))


def write_monthly_bb_csv(path: str, handle: Optional[str], monthly_rows: Sequence[Tuple[str, int, int]]) -> None:
    out_path = Path(path)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["handler", "month", "posts_bb", "posts_total"])
        for month, posts_bb, posts_total in monthly_rows:
            writer.writerow([handle or "", month, posts_bb, posts_total])


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Gera indicadores em CSV (Instagram BB).")
    parser.add_argument(
        "--indicator",
        action="append",
        default=[],
        help="Numero do indicador (0..19). Opcional, pode repetir ou usar virgula.",
    )
    parser.add_argument("--csv", dest="csv_path", default=None, help="Caminho do CSV (separador ';').")
    parser.add_argument("--handle", "--profile", dest="handle", default=None, help="Handle do perfil (ex: tainahinckel).")
    parser.add_argument("--out", dest="out_path", default=None, help="Caminho do CSV de saida.")
    args = parser.parse_args(argv)

    selected = parse_indicator_args(args.indicator)
    if not selected:
        selected = sorted(INDICATORS.keys())

    invalid = [n for n in selected if n not in INDICATORS]
    if invalid:
        raise SystemExit(f"Indicador invalido: {invalid}. Validos: {sorted(INDICATORS.keys())}")

    handle = normalize_handle(args.handle)
    csv_path, detected_handle = resolve_csv_path(args.csv_path, handle)
    handle = handle or detected_handle
    global TARGET_HANDLE
    TARGET_HANDLE = handle
    if args.out_path:
        out_path = str(resolve_path(args.out_path))
    else:
        out_path = str(ROOT / default_out_path(handle))

    if not Path(csv_path).exists():
        raise SystemExit(f"CSV nao encontrado: {csv_path}")

    rows = read_rows(csv_path)
    values, monthly_rows = collect_indicator_values(rows, sorted(selected), handle)
    write_indicators_csv(out_path, values)

    monthly_path = None
    if 4 in selected:
        monthly_path = resolve_monthly_out_path(out_path, handle)
        write_monthly_bb_csv(monthly_path, handle, monthly_rows)

    print(f"CSV usado: {os.path.abspath(csv_path)}")
    print(f"Saida CSV: {os.path.abspath(out_path)}")
    if monthly_path:
        print(f"Saida mensal: {os.path.abspath(monthly_path)}")
    print(f"Colunas: {len(values)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
