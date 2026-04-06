#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pandas nao encontrado. Instale com: pip install pandas openpyxl") from exc


# =========================
# CONFIGURACAO BB (EDITAVEL)
# =========================
BB_ALIASES = [
    "@bancodobrasil",
    "banco do brasil",
    "#bancodobrasil",
]

BB_CAMPAIGN_ALIASES = [
    "#tamojuntobb",
    "bbnosesportes",
    "#bbsquad",
    "#bb_squad",
    "bb_seguros",
    "#bbseguros",
    "#squad_bb",
    "#squadbb",
    "#festivaltamojuntobb",
    "#BBDW2025",
    "#BBDW2026",
    "#BBDW2027",
    "#BBDW2028",
    
    "#BBDW2025",    
    "#bbnoskate"
    "@festivaltamojuntobb",
]


TRUE_VALUES = {"true", "1", "yes", "y", "sim", "s", "verdadeiro"}
FALSE_VALUES = {"false", "0", "no", "n", "nao", "falso"}


def resolve_root() -> Path:
    env = os.getenv("PIPELINE_ROOT") or os.getenv("MCP_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parent


ROOT = resolve_root()
KNOWN_HANDLES: Optional[List[str]] = None


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


KEYWORDS_BY_FIELD = {
    "date": [
        "datetime",
        "date",
        "published",
        "created",
        "post_time",
        "post_date",
        "timestamp",
        "time",
        "data",
        "hora",
    ],
    "url": ["post_url", "permalink", "url", "link"],
    "text": ["caption", "legenda", "description", "text", "conteudo", "content", "message", "post_text"],
    "mentions": ["mentions", "mention", "tagged_accounts", "tagged_users", "marcacoes", "marcados", "tagged", "people_tags"],
    "hashtags": ["hashtags", "hashtag", "tags", "hash_tags", "hashes"],
    "brands": ["brand", "brands", "marca", "marcas", "sponsor", "patrocinador"],
    "sponsored": ["is_collab", "sponsored", "patrocin", "branded", "parceria", "paid", "partnership", "publi"],
    "paid_partnership": ["paid_partnership", "paidpartnership", "branded_content", "brandedcontent", "parceria_paga"],
    "owner": ["owner_username", "owner", "author", "username", "account", "perfil", "creator", "user", "handle", "account_name"],
    "media_type": ["media_type", "type", "formato", "media", "post_type", "tipo", "content_type"],
    "likes": ["likes", "like_count", "curtidas", "curtida", "favorite", "favorites", "favorite_count"],
    "comments": ["comments", "comment_count", "comentarios", "comentario", "respostas"],
    "views": ["views", "view_count", "plays", "play_count", "visualizacoes", "views_count", "plays_or_views", "video_views"],
}

EXCLUDE_BY_FIELD = {
    "date": ["scraped", "coleta", "crawl", "updated", "ingestion"],
}


@dataclass
class ColumnMap:
    date: Optional[str]
    url: Optional[str]
    text: Optional[str]
    mentions: Optional[str]
    hashtags: Optional[str]
    brands: Optional[str]
    sponsored: Optional[str]
    paid_partnership: Optional[str]
    owner: Optional[str]
    media_type: Optional[str]
    likes: Optional[str]
    comments: Optional[str]
    views: Optional[str]


def normalize_col_name(value: str) -> str:
    raw = value.strip().lower()
    raw = unicodedata.normalize("NFKD", raw)
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    return raw.strip("_")


def build_column_maps(columns: Sequence[str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    original_to_normalized: Dict[str, str] = {}
    normalized_to_original: Dict[str, str] = {}
    for col in columns:
        col_str = str(col)
        normalized = normalize_col_name(col_str)
        original_to_normalized[col_str] = normalized
        if normalized not in normalized_to_original:
            normalized_to_original[normalized] = col_str
    return original_to_normalized, normalized_to_original


def pick_column(
    columns: Sequence[str],
    keywords: Sequence[str],
    exclude: Optional[Sequence[str]] = None,
    normalized_map: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    best: Optional[str] = None
    best_rank: Optional[Tuple[int, int, int, int, int, str]] = None
    for col in columns:
        key = normalized_map.get(col) if normalized_map else normalize_col_name(col)
        exact_hits = 0
        contains_hits = 0
        for k in keywords:
            if key == k:
                exact_hits += 1
            elif k in key:
                contains_hits += 1
        if exact_hits + contains_hits == 0:
            continue
        score = exact_hits * 3 + contains_hits
        if exclude:
            score -= 2 * sum(1 for k in exclude if k in key)
        if score <= 0:
            continue
        has_exact = 1 if exact_hits > 0 else 0
        rank = (has_exact, score, exact_hits, contains_hits, -len(key), key)
        if best_rank is None or rank > best_rank:
            best_rank = rank
            best = col
    return best


def detect_columns(df: "pd.DataFrame") -> ColumnMap:
    cols = [str(c) for c in df.columns]
    original_to_normalized, _ = build_column_maps(cols)
    return ColumnMap(
        date=pick_column(
            cols,
            KEYWORDS_BY_FIELD["date"],
            EXCLUDE_BY_FIELD.get("date"),
            original_to_normalized,
        ),
        url=pick_column(cols, KEYWORDS_BY_FIELD["url"], normalized_map=original_to_normalized),
        text=pick_column(cols, KEYWORDS_BY_FIELD["text"], normalized_map=original_to_normalized),
        mentions=pick_column(cols, KEYWORDS_BY_FIELD["mentions"], normalized_map=original_to_normalized),
        hashtags=pick_column(cols, KEYWORDS_BY_FIELD["hashtags"], normalized_map=original_to_normalized),
        brands=pick_column(cols, KEYWORDS_BY_FIELD["brands"], normalized_map=original_to_normalized),
        sponsored=pick_column(cols, KEYWORDS_BY_FIELD["sponsored"], normalized_map=original_to_normalized),
        paid_partnership=pick_column(cols, KEYWORDS_BY_FIELD["paid_partnership"], normalized_map=original_to_normalized),
        owner=pick_column(cols, KEYWORDS_BY_FIELD["owner"], normalized_map=original_to_normalized),
        media_type=pick_column(cols, KEYWORDS_BY_FIELD["media_type"], normalized_map=original_to_normalized),
        likes=pick_column(cols, KEYWORDS_BY_FIELD["likes"], normalized_map=original_to_normalized),
        comments=pick_column(cols, KEYWORDS_BY_FIELD["comments"], normalized_map=original_to_normalized),
        views=pick_column(cols, KEYWORDS_BY_FIELD["views"], normalized_map=original_to_normalized),
    )


def sniff_delimiter(path: Path) -> str:
    try:
        line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    except Exception:
        return ","
    candidates = {",": line.count(","), ";": line.count(";"), "\t": line.count("\t")}
    best = max(candidates.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else ","


def read_input(path: Path) -> "pd.DataFrame":
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(path, dtype=str)
        except Exception as exc:
            raise SystemExit(f"Falha ao ler XLSX: {path}") from exc
    if suffix != ".csv":
        raise SystemExit(f"Extensao invalida: {suffix or '(sem extensao)'}. Use .csv ou .xlsx.")

    sep = sniff_delimiter(path)
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return pd.read_csv(path, sep=sep, dtype=str, encoding=encoding)
        except Exception:
            continue
    return pd.read_csv(path, sep=None, engine="python", dtype=str)


def parse_bool(value: Any) -> Optional[bool]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    return None


def parse_number(value: Any) -> Optional[int]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    raw = raw.replace("k", "000").replace(".", "").replace(",", "")
    clean = re.sub(r"[^\d-]", "", raw)
    if clean in {"", "-"}:
        return None
    try:
        return int(clean)
    except ValueError:
        return None


def parse_datetime(series: "pd.Series") -> "pd.Series":
    return pd.to_datetime(series, errors="coerce", utc=True)


def normalize_handle(value: Any) -> Optional[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.lstrip("@").strip()
    if "instagram.com" in text:
        m = re.search(r"instagram\.com/([^/?#]+)/?", text)
        if m:
            text = m.group(1)
    text = text.strip().lower()
    return text or None


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
    match = re.match(r"instagram_posts_enriched_(.+)\.csv$", path.name, flags=re.IGNORECASE)
    if match:
        return normalize_handle(match.group(1))
    return handle_from_posts_filename(path, load_known_handles())


def parse_run_log_datetime(path: Path) -> Optional[datetime]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    if not lines:
        return None
    for line in lines[1:]:
        raw = line.split(";", 1)[0].strip()
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return None


def resolve_run_log_datetime(file_path: Path, handle: Optional[str], root: Optional[Path] = None) -> Optional[datetime]:
    if not handle:
        return None
    root_dir = root or ROOT
    candidates = [
        file_path.parent / f"run_{handle}.csv",
        root_dir / "data" / f"run_{handle}.csv",
        root_dir / f"run_{handle}.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            found = parse_run_log_datetime(candidate)
            if found:
                return found
    return None


def split_list(value: Any) -> List[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    if isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        raw = str(value).strip()
        if not raw:
            return []
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1]
        if "|" in raw:
            items = raw.split("|")
        elif ";" in raw:
            items = raw.split(";")
        elif "," in raw:
            items = raw.split(",")
        else:
            items = raw.split()
    out = []
    for item in items:
        s = str(item).strip()
        if s:
            out.append(s)
    return out


def unique_ordered(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


MENTION_RE = re.compile(r"@[a-z0-9._]+", re.IGNORECASE)
HASHTAG_RE = re.compile(r"#[a-z0-9._]+", re.IGNORECASE)


def extract_mentions(text: str) -> List[str]:
    if not text:
        return []
    return unique_ordered([m.lower() for m in MENTION_RE.findall(text)])


def extract_hashtags(text: str) -> List[str]:
    if not text:
        return []
    return unique_ordered([h.lower() for h in HASHTAG_RE.findall(text)])


def normalize_mentions(items: Iterable[str]) -> List[str]:
    out = []
    for raw in items:
        s = str(raw).strip().lower()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if not s.startswith("@"):
            s = "@" + s
        out.append(s)
    return unique_ordered(out)


def normalize_hashtags(items: Iterable[str]) -> List[str]:
    out = []
    for raw in items:
        s = str(raw).strip().lower()
        if not s:
            continue
        if not s.startswith("#"):
            s = "#" + s
        out.append(s)
    return unique_ordered(out)


def build_bb_aliases() -> List[str]:
    aliases = [a.strip().lower() for a in BB_ALIASES + BB_CAMPAIGN_ALIASES if a.strip()]
    return unique_ordered(aliases)


def analyze_bb_connection(
    text: str,
    mentions: List[str],
    hashtags: List[str],
    aliases: List[str],
) -> Tuple[bool, Optional[str]]:
    text_lower = (text or "").lower()
    mention_set = {m.lower() for m in mentions}
    hashtag_set = {h.lower() for h in hashtags}

    alias_mentions = [a for a in aliases if a.startswith("@")]
    alias_hashtags = [a for a in aliases if a.startswith("#")]
    alias_text = [a for a in aliases if not a.startswith("@") and not a.startswith("#")]

    found_mentions = {a for a in alias_mentions if a in mention_set}
    found_hashtags = {a for a in alias_hashtags if a in hashtag_set}
    found_text = {a for a in alias_text if a in text_lower}

    if re.search(r"\bbb\b", text_lower):
        if "banco" in text_lower or "brasil" in text_lower:
            found_text.add("bb")

    has_mention = len(found_mentions) > 0
    has_hashtag = len(found_hashtags) > 0
    has_text = len(found_text) > 0

    connection_type = None
    if has_mention and has_hashtag:
        connection_type = "mention-hashtag"
    elif has_hashtag:
        connection_type = "hashtag"
    elif has_mention or has_text:
        connection_type = "mention"

    is_bb = has_mention or has_hashtag or has_text
    return is_bb, connection_type


def is_bb_mention(text: str, mentions: List[str], hashtags: List[str], aliases: List[str]) -> bool:
    return analyze_bb_connection(text, mentions, hashtags, aliases)[0]


def build_post_features(data: pd.DataFrame, colmap: ColumnMap, aliases: List[str]) -> Dict[str, Any]:
    total_rows = int(len(data))
    text_series = data[colmap.text].fillna("").astype(str) if colmap.text else pd.Series([""] * total_rows)
    mentions_series = data[colmap.mentions] if colmap.mentions else pd.Series([None] * total_rows)
    hashtags_series = data[colmap.hashtags] if colmap.hashtags else pd.Series([None] * total_rows)
    brands_series = data[colmap.brands] if colmap.brands else pd.Series([None] * total_rows)
    owner_series = data[colmap.owner] if colmap.owner else pd.Series([None] * total_rows)
    owner_norm = [normalize_handle(v) for v in owner_series.tolist()]

    mentions_list: List[List[str]] = []
    hashtags_list: List[List[str]] = []
    brand_list: List[List[str]] = []

    for idx, text in enumerate(text_series.tolist()):
        base_mentions = normalize_mentions(split_list(mentions_series.iloc[idx]))
        brand_mentions = normalize_mentions(split_list(brands_series.iloc[idx]))
        text_mentions = extract_mentions(str(text))
        mentions = unique_ordered(base_mentions + brand_mentions + text_mentions)
        mentions_list.append(mentions)

        base_hashtags = normalize_hashtags(split_list(hashtags_series.iloc[idx]))
        text_hashtags = extract_hashtags(str(text))
        hashtags = unique_ordered(base_hashtags + text_hashtags)
        hashtags_list.append(hashtags)

        if brand_mentions:
            brands = brand_mentions
        else:
            brands = mentions
        owner = owner_norm[idx]
        if owner:
            brands = [m for m in brands if m.lstrip("@") != owner]
        brand_list.append(unique_ordered(brands))

    bb_analysis = [
        analyze_bb_connection(text, mentions_list[i], hashtags_list[i], aliases) for i, text in enumerate(text_series.tolist())
    ]
    is_bb_flags = [item[0] for item in bb_analysis]
    bb_connection_types = [item[1] for item in bb_analysis]
    bb_handle = "@bancodobrasil"
    bb_explicit_flags = [bb_handle in mentions_list[i] for i in range(total_rows)]

    return {
        "mentions_list": mentions_list,
        "hashtags_list": hashtags_list,
        "brand_list": brand_list,
        "owner_norm": owner_norm,
        "is_bb_flags": is_bb_flags,
        "bb_connection_types": bb_connection_types,
        "bb_explicit_flags": bb_explicit_flags,
    }


def share(num: Optional[int], den: Optional[int]) -> Optional[float]:
    if num is None or den is None or den <= 0:
        return None
    return round(100.0 * num / den, 1)


def fmt_int(value: Optional[int]) -> str:
    if value is None:
        return "N/A"
    return f"{value:,}".replace(",", ".")


def fmt_pct_value(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def fmt_date(dt: Optional[datetime]) -> Optional[str]:
    if not dt or (isinstance(dt, float) and math.isnan(dt)):
        return None
    return dt.strftime("%Y-%m-%d")


def fmt_days(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}".rstrip("0").rstrip(".")


def median(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    values = sorted(values)
    mid = len(values) // 2
    if len(values) % 2 == 1:
        return float(values[mid])
    return (values[mid - 1] + values[mid]) / 2.0


def mean(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return float(sum(values) / len(values))


def month_range(start: datetime, end: datetime) -> List[str]:
    if start > end:
        start, end = end, start
    months = []
    current = datetime(start.year, start.month, 1)
    end_month = datetime(end.year, end.month, 1)
    while current <= end_month:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
    return months


def explain_monthly(bb_by_month: Dict[str, int], month_list: List[str]) -> Tuple[Optional[str], List[str]]:
    if not month_list:
        return None, []
    counts = [bb_by_month.get(m, 0) for m in month_list]
    if max(counts) == 0:
        return "nao houve mencoes ao BB no periodo", month_list
    min_v = min(counts)
    max_v = max(counts)
    within_0_2 = sum(1 for v in counts if 0 <= v <= 2)
    if len(counts) > 0 and within_0_2 / len(counts) >= 0.75:
        range_txt = "em geral 0-2 por mes"
    else:
        range_txt = f"variou de {min_v} a {max_v} por mes"
    peak_months = [m for m in month_list if bb_by_month.get(m, 0) == max_v]
    peak_txt = "pico de {0} em {1}".format(max_v, ", ".join(peak_months[:2]) + ("..." if len(peak_months) > 2 else ""))
    zero_months = [m for m in month_list if bb_by_month.get(m, 0) == 0]
    return f"{range_txt}, com {peak_txt}", zero_months


def map_columns_to_console(mapping: ColumnMap) -> None:
    print("Mapeamento de colunas:")
    print(f"- data/hora: {mapping.date}")
    print(f"- url: {mapping.url}")
    print(f"- texto/legenda: {mapping.text}")
    print(f"- mentions: {mapping.mentions}")
    print(f"- hashtags: {mapping.hashtags}")
    print(f"- brands: {mapping.brands}")
    print(f"- patrocinado: {mapping.sponsored}")
    print(f"- paid_partnership: {mapping.paid_partnership}")
    print(f"- owner: {mapping.owner}")
    print(f"- media_type: {mapping.media_type}")
    print(f"- likes: {mapping.likes}")
    print(f"- comments: {mapping.comments}")
    print(f"- views/plays: {mapping.views}")


def build_tables_md(monthly_rows: List[Dict[str, Any]], brand_top10: List[Tuple[str, int]]) -> Optional[str]:
    sections = []
    if monthly_rows:
        lines = ["## Mencoes BB por mes", "| month | posts_bb | posts_total |", "| --- | --- | --- |"]
        for row in monthly_rows:
            lines.append(f"| {row['month']} | {row['posts_bb']} | {row['posts_total']} |")
        sections.append("\n".join(lines))
    if brand_top10:
        lines = ["## Ranking de marcas (patrocinados)", "| handle | posts |", "| --- | --- |"]
        for handle, count in brand_top10:
            lines.append(f"| {handle} | {count} |")
        sections.append("\n".join(lines))
    if not sections:
        return None
    return "\n\n".join(sections).rstrip() + "\n"


def build_text_report(payload: Dict[str, Any]) -> str:
    base = payload["base"]
    bb = payload["bb"]
    sponsored = payload["sponsored"]
    brands = payload["brands"]
    branding = payload.get("branding", {})
    fmt = payload["format"]
    perf = payload["performance"]
    origin = payload["bb_origin"]
    monthly = payload["monthly"]
    meta = payload["meta"]

    principal = meta.get("principal_handle") or ""
    since = meta.get("since") or ""
    date_min = base.get("date_min")
    date_max = base.get("date_max")

    paragraphs: List[str] = []

    if base.get("posts_total") is None or base.get("posts_total") == 0:
        paragraphs.append(
            f"Nao ha publicacoes validas no recorte a partir de {since}. "
            "Sem esse volume minimo, nao e possivel detalhar indicadores."
        )
        paragraphs.append(
            "Ressalva final: nao ha metas ou benchmarks registrados. Portanto, o texto apenas descreve o que os dados "
            "mostram, sem indicar se o desempenho esta alinhado ao esperado."
        )
        return "\n\n".join(paragraphs).strip() + "\n"

    if date_min and date_max:
        line1 = f"O periodo analisado vai de {date_min} a {date_max}, considerando publicacoes a partir de {since}."
    else:
        line1 = f"O recorte considera publicacoes a partir de {since}, mas o periodo exato nao pode ser determinado."

    line1 += f" No total, foram {fmt_int(base.get('posts_total'))} publicacoes no recorte."
    if base.get("principal_posts") is not None:
        line1 += (
            f" Destas, {fmt_int(base.get('principal_posts'))} sao do {principal} "
            f"({fmt_pct_value(base.get('principal_share_pct'))} do total) e {fmt_int(base.get('other_posts'))} "
            "sao de outras contas."
        )
    paragraphs.append(line1)

    if bb.get("bb_posts_total") is not None:
        if bb.get("bb_posts_total") == 0:
            paragraphs.append("Nao houve mencoes ao Banco do Brasil no periodo analisado.")
        else:
            line2 = (
                f"Em relacao ao Banco do Brasil, ha {fmt_int(bb.get('bb_posts_total'))} posts com mencao, "
                f"o que representa {fmt_pct_value(bb.get('bb_share_pct'))} do total."
            )
            if bb.get("bb_last_date"):
                ref_date = bb.get("bb_ref_date") or date_max
                ref_days = bb.get("bb_days_since_last_ref")
                if ref_date and ref_days is not None:
                    line2 += (
                        f" A ultima mencao ocorreu em {bb.get('bb_last_date')} e, usando {ref_date} como referencia, "
                        f"isso indica {ref_days} dias desde a ultima mencao."
                    )
                elif bb.get("bb_days_since_last") is not None and date_max:
                    line2 += (
                        f" A ultima mencao ocorreu em {bb.get('bb_last_date')}, "
                        f"{bb.get('bb_days_since_last')} dias antes da data mais recente da base ({date_max})."
                    )
            paragraphs.append(line2)

            if monthly.get("summary"):
                month_line = f"Na distribuicao mensal, {monthly.get('summary')}."
                zero_months = monthly.get("zero_months") or []
                if zero_months:
                    if len(zero_months) <= 6:
                        month_line += f" Meses sem mencao: {', '.join(zero_months)}."
                    else:
                        month_line += f" Meses sem mencao incluem: {', '.join(zero_months[:6])}, entre outros."
                paragraphs.append(month_line)

            if date_min and date_max:
                med = bb.get("bb_interval_median_days")
                avg = bb.get("bb_interval_mean_days")
                if med is not None and avg is not None:
                    paragraphs.append(
                        "A regularidade entre mencoes ao BB mostra intervalo mediano de "
                        f"{fmt_days(med)} dias (o intervalo mais tipico) e medio de {fmt_days(avg)} dias (media geral)."
                    )
                else:
                    paragraphs.append("Nao ha base suficiente para estimar intervalos entre mencoes ao BB.")

            if bb.get("bb_explicit_mentions_posts") is not None and bb.get("bb_posts_total"):
                tag_line = (
                    f"Sobre marcacao, {fmt_int(bb.get('bb_explicit_mentions_posts'))} posts BB trazem "
                    f"@bancodobrasil explicitamente ({fmt_pct_value(bb.get('bb_explicit_mentions_share_pct'))} dos BB)."
                )
                if branding.get("bb_tag_missing_posts") is not None:
                    tag_line += f" Isso deixa {fmt_int(branding.get('bb_tag_missing_posts'))} posts BB sem a marcacao direta."
                paragraphs.append(tag_line)

    if sponsored.get("sponsored_posts_total") is not None:
        line3 = (
            f"Sobre posts patrocinados, foram {fmt_int(sponsored.get('sponsored_posts_total'))} publicacoes "
            f"({fmt_pct_value(sponsored.get('sponsored_share_pct'))} do total)."
        )
        if sponsored.get("sponsored_posts_total") and sponsored.get("sponsored_bb_posts") is not None:
            line3 += (
                f" Entre esses, {fmt_int(sponsored.get('sponsored_bb_posts'))} mencionam o BB, "
                f"o que equivale a {fmt_pct_value(sponsored.get('sponsored_bb_share_pct'))} dos patrocinados."
            )
        if (
            sponsored.get("sponsored_posts_total")
            and sponsored.get("bb_posts_total")
            and sponsored.get("bb_posts_org") is not None
        ):
            bb_sponsored = None
            if sponsored.get("bb_posts_total") is not None and sponsored.get("bb_posts_org") is not None:
                bb_sponsored = sponsored.get("bb_posts_total") - sponsored.get("bb_posts_org")
            if bb_sponsored is not None:
                line3 += (
                    f" Dentro das mencoes ao BB, {fmt_int(sponsored.get('bb_posts_org'))} sao organicas "
                    f"e {fmt_int(bb_sponsored)} sao patrocinadas, indicando "
                    f"{fmt_pct_value(sponsored.get('bb_org_share_of_bb_pct'))} de BB organico."
                )
        if meta.get("sponsored_method") == "mentions_proxy":
            line3 += " Quando nao havia marcacao explicita, a classificacao de patrocinio foi inferida por mencoes de marcas."
        paragraphs.append(line3)

        if branding.get("bb_sponsored_brand_solo_posts") is not None and sponsored.get("sponsored_bb_posts"):
            line_brand = (
                f"No recorte BB patrocinado, {fmt_int(branding.get('bb_sponsored_brand_solo_posts'))} posts "
                "trazem apenas o BB e "
                f"{fmt_int(branding.get('bb_sponsored_brand_multi_posts'))} combinam outras marcas."
            )
            if branding.get("bb_sponsored_brand_no_tag_posts") is not None:
                line_brand += (
                    f" Outros {fmt_int(branding.get('bb_sponsored_brand_no_tag_posts'))} posts BB patrocinados "
                    "nao trazem @bancodobrasil explicitamente."
                )
            if branding.get("bb_sponsored_co_mentions_top5"):
                top_parts = []
                for handle, count in branding.get("bb_sponsored_co_mentions_top5", []):
                    top_parts.append(f"{handle} ({fmt_int(count)})")
                line_brand += " As marcas mais frequentes junto do BB foram: " + ", ".join(top_parts) + "."
            paragraphs.append(line_brand)

    if brands.get("top10"):
        top10_parts = []
        for handle, count in brands["top10"]:
            top10_parts.append(f"{handle} ({fmt_int(count)})")
        line4 = "Entre os patrocinados, as 10 marcas mais mencionadas foram: " + ", ".join(top10_parts) + "."
        if brands.get("bb_rank") is not None and brands.get("bb_vs_leader_ratio") is not None:
            line4 += (
                f" O BB aparece na posicao {brands.get('bb_rank')} do ranking, com razao de "
                f"{brands.get('bb_vs_leader_ratio'):.3f} em relacao ao lider."
            )
        paragraphs.append(line4)

    if fmt.get("reels_share_total_pct") is not None:
        line_fmt = (
            f"Quanto ao formato, reels representam {fmt_pct_value(fmt.get('reels_share_total_pct'))} do total e "
            f"{fmt_pct_value(fmt.get('reels_share_bb_pct'))} dentro dos posts que mencionam BB."
        )
        if fmt.get("reels_share_sponsored_pct") is not None:
            line_fmt += f" Entre os patrocinados, reels sao {fmt_pct_value(fmt.get('reels_share_sponsored_pct'))}."
        if fmt.get("reels_share_bb_sponsored_pct") is not None:
            line_fmt += (
                f" No recorte BB patrocinado, reels sao {fmt_pct_value(fmt.get('reels_share_bb_sponsored_pct'))}."
            )
        if fmt.get("bb_share_in_sponsored_reels_pct") is not None:
            line_fmt += (
                " Considerando apenas reels patrocinados, "
                f"{fmt_pct_value(fmt.get('bb_share_in_sponsored_reels_pct'))} mencionam BB."
            )
        paragraphs.append(line_fmt)

    if perf.get("likes") or perf.get("comments"):
        perf_lines = []
        if perf.get("likes"):
            likes = perf["likes"]
            perf_lines.append(
                "Para likes, a mediana nos patrocinados com BB foi de "
                f"{fmt_days(likes.get('bb_median'))} contra {fmt_days(likes.get('nonbb_median'))} em nao-BB, "
                f"com base em {fmt_int(likes.get('bb_count'))} posts BB e {fmt_int(likes.get('nonbb_count'))} "
                "posts nao-BB com dado disponivel."
            )
        if perf.get("comments"):
            comm = perf["comments"]
            perf_lines.append(
                "Para comentarios, a mediana nos patrocinados com BB foi de "
                f"{fmt_days(comm.get('bb_median'))} contra {fmt_days(comm.get('nonbb_median'))} em nao-BB, "
                f"com base em {fmt_int(comm.get('bb_count'))} posts BB e {fmt_int(comm.get('nonbb_count'))} "
                "posts nao-BB com dado disponivel."
            )
        paragraphs.append(" ".join(perf_lines))

    if origin.get("bb_principal_posts") is not None:
        origin_line = (
            f"Quanto a origem das mencoes ao BB, {fmt_int(origin.get('bb_principal_posts'))} posts sao do "
            f"{principal} ({fmt_pct_value(origin.get('bb_principal_share_pct'))} dos BB) e "
            f"{fmt_int(origin.get('bb_other_posts'))} sao de outras contas."
        )
        if origin.get("bb_other_owners_top"):
            top_parts = []
            for handle, count in origin.get("bb_other_owners_top", []):
                top_parts.append(f"{handle} ({fmt_int(count)})")
            origin_line += " Entre outras contas, aparecem: " + ", ".join(top_parts) + "."
        paragraphs.append(origin_line)

    paragraphs.append(
        "Ressalva final: nao ha metas ou benchmarks registrados. Portanto, o texto apenas descreve o que os dados "
        "mostram, sem indicar se o desempenho esta alinhado ao esperado."
    )

    return "\n\n".join(paragraphs).strip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Gera texto executivo a partir de planilha de posts Instagram.")
    parser.add_argument("--file", required=True, help="Caminho do CSV/XLSX.")
    parser.add_argument("--user", required=True, help="Handle principal (ex: tainahinckel).")
    parser.add_argument(
        "--since",
        default=None,
        help="Data inicio (YYYY-MM-DD). Opcional; quando ausente, usa o inicio da base.",
    )
    parser.add_argument("--out", default="out", help="Diretorio de saida.")
    args = parser.parse_args(argv)

    file_path = resolve_path(args.file)
    if not file_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {file_path}")

    df = read_input(file_path)
    df.columns = [str(c).strip() for c in df.columns]

    colmap = detect_columns(df)
    map_columns_to_console(colmap)

    principal_handle = normalize_handle(args.user)
    run_handle = principal_handle or handle_from_filename(file_path)
    collected_at = resolve_run_log_datetime(file_path, run_handle, ROOT)
    since_raw = (args.since or "").strip()
    since_dt = None
    if since_raw:
        since_dt = pd.to_datetime(since_raw, errors="coerce", utc=True)
        if pd.isna(since_dt):
            raise SystemExit("Data --since invalida. Use YYYY-MM-DD.")

    data = df.copy()
    date_series = parse_datetime(data[colmap.date]) if colmap.date else pd.Series([pd.NaT] * len(data))
    data["_post_dt"] = date_series
    missing_date_count = int(data["_post_dt"].isna().sum())

    if colmap.date:
        data = data[~data["_post_dt"].isna()]
        if since_dt is not None:
            data = data[data["_post_dt"] >= since_dt]

    total_rows = int(len(data))
    date_min = data["_post_dt"].min() if total_rows else None
    date_max = data["_post_dt"].max() if total_rows else None
    if date_min is not None and pd.isna(date_min):
        date_min = None
    if date_max is not None and pd.isna(date_max):
        date_max = None

    aliases = build_bb_aliases()
    features = build_post_features(data, colmap, aliases)
    bb_dates_initial = [
        data["_post_dt"].iloc[i]
        for i, v in enumerate(features["is_bb_flags"])
        if v and not pd.isna(data["_post_dt"].iloc[i])
    ]
    bb_first_dt = min(bb_dates_initial) if bb_dates_initial else None

    bb_first_str = None
    since_effective = since_raw or None
    if bb_first_dt is not None:
        bb_first_str = fmt_date(bb_first_dt.to_pydatetime() if hasattr(bb_first_dt, "to_pydatetime") else bb_first_dt)
        if bb_first_str:
            since_effective = bb_first_str
        if date_min is None or bb_first_dt > date_min:
            data = data[data["_post_dt"] >= bb_first_dt]
            total_rows = int(len(data))
            date_min = data["_post_dt"].min() if total_rows else None
            date_max = data["_post_dt"].max() if total_rows else None
            if date_min is not None and pd.isna(date_min):
                date_min = None
            if date_max is not None and pd.isna(date_max):
                date_max = None
            features = build_post_features(data, colmap, aliases)
    if since_effective is None and date_min is not None:
        since_effective = fmt_date(date_min.to_pydatetime() if hasattr(date_min, "to_pydatetime") else date_min)
    bb_first_date = bb_first_str

    mentions_list = features["mentions_list"]
    hashtags_list = features["hashtags_list"]
    brand_list = features["brand_list"]
    owner_norm = features["owner_norm"]
    is_bb_flags = features["is_bb_flags"]
    bb_connection_types = features["bb_connection_types"]
    bb_explicit_flags = features["bb_explicit_flags"]
    data["_is_bb_mention"] = is_bb_flags
    data["_bb_connection_type"] = bb_connection_types
    bb_handle = "@bancodobrasil"

    sponsored_source = None
    has_sponsored_data = False
    if colmap.sponsored:
        sponsored_source = "sponsored_column"
        sponsored_flags = [parse_bool(v) for v in data[colmap.sponsored].tolist()]
        has_sponsored_data = True
    elif colmap.paid_partnership:
        sponsored_source = "paid_partnership_column"
        sponsored_flags = [parse_bool(v) for v in data[colmap.paid_partnership].tolist()]
        has_sponsored_data = True
    else:
        proxy_available = bool(colmap.brands or colmap.mentions or colmap.text)
        if proxy_available:
            sponsored_source = "mentions_proxy"
            sponsored_flags = [bool(brand_list[i]) for i in range(total_rows)]
            has_sponsored_data = True
        else:
            sponsored_flags = [None] * total_rows

    if has_sponsored_data:
        sponsored_flags = [bool(v) if v is not None else False for v in sponsored_flags]

    likes_series = data[colmap.likes] if colmap.likes else pd.Series([None] * total_rows)
    comments_series = data[colmap.comments] if colmap.comments else pd.Series([None] * total_rows)
    views_series = data[colmap.views] if colmap.views else pd.Series([None] * total_rows)

    likes_values = [parse_number(v) for v in likes_series.tolist()] if colmap.likes else [None] * total_rows
    comments_values = [parse_number(v) for v in comments_series.tolist()] if colmap.comments else [None] * total_rows
    views_values = [parse_number(v) for v in views_series.tolist()] if colmap.views else [None] * total_rows

    media_series = (
        data[colmap.media_type].fillna("").astype(str).str.lower()
        if colmap.media_type
        else pd.Series([""] * total_rows)
    )
    media_values = media_series.tolist()

    principal_posts = None
    other_posts = None
    principal_share = None
    if colmap.owner and principal_handle:
        principal_posts = sum(1 for o in owner_norm if o == principal_handle)
        other_posts = total_rows - principal_posts
        principal_share = share(principal_posts, total_rows)

    bb_posts_total = sum(1 for v in is_bb_flags if v)
    bb_share_total = share(bb_posts_total, total_rows)
    bb_explicit_posts = sum(1 for i, v in enumerate(is_bb_flags) if v and bb_explicit_flags[i])
    bb_explicit_share = share(bb_explicit_posts, bb_posts_total)

    bb_connection_counts = {"mention": 0, "hashtag": 0, "mention-hashtag": 0, "unknown": 0}
    for i, flagged in enumerate(is_bb_flags):
        if not flagged:
            continue
        connection = bb_connection_types[i] or "unknown"
        if connection not in bb_connection_counts:
            bb_connection_counts["unknown"] += 1
        else:
            bb_connection_counts[connection] += 1
    bb_connection_stats = {
        "mention_posts": bb_connection_counts["mention"],
        "mention_share_pct": share(bb_connection_counts["mention"], bb_posts_total),
        "hashtag_posts": bb_connection_counts["hashtag"],
        "hashtag_share_pct": share(bb_connection_counts["hashtag"], bb_posts_total),
        "mention_hashtag_posts": bb_connection_counts["mention-hashtag"],
        "mention_hashtag_share_pct": share(bb_connection_counts["mention-hashtag"], bb_posts_total),
        "unknown_posts": bb_connection_counts["unknown"],
        "unknown_share_pct": share(bb_connection_counts["unknown"], bb_posts_total),
    }

    bb_dates = [
        data["_post_dt"].iloc[i] for i, v in enumerate(is_bb_flags) if v and not pd.isna(data["_post_dt"].iloc[i])
    ]
    last_bb_dt = max(bb_dates) if bb_dates else None
    bb_days_since_last = None
    if last_bb_dt is not None and date_max is not None:
        bb_days_since_last = int((date_max - last_bb_dt).days)

    bb_dates_sorted = sorted(bb_dates)
    bb_intervals = []
    for i in range(1, len(bb_dates_sorted)):
        delta = (bb_dates_sorted[i] - bb_dates_sorted[i - 1]).total_seconds() / 86400.0
        bb_intervals.append(delta)
    bb_interval_median = median(bb_intervals) if len(bb_intervals) >= 1 else None
    bb_interval_mean = mean(bb_intervals) if len(bb_intervals) >= 1 else None

    bb_ref_dt = None
    if collected_at is not None:
        bb_ref_dt = collected_at
    elif date_max is not None:
        bb_ref_dt = date_max.to_pydatetime()

    bb_days_since_last_ref = None
    if last_bb_dt is not None and bb_ref_dt is not None:
        last_bb_py = last_bb_dt.to_pydatetime() if hasattr(last_bb_dt, "to_pydatetime") else last_bb_dt
        bb_days_since_last_ref = int((bb_ref_dt - last_bb_py).days)

    monthly_rows: List[Dict[str, Any]] = []
    monthly_summary = None
    zero_months: List[str] = []
    if date_min is not None and date_max is not None:
        months = month_range(date_min.to_pydatetime(), date_max.to_pydatetime())
        bb_by_month: Dict[str, int] = {}
        total_by_month: Dict[str, int] = {}
        for i in range(total_rows):
            dt = data["_post_dt"].iloc[i]
            if pd.isna(dt):
                continue
            key = dt.strftime("%Y-%m")
            total_by_month[key] = total_by_month.get(key, 0) + 1
            if is_bb_flags[i]:
                bb_by_month[key] = bb_by_month.get(key, 0) + 1
        for m in months:
            monthly_rows.append(
                {
                    "month": m,
                    "posts_bb": bb_by_month.get(m, 0),
                    "posts_total": total_by_month.get(m, 0),
                }
            )
        monthly_summary, zero_months = explain_monthly(bb_by_month, months)

    sponsored_posts_total = None
    sponsored_share_total = None
    sponsored_bb_posts = None
    sponsored_bb_share = None
    bb_posts_org = None
    bb_org_share_of_bb = None
    if has_sponsored_data:
        sponsored_posts_total = sum(1 for v in sponsored_flags if v)
        sponsored_share_total = share(sponsored_posts_total, total_rows)
        sponsored_bb_posts = sum(1 for i, v in enumerate(sponsored_flags) if v and is_bb_flags[i])
        sponsored_bb_share = share(sponsored_bb_posts, sponsored_posts_total)
        bb_posts_org = sum(1 for i, v in enumerate(is_bb_flags) if v and not sponsored_flags[i])
        bb_org_share_of_bb = share(bb_posts_org, bb_posts_total)

    bb_tag_missing_posts = bb_posts_total - bb_explicit_posts if bb_posts_total is not None else None
    bb_tag_missing_share = share(bb_tag_missing_posts, bb_posts_total)

    bb_sponsored_explicit_posts = None
    bb_sponsored_explicit_share = None
    if has_sponsored_data:
        bb_sponsored_explicit_posts = sum(
            1 for i, v in enumerate(is_bb_flags) if v and sponsored_flags[i] and bb_explicit_flags[i]
        )
        bb_sponsored_explicit_share = share(bb_sponsored_explicit_posts, sponsored_bb_posts)

    bb_brand_solo_posts = 0
    bb_brand_multi_posts = 0
    bb_brand_no_tag_posts = 0
    bb_sponsored_brand_solo_posts = 0
    bb_sponsored_brand_multi_posts = 0
    bb_sponsored_brand_no_tag_posts = 0
    brand_counts_bb: List[int] = []
    brand_counts_sponsored: List[int] = []
    brand_counts_bb_sponsored: List[int] = []
    bb_sponsored_co_mentions: Counter[str] = Counter()

    for i in range(total_rows):
        brand_handles = [m for m in brand_list[i] if m.startswith("@")]
        brand_count = len(brand_handles)

        if is_bb_flags[i]:
            brand_counts_bb.append(brand_count)
            if bb_handle in brand_handles:
                if brand_count == 1:
                    bb_brand_solo_posts += 1
                elif brand_count > 1:
                    bb_brand_multi_posts += 1
            else:
                bb_brand_no_tag_posts += 1

        if has_sponsored_data and sponsored_flags[i]:
            brand_counts_sponsored.append(brand_count)
            if is_bb_flags[i]:
                brand_counts_bb_sponsored.append(brand_count)
                if bb_handle in brand_handles:
                    if brand_count == 1:
                        bb_sponsored_brand_solo_posts += 1
                    elif brand_count > 1:
                        bb_sponsored_brand_multi_posts += 1
                    for handle in brand_handles:
                        if handle != bb_handle:
                            bb_sponsored_co_mentions[handle] += 1
                else:
                    bb_sponsored_brand_no_tag_posts += 1

    bb_brand_solo_share = share(bb_brand_solo_posts, bb_posts_total)
    bb_brand_multi_share = share(bb_brand_multi_posts, bb_posts_total)
    bb_brand_no_tag_share = share(bb_brand_no_tag_posts, bb_posts_total)

    bb_sponsored_brand_solo_share = share(bb_sponsored_brand_solo_posts, sponsored_bb_posts)
    bb_sponsored_brand_multi_share = share(bb_sponsored_brand_multi_posts, sponsored_bb_posts)
    bb_sponsored_brand_no_tag_share = share(bb_sponsored_brand_no_tag_posts, sponsored_bb_posts)

    brands_per_bb_post_avg = round(mean(brand_counts_bb), 1) if brand_counts_bb else None
    brands_per_sponsored_post_avg = round(mean(brand_counts_sponsored), 1) if brand_counts_sponsored else None
    brands_per_sponsored_bb_post_avg = round(mean(brand_counts_bb_sponsored), 1) if brand_counts_bb_sponsored else None

    bb_sponsored_co_mentions_top5 = bb_sponsored_co_mentions.most_common(5)

    if not has_sponsored_data:
        bb_sponsored_brand_solo_posts = None
        bb_sponsored_brand_multi_posts = None
        bb_sponsored_brand_no_tag_posts = None
        bb_sponsored_brand_solo_share = None
        bb_sponsored_brand_multi_share = None
        bb_sponsored_brand_no_tag_share = None
        bb_sponsored_co_mentions_top5 = []
        brands_per_sponsored_post_avg = None
        brands_per_sponsored_bb_post_avg = None

    brand_counter: Counter[str] = Counter()
    if has_sponsored_data:
        for i in range(total_rows):
            if not sponsored_flags[i]:
                continue
            owner = owner_norm[i]
            mentions = [m for m in brand_list[i] if m.startswith("@")]
            if owner:
                mentions = [m for m in mentions if m.lstrip("@") != owner]
            mentions = list({m.lower() for m in mentions})
            for m in mentions:
                brand_counter[m] += 1
    top10 = brand_counter.most_common(10)
    leader_handle, leader_posts = (top10[0] if top10 else (None, None))
    bb_rank = None
    bb_ratio = None
    if top10:
        for idx, (h, _count) in enumerate(top10, start=1):
            if h == "@bancodobrasil":
                bb_rank = idx
                break
    if leader_posts and leader_posts > 0:
        bb_posts = brand_counter.get("@bancodobrasil", 0)
        bb_ratio = round(bb_posts / leader_posts, 3)

    reels_total = None
    reels_bb = None
    reels_sponsored_total = None
    reels_bb_sponsored_total = None
    reels_share_total = None
    reels_share_bb = None
    reels_share_sponsored = None
    reels_share_bb_sponsored = None
    bb_share_in_sponsored_reels = None
    if colmap.media_type and total_rows:
        media_filled = sum(1 for v in media_values if v)
        if media_filled > 0:
            reels_total = sum(1 for v in media_values if "reel" in v)
            reels_share_total = share(reels_total, total_rows)
            reels_bb = sum(1 for i, v in enumerate(media_values) if "reel" in v and is_bb_flags[i])
            reels_share_bb = share(reels_bb, bb_posts_total)
            if has_sponsored_data:
                reels_sponsored_total = sum(
                    1 for i, v in enumerate(media_values) if "reel" in v and sponsored_flags[i]
                )
                reels_share_sponsored = share(reels_sponsored_total, sponsored_posts_total)
                reels_bb_sponsored_total = sum(
                    1
                    for i, v in enumerate(media_values)
                    if "reel" in v and sponsored_flags[i] and is_bb_flags[i]
                )
                reels_share_bb_sponsored = share(reels_bb_sponsored_total, sponsored_bb_posts)
                bb_share_in_sponsored_reels = share(reels_bb_sponsored_total, reels_sponsored_total)

    perf_likes = None
    if colmap.likes and has_sponsored_data:
        bb_likes = [
            likes_values[i] for i in range(total_rows) if sponsored_flags[i] and is_bb_flags[i] and likes_values[i] is not None
        ]
        non_bb_likes = [
            likes_values[i]
            for i in range(total_rows)
            if sponsored_flags[i] and not is_bb_flags[i] and likes_values[i] is not None
        ]
        if bb_likes and non_bb_likes:
            perf_likes = {
                "bb_median": median([float(v) for v in bb_likes]),
                "nonbb_median": median([float(v) for v in non_bb_likes]),
                "bb_count": len(bb_likes),
                "nonbb_count": len(non_bb_likes),
            }

    perf_comments = None
    if colmap.comments and has_sponsored_data:
        bb_comments = [
            comments_values[i]
            for i in range(total_rows)
            if sponsored_flags[i] and is_bb_flags[i] and comments_values[i] is not None
        ]
        non_bb_comments = [
            comments_values[i]
            for i in range(total_rows)
            if sponsored_flags[i] and not is_bb_flags[i] and comments_values[i] is not None
        ]
        if bb_comments and non_bb_comments:
            perf_comments = {
                "bb_median": median([float(v) for v in bb_comments]),
                "nonbb_median": median([float(v) for v in non_bb_comments]),
                "bb_count": len(bb_comments),
                "nonbb_count": len(non_bb_comments),
            }

    perf_format = None
    if colmap.media_type and has_sponsored_data:
        def build_format_stats(match_reel: bool) -> Dict[str, Any]:
            posts_total = 0
            likes_vals: List[float] = []
            comments_vals: List[float] = []
            for i in range(total_rows):
                if not sponsored_flags[i]:
                    continue
                is_reel = "reel" in media_values[i]
                if is_reel != match_reel:
                    continue
                posts_total += 1
                if likes_values[i] is not None:
                    likes_vals.append(float(likes_values[i]))
                if comments_values[i] is not None:
                    comments_vals.append(float(comments_values[i]))
            return {
                "posts_total": posts_total,
                "likes_median": median(likes_vals) if likes_vals else None,
                "likes_count": len(likes_vals),
                "comments_median": median(comments_vals) if comments_vals else None,
                "comments_count": len(comments_vals),
            }

        perf_format = {
            "sponsored_reels": build_format_stats(True),
            "sponsored_nonreels": build_format_stats(False),
        }

    bb_principal_posts = None
    bb_other_posts = None
    bb_principal_share = None
    if colmap.owner and principal_handle:
        bb_principal_posts = sum(1 for i, v in enumerate(is_bb_flags) if v and owner_norm[i] == principal_handle)
        bb_other_posts = bb_posts_total - bb_principal_posts
        bb_principal_share = share(bb_principal_posts, bb_posts_total)
    bb_other_owners_top = []
    if colmap.owner:
        other_counts: Counter[str] = Counter()
        for i, flagged in enumerate(is_bb_flags):
            if not flagged:
                continue
            owner = owner_norm[i]
            if not owner or owner == principal_handle:
                continue
            other_counts[owner] += 1
        bb_other_owners_top = [(f"@{handle}", count) for handle, count in other_counts.most_common(3)]

    indicadores: Dict[str, Any] = {
        "meta": {
            "file": str(file_path),
            "principal_handle": f"@{principal_handle}" if principal_handle else None,
            "since": since_effective,
            "since_input": since_raw or None,
            "bb_first_date": bb_first_date,
            "rows_total_input": int(len(df)),
            "rows_missing_date": missing_date_count,
            "rows_in_range": total_rows,
            "column_mapping": colmap.__dict__,
            "sponsored_method": sponsored_source,
            "collected_at_utc": collected_at.isoformat() if collected_at else None,
        },
        "base": {
            "posts_total": total_rows,
            "date_min": fmt_date(date_min.to_pydatetime()) if date_min is not None else None,
            "date_max": fmt_date(date_max.to_pydatetime()) if date_max is not None else None,
            "principal_posts": principal_posts,
            "principal_share_pct": principal_share,
            "other_posts": other_posts,
        },
        "bb": {
            "bb_posts_total": bb_posts_total,
            "bb_share_pct": bb_share_total,
            "bb_last_date": fmt_date(last_bb_dt.to_pydatetime()) if last_bb_dt is not None else None,
            "bb_days_since_last": bb_days_since_last,
            "bb_interval_median_days": bb_interval_median,
            "bb_interval_mean_days": bb_interval_mean,
            "bb_ref_date": fmt_date(bb_ref_dt) if bb_ref_dt is not None else None,
            "bb_days_since_last_ref": bb_days_since_last_ref,
            "bb_explicit_mentions_posts": bb_explicit_posts,
            "bb_explicit_mentions_share_pct": bb_explicit_share,
        },
        "bb_connection": bb_connection_stats,
        "monthly": {
            "summary": monthly_summary,
            "zero_months": zero_months,
            "rows": monthly_rows,
        },
        "sponsored": {
            "sponsored_posts_total": sponsored_posts_total,
            "sponsored_share_pct": sponsored_share_total,
            "sponsored_bb_posts": sponsored_bb_posts,
            "sponsored_bb_share_pct": sponsored_bb_share,
            "bb_posts_total": bb_posts_total,
            "bb_posts_org": bb_posts_org,
            "bb_org_share_of_bb_pct": bb_org_share_of_bb,
        },
        "brands": {
            "top10": top10,
            "leader_handle": leader_handle,
            "leader_posts": leader_posts,
            "bb_rank": bb_rank,
            "bb_vs_leader_ratio": bb_ratio,
        },
        "branding": {
            "bb_tag_missing_posts": bb_tag_missing_posts,
            "bb_tag_missing_share_pct": bb_tag_missing_share,
            "bb_sponsored_explicit_mentions_posts": bb_sponsored_explicit_posts,
            "bb_sponsored_explicit_mentions_share_pct": bb_sponsored_explicit_share,
            "bb_brand_solo_posts": bb_brand_solo_posts,
            "bb_brand_solo_share_pct": bb_brand_solo_share,
            "bb_brand_multi_posts": bb_brand_multi_posts,
            "bb_brand_multi_share_pct": bb_brand_multi_share,
            "bb_brand_no_tag_posts": bb_brand_no_tag_posts,
            "bb_brand_no_tag_share_pct": bb_brand_no_tag_share,
            "bb_sponsored_brand_solo_posts": bb_sponsored_brand_solo_posts,
            "bb_sponsored_brand_solo_share_pct": bb_sponsored_brand_solo_share,
            "bb_sponsored_brand_multi_posts": bb_sponsored_brand_multi_posts,
            "bb_sponsored_brand_multi_share_pct": bb_sponsored_brand_multi_share,
            "bb_sponsored_brand_no_tag_posts": bb_sponsored_brand_no_tag_posts,
            "bb_sponsored_brand_no_tag_share_pct": bb_sponsored_brand_no_tag_share,
            "bb_sponsored_co_mentions_top5": bb_sponsored_co_mentions_top5,
            "brands_per_bb_post_avg": brands_per_bb_post_avg,
            "brands_per_sponsored_post_avg": brands_per_sponsored_post_avg,
            "brands_per_sponsored_bb_post_avg": brands_per_sponsored_bb_post_avg,
        },
        "format": {
            "reels_total": reels_total,
            "reels_bb_total": reels_bb,
            "reels_sponsored_total": reels_sponsored_total,
            "reels_bb_sponsored_total": reels_bb_sponsored_total,
            "reels_share_total_pct": reels_share_total,
            "reels_share_bb_pct": reels_share_bb,
            "reels_share_sponsored_pct": reels_share_sponsored,
            "reels_share_bb_sponsored_pct": reels_share_bb_sponsored,
            "bb_share_in_sponsored_reels_pct": bb_share_in_sponsored_reels,
        },
        "performance": {
            "likes": perf_likes,
            "comments": perf_comments,
        },
        "performance_format": perf_format,
        "bb_origin": {
            "bb_principal_posts": bb_principal_posts,
            "bb_principal_share_pct": bb_principal_share,
            "bb_other_posts": bb_other_posts,
            "bb_other_owners_top": bb_other_owners_top,
        },
        "coverage": {
            "likes_coverage_pct": share(sum(1 for v in likes_values if v is not None), total_rows) if colmap.likes else None,
            "comments_coverage_pct": share(sum(1 for v in comments_values if v is not None), total_rows) if colmap.comments else None,
            "views_coverage_pct": share(sum(1 for v in views_values if v is not None), total_rows) if colmap.views else None,
        },
    }

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    indicadores_path = out_dir / "indicadores.json"
    texto_path = out_dir / "texto_relatorio.md"
    tabelas_path = out_dir / "tabelas.md"

    indicadores_path.write_text(json.dumps(indicadores, ensure_ascii=True, indent=2), encoding="utf-8")

    texto = build_text_report(indicadores)
    texto_path.write_text(texto, encoding="utf-8")

    tables_md = build_tables_md(indicadores["monthly"]["rows"], indicadores["brands"]["top10"])
    if tables_md:
        tabelas_path.write_text(tables_md, encoding="utf-8")

    print(f"Indicadores: {indicadores_path}")
    print(f"Texto: {texto_path}")
    if tables_md:
        print(f"Tabelas: {tabelas_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
