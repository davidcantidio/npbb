#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.openai import OpenAIChat, OpenAIResponses


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


def load_indicators(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Falha ao ler arquivo: {path}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON invalido: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("JSON invalido: esperado objeto na raiz.")
    return payload


def get_nested(payload: Dict[str, Any], path: str) -> tuple[bool, Any]:
    current: Any = payload
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current


def validate_indicators(payload: Dict[str, Any]) -> None:
    required_paths = [
        "base.posts_total",
        "base.date_min",
        "base.date_max",
        "meta.principal_handle",
    ]
    missing = []
    for path in required_paths:
        ok, value = get_nested(payload, path)
        if not ok or value in (None, ""):
            missing.append(path)
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"Indicadores invalidos: campos ausentes: {joined}")


def build_period(payload: Dict[str, Any]) -> str:
    base = payload.get("base") if isinstance(payload.get("base"), dict) else {}
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    date_min = base.get("date_min")
    date_max = base.get("date_max")
    since = meta.get("since")
    if date_min and date_max:
        return f"{date_min} a {date_max}"
    if since and date_max:
        return f"{since} a {date_max}"
    if since:
        return f"a partir de {since}"
    return "periodo nao informado"


def sanitize_indicators(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.loads(json.dumps(payload))
    principal_handle = None
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else None
    if isinstance(meta, dict):
        principal_handle = meta.get("principal_handle")
        meta.pop("file", None)
        meta.pop("column_mapping", None)
        meta.pop("sponsored_method", None)
    base = data.get("base") if isinstance(data.get("base"), dict) else None
    if isinstance(base, dict):
        if principal_handle and "principal_handle" not in base:
            base["principal_handle"] = principal_handle
        posts_total = base.get("posts_total")
        other_posts = base.get("other_posts")
        principal_share = base.get("principal_share_pct")
        if isinstance(posts_total, (int, float)) and isinstance(other_posts, (int, float)):
            other_share = round((other_posts / posts_total) * 100, 1) if posts_total else 0.0
            base["other_share_pct"] = other_share
        if principal_share is not None and "other_share_pct" not in base and isinstance(principal_share, (int, float)):
            base["other_share_pct"] = round(100 - float(principal_share), 1)
        base["other_is_reposts"] = bool(other_posts and other_posts > 0)
    return data


def load_min_posts_threshold(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    value = payload.get("min_posts")
    if isinstance(value, int) and value > 0:
        return value
    return None


def load_coverage_thresholds(path: Path) -> Dict[str, int]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    coverage = payload.get("coverage_min_pct")
    if not isinstance(coverage, dict):
        return {}
    out: Dict[str, int] = {}
    for key, value in coverage.items():
        if isinstance(value, int) and value > 0:
            out[str(key)] = value
    return out


def parse_positive_int(value: Optional[int], name: str, max_value: Optional[int] = None) -> Optional[int]:
    if value is None:
        return None
    if value <= 0:
        raise SystemExit(f"Valor invalido em {name}: {value}. Use inteiro > 0.")
    if max_value is not None and value > max_value:
        raise SystemExit(f"Valor invalido em {name}: {value}. Use inteiro <= {max_value}.")
    return value


class BrandCount(BaseModel):
    handle: str
    posts: int


class BaseBlock(BaseModel):
    posts_total: int
    date_min: str
    date_max: str
    principal_handle: str
    principal_posts: int
    principal_share_pct: float
    other_posts: int
    other_share_pct: float
    other_is_reposts: bool


class BBBlock(BaseModel):
    bb_posts_total: int
    bb_share_pct: float
    bb_last_date: Optional[str] = None
    bb_ref_date: Optional[str] = None
    bb_days_since_last_ref: Optional[int] = None
    bb_interval_median_days: Optional[float] = None
    bb_interval_mean_days: Optional[float] = None
    bb_explicit_mentions_posts: Optional[int] = None
    bb_explicit_mentions_share_pct: Optional[float] = None


class BBConnectionBlock(BaseModel):
    mention_posts: Optional[int] = None
    mention_share_pct: Optional[float] = None
    hashtag_posts: Optional[int] = None
    hashtag_share_pct: Optional[float] = None
    mention_hashtag_posts: Optional[int] = None
    mention_hashtag_share_pct: Optional[float] = None
    unknown_posts: Optional[int] = None
    unknown_share_pct: Optional[float] = None


class MonthlyBlock(BaseModel):
    summary: Optional[str] = None
    zero_months: List[str] = Field(default_factory=list)


class SponsoredBlock(BaseModel):
    sponsored_posts_total: int
    sponsored_share_pct: float
    sponsored_bb_posts: Optional[int] = None
    sponsored_bb_share_pct: Optional[float] = None
    bb_posts_total: Optional[int] = None
    bb_posts_org: Optional[int] = None
    bb_org_share_of_bb_pct: Optional[float] = None


class BrandsBlock(BaseModel):
    top10: List[BrandCount] = Field(default_factory=list)
    leader_handle: Optional[str] = None
    leader_posts: Optional[int] = None
    bb_rank: Optional[int] = None
    bb_vs_leader_ratio: Optional[float] = None


class BrandingBlock(BaseModel):
    bb_tag_missing_posts: Optional[int] = None
    bb_tag_missing_share_pct: Optional[float] = None
    bb_sponsored_explicit_mentions_posts: Optional[int] = None
    bb_sponsored_explicit_mentions_share_pct: Optional[float] = None
    bb_brand_solo_posts: Optional[int] = None
    bb_brand_solo_share_pct: Optional[float] = None
    bb_brand_multi_posts: Optional[int] = None
    bb_brand_multi_share_pct: Optional[float] = None
    bb_brand_no_tag_posts: Optional[int] = None
    bb_brand_no_tag_share_pct: Optional[float] = None
    bb_sponsored_brand_solo_posts: Optional[int] = None
    bb_sponsored_brand_solo_share_pct: Optional[float] = None
    bb_sponsored_brand_multi_posts: Optional[int] = None
    bb_sponsored_brand_multi_share_pct: Optional[float] = None
    bb_sponsored_brand_no_tag_posts: Optional[int] = None
    bb_sponsored_brand_no_tag_share_pct: Optional[float] = None
    bb_sponsored_co_mentions_top5: List[BrandCount] = Field(default_factory=list)
    brands_per_bb_post_avg: Optional[float] = None
    brands_per_sponsored_post_avg: Optional[float] = None
    brands_per_sponsored_bb_post_avg: Optional[float] = None


class FormatBlock(BaseModel):
    reels_total: Optional[int] = None
    reels_bb_total: Optional[int] = None
    reels_sponsored_total: Optional[int] = None
    reels_bb_sponsored_total: Optional[int] = None
    reels_share_total_pct: Optional[float] = None
    reels_share_bb_pct: Optional[float] = None
    reels_share_sponsored_pct: Optional[float] = None
    reels_share_bb_sponsored_pct: Optional[float] = None
    bb_share_in_sponsored_reels_pct: Optional[float] = None


class PerformanceMetric(BaseModel):
    bb_median: float
    nonbb_median: float
    bb_count: int
    nonbb_count: int


class PerformanceBlock(BaseModel):
    likes: Optional[PerformanceMetric] = None
    comments: Optional[PerformanceMetric] = None


class FormatPerfBlock(BaseModel):
    posts_total: int
    likes_median: Optional[float] = None
    likes_count: int
    comments_median: Optional[float] = None
    comments_count: int


class PerformanceFormatBlock(BaseModel):
    sponsored_reels: FormatPerfBlock
    sponsored_nonreels: FormatPerfBlock


class OriginBlock(BaseModel):
    bb_principal_posts: int
    bb_principal_share_pct: float
    bb_other_posts: int
    bb_other_owners_top: List[BrandCount] = Field(default_factory=list)


class Ledger(BaseModel):
    user: str
    periodo: str
    base: BaseBlock
    bb: Optional[BBBlock] = None
    bb_connection: Optional[BBConnectionBlock] = None
    monthly: Optional[MonthlyBlock] = None
    sponsored: Optional[SponsoredBlock] = None
    brands: Optional[BrandsBlock] = None
    branding: Optional[BrandingBlock] = None
    format: Optional[FormatBlock] = None
    performance: Optional[PerformanceBlock] = None
    performance_format: Optional[PerformanceFormatBlock] = None
    origin: Optional[OriginBlock] = None
    qa_notes: List[str] = Field(default_factory=list)
    omit_metrics: List[str] = Field(default_factory=list)


REWRITE_RULES = [
    (r"\bnao deve renovar\b", "nao ha indicacao de continuidade"),
    (r"\bdeve renovar\b", "nao ha recomendacao de continuidade"),
    (r"\bprecisa renovar\b", "nao ha recomendacao de continuidade"),
    (r"\brecomenda-se\b", "os dados sugerem"),
    (r"\brecomendo\b", "os dados sugerem"),
    (r"\brecomendamos\b", "os dados sugerem"),
    (r"\brecomenda\b", "os dados sugerem"),
    (r"\bvale a pena\b", "os dados sugerem"),
    (r"\bnao deve\b", "nao ha indicacao de"),
    (r"\bdeveria\b", "pode indicar"),
    (r"\bdeve\b", "pode indicar"),
    (r"\brenovacao\b", "continuidade"),
    (r"\brenovar\b", "prosseguir"),
    (r"\brenova\b", "prossegue"),
    (r"\bbenchmark\b", "comparacao"),
    (r"\bshare\b", "percentual"),
    (r"\bengajamento\b", "curtidas e comentarios"),
    (r"\bperformance\b", "resultado observado"),
    (r"\bkpi\b", "indicador"),
    (r"\bsucesso garantido\b", "resultado observado"),
    (r"\bsucesso\b", "resultado"),
    (r"\bfracasso\b", "resultado"),
    (r"\bexcelente\b", ""),
    (r"\botimo\b", ""),
    (r"\bfraco\b", ""),
    (r"\bruim\b", ""),
]


FORBIDDEN_TERMS = [rule[0] for rule in REWRITE_RULES]


def sanitize_text(text: str) -> str:
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    raw = re.sub(r"[ \t]+", " ", raw)
    lines = [line.strip() for line in raw.split("\n")]
    cleaned_lines = []
    empty_count = 0
    for line in lines:
        if not line:
            empty_count += 1
            if empty_count > 1:
                continue
            cleaned_lines.append("")
            continue
        empty_count = 0
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def rewrite_forbidden_terms(text: str) -> tuple[str, Sequence[str]]:
    rewritten = text
    applied: List[str] = []
    for pattern, replacement in REWRITE_RULES:
        if re.search(pattern, rewritten, flags=re.IGNORECASE):
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
            applied.append(pattern)
    return rewritten, applied


def detect_forbidden_terms(text: str) -> List[str]:
    found = []
    for pattern in FORBIDDEN_TERMS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(pattern)
    return found


def extract_json_from_text(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise SystemExit("Resposta JSON invalida do agente.")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise SystemExit("Resposta JSON invalida do agente.") from exc


def extract_content(output: Any) -> Any:
    if hasattr(output, "content"):
        content = output.content
    else:
        content = output
    if isinstance(content, BaseModel):
        return content.model_dump()
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        return extract_json_from_text(content)
    return content


def parse_bool_env(name: str) -> bool:
    raw = os.getenv(name, "").strip().lower()
    return raw in {"1", "true", "yes", "y", "sim"}


def build_model(
    model_id: str,
    endpoint: str,
    timeout: Optional[float],
    max_retries: Optional[int],
    max_tokens: Optional[int],
    temperature: Optional[float],
) -> OpenAIChat:
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip() or "https://api.openai.com/v1"
    reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", "").strip().lower() or None
    temp = temperature
    if model_id.strip().lower().startswith("gpt-5"):
        temp = None
    if endpoint == "responses":
        return OpenAIResponses(
            id=model_id,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            max_output_tokens=max_tokens,
            temperature=temp,
            reasoning_effort=reasoning_effort,
        )
    return OpenAIChat(
        id=model_id,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        max_tokens=max_tokens,
        temperature=temp,
        reasoning_effort=reasoning_effort,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Interpreta indicadores com agentes (Agno).")
    parser.add_argument("--input", required=True, help="Caminho do indicadores.json.")
    parser.add_argument("--out", default="out", help="Diretorio de saida.")
    parser.add_argument("--user", required=True, help="Handle principal (ex: @exemplo).")
    parser.add_argument(
        "--prompt-ledger",
        default=str(Path("prompts") / "agents" / "ledger_prompt.md"),
        help="Prompt do agente analista.",
    )
    parser.add_argument(
        "--prompt-writer",
        default=str(Path("prompts") / "agents" / "writer_prompt.md"),
        help="Prompt do agente redator.",
    )
    parser.add_argument(
        "--prompt-review",
        default=str(Path("prompts") / "agents" / "ptbr_review_prompt.md"),
        help="Prompt do agente revisor PT-BR.",
    )
    parser.add_argument(
        "--qa-config",
        default=str(Path("config") / "qa_thresholds.json"),
        help="Caminho do arquivo de thresholds de QA.",
    )
    parser.add_argument("--min-posts", type=int, help="Override do minimo de posts.")
    parser.add_argument("--min-coverage-likes", type=int, help="Override da cobertura minima de likes (percentual).")
    parser.add_argument("--min-coverage-comments", type=int, help="Override da cobertura minima de comments (percentual).")
    parser.add_argument("--min-coverage-views", type=int, help="Override da cobertura minima de views (percentual).")
    parser.add_argument("--model", help="Modelo base (default: OPENAI_MODEL ou gpt-5-mini).")
    parser.add_argument("--model-ledger", help="Modelo para o agente analista.")
    parser.add_argument("--model-writer", help="Modelo para o agente redator.")
    parser.add_argument("--model-review", help="Modelo para o agente revisor.")
    parser.add_argument("--timeout", type=int, help="Timeout em segundos para chamadas ao modelo.")
    parser.add_argument("--max-retries", type=int, help="Numero maximo de retries do cliente.")
    parser.add_argument("--max-output-ledger", type=int, help="Limite de tokens de saida do agente analista.")
    parser.add_argument("--max-output-writer", type=int, help="Limite de tokens de saida do agente redator.")
    parser.add_argument("--max-output-review", type=int, help="Limite de tokens de saida do agente revisor.")
    parser.add_argument("--temperature", type=float, help="Temperatura base (default: 0.2).")
    parser.add_argument(
        "--endpoint",
        choices=["chat", "responses"],
        help="Endpoint OpenAI a usar: chat (Chat Completions) ou responses (Responses API).",
    )
    args = parser.parse_args(argv)

    input_path = resolve_path(args.input, ROOT)
    if not input_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {input_path}")

    prompt_ledger_path = resolve_path(args.prompt_ledger, ROOT)
    prompt_writer_path = resolve_path(args.prompt_writer, ROOT)
    prompt_review_path = resolve_path(args.prompt_review, ROOT)
    for prompt_path in (prompt_ledger_path, prompt_writer_path, prompt_review_path):
        if not prompt_path.exists():
            raise SystemExit(f"Prompt nao encontrado: {prompt_path}")

    prompt_ledger = prompt_ledger_path.read_text(encoding="utf-8").strip()
    prompt_writer = prompt_writer_path.read_text(encoding="utf-8").strip()
    prompt_review = prompt_review_path.read_text(encoding="utf-8").strip()

    if not prompt_ledger or not prompt_writer or not prompt_review:
        raise SystemExit("Prompt vazio detectado.")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY nao definido no ambiente.")

    indicators = load_indicators(input_path)
    validate_indicators(indicators)
    sanitized = sanitize_indicators(indicators)
    periodo = build_period(indicators)

    qa_config_path = resolve_path(args.qa_config, ROOT)
    min_posts_override = parse_positive_int(args.min_posts, "--min-posts")
    min_posts = min_posts_override if min_posts_override is not None else load_min_posts_threshold(qa_config_path)
    posts_total = indicators.get("base", {}).get("posts_total") if isinstance(indicators.get("base"), dict) else None
    volume_status = "nao_disponivel"
    volume_warning = None
    if min_posts is None:
        volume_status = "nao_configurado"
    elif isinstance(posts_total, int):
        if posts_total >= min_posts:
            volume_status = "ok"
        else:
            volume_status = "baixo"
            volume_warning = f"Base insuficiente: {posts_total} posts (minimo {min_posts})."
            print(f"WARNING: {volume_warning}")
    else:
        volume_warning = "Total de posts nao informado."

    coverage_thresholds = load_coverage_thresholds(qa_config_path)
    likes_override = parse_positive_int(args.min_coverage_likes, "--min-coverage-likes", 100)
    comments_override = parse_positive_int(args.min_coverage_comments, "--min-coverage-comments", 100)
    views_override = parse_positive_int(args.min_coverage_views, "--min-coverage-views", 100)
    if likes_override is not None:
        coverage_thresholds["likes"] = likes_override
    if comments_override is not None:
        coverage_thresholds["comments"] = comments_override
    if views_override is not None:
        coverage_thresholds["views"] = views_override
    coverage_payload = indicators.get("coverage") if isinstance(indicators.get("coverage"), dict) else {}
    coverage_status: Dict[str, Dict[str, Any]] = {}
    for metric, min_pct in coverage_thresholds.items():
        key = f"{metric}_coverage_pct"
        value = coverage_payload.get(key)
        if isinstance(value, (int, float)):
            status = "ok" if value >= min_pct else "baixo"
        else:
            status = "nao_disponivel"
        coverage_status[metric] = {"coverage_pct": value, "min_pct": min_pct, "status": status}
        if status == "baixo":
            print(f"WARNING: cobertura baixa para {metric}: {value}% (minimo {min_pct}%).")

    qa_notes: List[str] = []
    if volume_status == "baixo" and volume_warning:
        qa_notes.append("Aviso: base abaixo do volume minimo definido; interpretacao pode ser menos robusta.")
    low_coverage = [m for m, info in coverage_status.items() if info.get("status") == "baixo"]
    if low_coverage:
        qa_notes.append("Aviso: ha metricas com cobertura baixa de dados, o que limita comparacoes.")

    model_default = (args.model or os.getenv("OPENAI_MODEL", "").strip()) or "gpt-5-mini"
    model_ledger = args.model_ledger or model_default
    model_writer = args.model_writer or model_default
    model_review = args.model_review or model_default

    timeout = args.timeout if args.timeout is not None else None
    max_retries = args.max_retries if args.max_retries is not None else None

    temp = args.temperature if args.temperature is not None else 0.2
    endpoint = (args.endpoint or os.getenv("OPENAI_ENDPOINT", "chat")).strip().lower()
    if endpoint not in {"chat", "responses"}:
        raise SystemExit("OPENAI_ENDPOINT invalido. Use 'responses' ou 'chat'.")

    ledger_model = build_model(model_ledger, endpoint, timeout, max_retries, args.max_output_ledger, temperature=0.1)
    writer_model = build_model(model_writer, endpoint, timeout, max_retries, args.max_output_writer, temperature=temp)
    review_model = build_model(model_review, endpoint, timeout, max_retries, args.max_output_review, temperature=0.05)

    ledger_agent = Agent(name="analista", model=ledger_model, instructions=prompt_ledger)
    writer_agent = Agent(name="redator", model=writer_model, instructions=prompt_writer)
    review_agent = Agent(name="revisor_ptbr", model=review_model, instructions=prompt_review)

    ledger_input = {
        "user": args.user,
        "periodo": periodo,
        "qa": {
            "min_posts": min_posts,
            "volume_status": volume_status,
            "coverage_status": coverage_status,
        },
        "indicators": sanitized,
    }
    ledger_payload = json.dumps(ledger_input, ensure_ascii=False)
    print("Agente analista: iniciando.")
    ledger_output = ledger_agent.run(ledger_payload, output_schema=Ledger)
    print("Agente analista: concluido.")
    ledger = extract_content(ledger_output)

    print("Agente redator: iniciando.")
    writer_input = {
        "user": args.user,
        "periodo": periodo,
        "ledger": ledger,
        "qa_notes": qa_notes,
    }
    writer_payload = json.dumps(writer_input, ensure_ascii=False)
    writer_output = writer_agent.run(writer_payload)
    print("Agente redator: concluido.")
    draft_text = writer_output.content if hasattr(writer_output, "content") else str(writer_output)
    if not isinstance(draft_text, str):
        draft_text = str(draft_text)

    print("Agente revisor PT-BR: iniciando.")
    review_output = review_agent.run(draft_text)
    print("Agente revisor PT-BR: concluido.")
    reviewed_text = review_output.content if hasattr(review_output, "content") else str(review_output)
    if not isinstance(reviewed_text, str):
        reviewed_text = str(reviewed_text)

    final_text = sanitize_text(reviewed_text)
    final_text, rewrites = rewrite_forbidden_terms(final_text)
    violations = detect_forbidden_terms(final_text)

    if qa_notes and not all(note in final_text for note in qa_notes):
        final_text = final_text + "\n\n" + " ".join(qa_notes)

    out_dir = resolve_path(args.out, ROOT)
    out_dir.mkdir(parents=True, exist_ok=True)

    texto_path = out_dir / "texto_relatorio.md"
    ledger_path = out_dir / "ledger.json"
    meta_path = out_dir / "interpretation.json"
    qa_path = out_dir / "qa.json"

    generated_at = datetime.now(timezone.utc).isoformat()

    extra_checks: Dict[str, Any] = {}
    other_posts = None
    if isinstance(ledger, dict):
        base = ledger.get("base") if isinstance(ledger.get("base"), dict) else None
        if isinstance(base, dict):
            other_posts = base.get("other_posts")
        if isinstance(other_posts, int) and other_posts > 0:
            has_repost = bool(re.search(r"repost|republica", final_text, flags=re.IGNORECASE))
            extra_checks["reposts_mencionado"] = "ok" if has_repost else "warn"

    has_source_terms = bool(re.search(r"\b(arquivo|coluna|indicadores\.json)\b", final_text, flags=re.IGNORECASE))
    extra_checks["sem_fontes_tecnicas"] = "ok" if not has_source_terms else "warn"

    meta_payload = {
        "timestamp": generated_at,
        "input_path": str(input_path),
        "prompt_ledger": str(prompt_ledger_path),
        "prompt_writer": str(prompt_writer_path),
        "prompt_review": str(prompt_review_path),
        "models": {
            "ledger": model_ledger,
            "writer": model_writer,
            "review": model_review,
        },
        "qa_notes": qa_notes,
        "reescritas_aplicadas": rewrites,
        "termos_proibidos": violations,
    }

    qa_payload = {
        "timestamp": generated_at,
        "min_posts": min_posts,
        "posts_total": posts_total,
        "volume_status": volume_status,
        "volume_warning": volume_warning,
        "coverage_status": coverage_status,
        "checks": extra_checks,
    }

    texto_path.write_text(final_text.strip() + "\n", encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa_path.write_text(json.dumps(qa_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Input: {input_path}")
    print(f"Out: {out_dir}")
    print(f"Output texto: {texto_path}")
    print(f"Output ledger: {ledger_path}")
    print(f"Output metadata: {meta_path}")
    print(f"Output QA: {qa_path}")
    print(f"User: {args.user}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
