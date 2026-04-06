#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple


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
    raw = (value or "").strip()
    if not raw:
        return None
    raw = raw.lstrip("@").strip().lower()
    return raw or None


def sanitize_label(value: Optional[str]) -> Optional[str]:
    raw = (value or "").strip().lower()
    if not raw:
        return None
    safe = re.sub(r"[^a-z0-9._-]+", "_", raw).strip("_")
    return safe or None


def load_handle_map(root: Path) -> Dict[str, str]:
    path = root / "config" / "instagram_handles.csv"
    if not path.exists():
        return {}
    mapping: Dict[str, str] = {}
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not isinstance(row, dict):
                    continue
                raw_handle = row.get("handle")
                raw_name = row.get("name")
                handle_norm = normalize_handle(raw_handle)
                name = (raw_name or "").strip()
                if handle_norm and name:
                    mapping[handle_norm] = name
    except OSError:
        return {}
    return mapping


def resolve_indicators_input(path: Path, root: Path) -> Path:
    if path.exists():
        return path
    if path.name != "indicadores.json":
        return path

    handle = normalize_handle(path.parent.name)
    if not handle:
        return path

    out_root = path.parent.parent
    if not out_root.exists():
        fallback_root = root / "out"
        out_root = fallback_root if fallback_root.exists() else out_root

    handle_map = load_handle_map(root)
    candidates: List[str] = []
    safe_handle = sanitize_label(handle) or handle
    candidates.append(safe_handle)
    athlete_name = handle_map.get(handle)
    athlete_dir = sanitize_label(athlete_name)
    if athlete_dir:
        candidates.append(athlete_dir)

    for candidate in candidates:
        alt = out_root / candidate / "indicadores.json"
        if alt.exists():
            print(f"WARNING: arquivo nao encontrado em {path}; usando {alt}")
            return alt

    return path


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


def get_nested(payload: Dict[str, Any], path: str) -> Tuple[bool, Any]:
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


def build_prompt(prompt_text: str, indicators: Dict[str, Any], user: str, input_path: Path) -> str:
    periodo = build_period(indicators)
    origem = f"indicadores gerados a partir de {input_path.name}"
    indicators_json = json.dumps(indicators, ensure_ascii=True)
    return (
        prompt_text.strip()
        + "\n\n"
        + "Contexto:\n"
        + f"user: {user}\n"
        + f"periodo: {periodo}\n"
        + f"origem: {origem}\n"
        + f"indicadores_json: {indicators_json}\n"
    )


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


class TextProvider(Protocol):
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError


class MockProvider:
    def generate_text(self, prompt: str) -> str:
        _ = prompt
        return "Texto executivo ainda nao disponivel. Provider mock em uso."


def extract_text_from_response(payload: Dict[str, Any]) -> Optional[str]:
    if isinstance(payload.get("output_text"), str):
        return payload.get("output_text")
    output = payload.get("output")
    if isinstance(output, list):
        for item in output:
            content = item.get("content") if isinstance(item, dict) else None
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    return part.get("text")
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message.get("content")
            if isinstance(first.get("text"), str):
                return first.get("text")
    return None


class OpenAIProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout: int,
        retries: int,
        retry_backoff: float,
        prefer_chat: bool,
        background: bool,
        poll_interval: float,
        max_wait: Optional[int],
        reasoning_effort: Optional[str],
        max_output_tokens: Optional[int],
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff = retry_backoff
        self.prefer_chat = prefer_chat
        self.background = background
        self.poll_interval = poll_interval
        self.max_wait = max_wait
        self.reasoning_effort = reasoning_effort
        self.max_output_tokens = max_output_tokens
        self.endpoint = "chat" if prefer_chat else "responses"

    def _format_http_error(self, exc: urllib.error.HTTPError) -> str:
        detail = ""
        try:
            raw = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            raw = ""
        if raw:
            try:
                payload = json.loads(raw)
                if isinstance(payload, dict):
                    err = payload.get("error")
                    if isinstance(err, dict):
                        msg = err.get("message")
                        if isinstance(msg, str) and msg.strip():
                            detail = msg.strip()
            except json.JSONDecodeError:
                detail = raw.strip()
        if detail:
            return f"HTTP {exc.code}: {detail}"
        return f"HTTP {exc.code}"

    def _extract_error_message(self, payload: Dict[str, Any]) -> Optional[str]:
        for key in ("error", "last_error"):
            value = payload.get(key)
            if isinstance(value, dict):
                message = value.get("message") if isinstance(value.get("message"), str) else None
                code = value.get("code") if isinstance(value.get("code"), str) else None
                error_type = value.get("type") if isinstance(value.get("type"), str) else None
                parts = [p for p in [message, code, error_type] if p]
                if parts:
                    return " - ".join(parts)
            elif isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _request_json(self, url: str, payload: Optional[Dict[str, Any]], method: str) -> str:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        last_error: Optional[BaseException] = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.read().decode("utf-8", errors="ignore")
            except urllib.error.HTTPError as exc:
                last_error = exc
                retryable = exc.code in {408, 429, 500, 502, 503, 504}
                if retryable and attempt < self.retries:
                    wait_s = self.retry_backoff * (2**attempt)
                    print(f"WARNING: falha HTTP {exc.code} no provider openai. Tentando novamente em {wait_s:.1f}s.")
                    time.sleep(wait_s)
                    continue
                raise
            except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
                last_error = exc
                if attempt < self.retries:
                    wait_s = self.retry_backoff * (2**attempt)
                    print(
                        "WARNING: timeout/erro de rede no provider openai. Tentando novamente em "
                        f"{wait_s:.1f}s."
                    )
                    time.sleep(wait_s)
                    continue
                raise
        if last_error is not None:
            raise last_error
        raise RuntimeError("Falha inesperada no provider openai.")

    def _poll_response(self, response_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/responses/{response_id}"
        start = time.time()
        while True:
            raw = self._request_json(url, None, "GET")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit("Resposta invalida do provider openai.") from exc

            status = data.get("status")
            if extract_text_from_response(data):
                return data
            if status in {"completed", "succeeded"}:
                return data
            if status in {"failed", "cancelled", "expired"}:
                detail = self._extract_error_message(data)
                if detail:
                    raise SystemExit(f"Falha no provider openai (status {status}): {detail}")
                raise SystemExit(f"Falha no provider openai (status {status}).")
            if self.max_wait is not None and self.max_wait > 0:
                if time.time() - start > self.max_wait:
                    raise SystemExit("Falha no provider openai (timeout aguardando resposta).")
            time.sleep(self.poll_interval)

    def generate_text(self, prompt: str) -> str:
        responses_url = f"{self.base_url}/responses"
        responses_payload: Dict[str, Any] = {"model": self.model, "input": prompt}
        if self.reasoning_effort:
            responses_payload["reasoning"] = {"effort": self.reasoning_effort}
        if self.max_output_tokens:
            responses_payload["max_output_tokens"] = self.max_output_tokens
        if self.background:
            responses_payload["background"] = True
        chat_url = f"{self.base_url}/chat/completions"
        chat_payload: Dict[str, Any] = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        if self.max_output_tokens:
            chat_payload["max_tokens"] = self.max_output_tokens

        raw = None
        if self.prefer_chat:
            try:
                raw = self._request_json(chat_url, chat_payload, "POST")
                self.endpoint = "chat"
            except urllib.error.HTTPError as exc:
                raise SystemExit(f"Falha no provider openai ({self._format_http_error(exc)}).") from exc
            except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
                raise SystemExit(f"Falha no provider openai (timeout ou erro de rede): {exc}") from exc
        else:
            try:
                raw = self._request_json(responses_url, responses_payload, "POST")
                self.endpoint = "responses"
            except urllib.error.HTTPError as exc:
                fallback_http = exc.code in {404, 405, 415}
                if fallback_http:
                    print(
                        f"WARNING: endpoint /responses retornou {self._format_http_error(exc)}. Tentando /chat/completions."
                    )
                else:
                    raise SystemExit(f"Falha no provider openai ({self._format_http_error(exc)}).") from exc
            except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
                print(
                    "WARNING: falha no endpoint /responses. Tentando /chat/completions."
                )
            if raw is None:
                try:
                    raw = self._request_json(chat_url, chat_payload, "POST")
                    self.endpoint = "chat"
                except urllib.error.HTTPError as exc:
                    raise SystemExit(
                        f"Falha no provider openai ({self._format_http_error(exc)}) ao tentar /chat/completions."
                    ) from exc
                except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
                    raise SystemExit(
                        f"Falha no provider openai (timeout ou erro de rede) ao tentar /chat/completions: {exc}"
                    ) from exc

        if raw is None:
            raise SystemExit("Falha no provider openai (sem resposta).")

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit("Resposta invalida do provider openai.") from exc

        if self.endpoint == "responses":
            response_id = data.get("id")
            status = data.get("status")
            if self.background and response_id:
                data = self._poll_response(response_id)
            elif status in {"queued", "in_progress"} and response_id:
                data = self._poll_response(response_id)
            elif status in {"failed", "cancelled", "expired"}:
                detail = self._extract_error_message(data)
                if detail:
                    raise SystemExit(f"Falha no provider openai (status {status}): {detail}")
                raise SystemExit(f"Falha no provider openai (status {status}).")

        text = extract_text_from_response(data)
        if not text:
            raise SystemExit("Resposta vazia do provider openai.")
        return text


def read_env_int(name: str, default: int, allow_zero: bool = False) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit(f"Valor invalido em {name}: {raw}") from exc
    if allow_zero:
        if value < 0:
            raise SystemExit(f"Valor invalido em {name}: {value}. Use inteiro >= 0.")
    elif value <= 0:
        raise SystemExit(f"Valor invalido em {name}: {value}. Use inteiro > 0.")
    return value


def read_env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise SystemExit(f"Valor invalido em {name}: {raw}") from exc
    if value <= 0:
        raise SystemExit(f"Valor invalido em {name}: {value}. Use numero > 0.")
    return value


def resolve_provider(
    name: str,
    timeout: int,
    retries: int,
    retry_backoff: float,
    endpoint: Optional[str],
    background: bool,
    poll_interval: float,
    max_wait: Optional[int],
    reasoning_effort: Optional[str],
    max_output_tokens: Optional[int],
) -> TextProvider:
    key = (name or "").strip().lower()
    if key in {"mock", "none"}:
        return MockProvider()
    if key == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise SystemExit("OPENAI_API_KEY nao definido no ambiente.")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip() or "https://api.openai.com/v1"
        prefer_chat = False
        endpoint_choice = (endpoint or os.getenv("OPENAI_ENDPOINT", "")).strip().lower()
        if endpoint_choice:
            if endpoint_choice not in {"responses", "chat"}:
                raise SystemExit("OPENAI_ENDPOINT invalido. Use 'responses' ou 'chat'.")
            prefer_chat = endpoint_choice == "chat"
        return OpenAIProvider(
            api_key,
            model,
            base_url,
            timeout,
            retries,
            retry_backoff,
            prefer_chat,
            background,
            poll_interval,
            max_wait,
            reasoning_effort,
            max_output_tokens,
        )
    raise SystemExit(f"Provider invalido: {name}. Use 'mock' ou 'openai'.")


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


def detect_forbidden_terms(text: str) -> Sequence[str]:
    found = []
    for pattern in FORBIDDEN_TERMS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(pattern)
    return found


def rewrite_forbidden_terms(text: str) -> Tuple[str, Sequence[str]]:
    rewritten = text
    applied: List[str] = []
    for pattern, replacement in REWRITE_RULES:
        if re.search(pattern, rewritten, flags=re.IGNORECASE):
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
            applied.append(pattern)
    return rewritten, applied


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


LINGUISTIC_JARGON = [
    "benchmark",
    "share",
    "engajamento",
    "performance",
    "kpi",
]

CAUSAL_MARKERS = [
    "por causa de",
    "isso prova",
    "isso demonstra",
    "isso indica que",
    "evidencia que",
]


def find_terms(text: str, terms: Sequence[str]) -> List[str]:
    found: List[str] = []
    lowered = text.lower()
    for term in terms:
        if term in lowered:
            found.append(term)
    return found


def has_markdown_table(text: str) -> bool:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|") and "|" in line[1:-1]:
            return True
    return False


def has_bullet_list(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            return True
    return False


def build_linguistic_checklist(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    items: List[Dict[str, Any]] = []

    has_table = has_markdown_table(text)
    has_list = has_bullet_list(text)
    items.append(
        {
            "id": "sem_tabelas_listas",
            "status": "ok" if not (has_table or has_list) else "warn",
            "details": "Sem tabelas/listas detectadas." if not (has_table or has_list) else "Tabela ou lista encontrada.",
        }
    )

    forbidden = detect_forbidden_terms(text)
    items.append(
        {
            "id": "sem_recomendacoes_explicitas",
            "status": "ok" if not forbidden else "warn",
            "details": "Sem termos proibidos." if not forbidden else f"Termos detectados: {', '.join(forbidden)}.",
        }
    )

    jargon_found = find_terms(text, LINGUISTIC_JARGON)
    items.append(
        {
            "id": "sem_jargao_sem_explicacao",
            "status": "ok" if not jargon_found else "warn",
            "details": "Sem jargao detectado." if not jargon_found else f"Jargao detectado: {', '.join(jargon_found)}.",
        }
    )

    causal_found = find_terms(text, CAUSAL_MARKERS)
    items.append(
        {
            "id": "sem_causa_efeito",
            "status": "ok" if not causal_found else "warn",
            "details": "Sem linguagem causal detectada." if not causal_found else f"Linguagem causal: {', '.join(causal_found)}.",
        }
    )

    has_bb = "bb" in lowered or "banco do brasil" in lowered
    has_bb_explicit = "banco do brasil (bb)" in lowered
    if not has_bb:
        status = "na"
        details = "Sem mencoes ao BB no texto."
    else:
        status = "ok" if has_bb_explicit else "warn"
        details = "Primeira mencao inclui Banco do Brasil (BB)." if has_bb_explicit else "Nao inclui Banco do Brasil (BB) na primeira mencao."
    items.append({"id": "bb_explicitado", "status": status, "details": details})

    if "mediana" in lowered:
        has_expl = "intervalo mais tipico" in lowered
        status = "ok" if has_expl else "warn"
        details = "Mediana explicada em linguagem simples." if has_expl else "Mediana sem explicacao simples."
    else:
        status = "na"
        details = "Sem uso de mediana."
    items.append({"id": "mediana_explicada", "status": status, "details": details})

    media_match = re.search(r"\bmedia\b", lowered)
    if media_match:
        has_expl = "media geral" in lowered
        status = "ok" if has_expl else "warn"
        details = "Media explicada em linguagem simples." if has_expl else "Media sem explicacao simples."
    else:
        status = "na"
        details = "Sem uso de media."
    items.append({"id": "media_explicada", "status": status, "details": details})

    has_percent = "%" in text or "percentual" in lowered or "por cento" in lowered
    if not has_percent:
        status = "na"
        details = "Sem percentuais no texto."
    else:
        explained = bool(re.search(r"(a|em) cada 100", lowered) or "por cento" in lowered)
        status = "ok" if explained else "warn"
        details = "Percentual explicado em termos simples." if explained else "Percentual sem explicacao simples."
    items.append({"id": "percentual_explicado", "status": status, "details": details})

    needs_base = bool(re.search(r"\bmediana\b|\bmedia\b|%|percentual", lowered))
    if not needs_base:
        status = "na"
        details = "Sem metricas que exijam base."
    else:
        status = "ok" if "com base" in lowered else "warn"
        details = "Base informada para metricas." if "com base" in lowered else "Base nao informada para metricas."
    items.append({"id": "base_informada", "status": status, "details": details})

    warnings = sum(1 for item in items if item["status"] == "warn")
    summary_status = "ok" if warnings == 0 else "warn"
    return {"summary": {"status": summary_status, "warnings": warnings}, "items": items}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Interpreta indicadores e gera texto executivo.")
    parser.add_argument("--input", required=True, help="Caminho do indicadores.json.")
    parser.add_argument("--out", default="out", help="Diretorio de saida.")
    parser.add_argument("--provider", default="mock", help="Provider do interpretador (ex: mock).")
    parser.add_argument(
        "--prompt",
        default=str(Path("prompts") / "exec_summary_prompt.md"),
        help="Caminho do prompt base.",
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
    parser.add_argument("--user", required=True, help="Handle principal (ex: @exemplo).")
    parser.add_argument("--timeout", type=int, help="Timeout em segundos para chamadas ao provider.")
    parser.add_argument("--retries", type=int, help="Numero de tentativas em caso de falha de rede.")
    parser.add_argument("--retry-backoff", type=float, help="Backoff base (segundos) entre tentativas.")
    parser.add_argument("--endpoint", help="Endpoint OpenAI: responses ou chat (override de OPENAI_ENDPOINT).")
    parser.add_argument("--background", action="store_true", help="Usa background mode no Responses API.")
    parser.add_argument("--poll-interval", type=float, help="Intervalo (segundos) para polling em background.")
    parser.add_argument("--max-wait", type=int, help="Tempo maximo (segundos) para aguardar resposta em background.")
    parser.add_argument(
        "--reasoning-effort",
        choices=["medium", "high", "xhigh"],
        help="Nivel de effort para modelos com suporte a reasoning.effort.",
    )
    parser.add_argument("--max-output-tokens", type=int, help="Limite de tokens de saida (Responses/Chat).")
    args = parser.parse_args(argv)

    input_path = resolve_path(args.input, ROOT)
    input_path = resolve_indicators_input(input_path, ROOT)
    if not input_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {input_path}")

    prompt_path = resolve_path(args.prompt, ROOT)
    if not prompt_path.exists():
        raise SystemExit(f"Prompt nao encontrado: {prompt_path}")
    try:
        prompt_text = prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Falha ao ler prompt: {prompt_path}") from exc
    if not prompt_text.strip():
        raise SystemExit(f"Prompt vazio: {prompt_path}")

    indicators = load_indicators(input_path)
    validate_indicators(indicators)

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

    final_prompt = build_prompt(prompt_text, indicators, args.user, input_path)
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
    print(f"QA: volume_status={volume_status}, posts_total={posts_total}, min_posts={min_posts}")
    for metric, info in coverage_status.items():
        print(
            "QA: coverage_{0}={1}% (min {2}%) status={3}".format(
                metric,
                info.get("coverage_pct"),
                info.get("min_pct"),
                info.get("status"),
            )
        )
    provider_name = (args.provider or "").strip().lower()
    timeout = (
        parse_positive_int(args.timeout, "--timeout") if args.timeout is not None else read_env_int("OPENAI_TIMEOUT", 60)
    )
    if args.retries is not None:
        if args.retries < 0:
            raise SystemExit("Valor invalido em --retries. Use inteiro >= 0.")
        retries = args.retries
    else:
        retries = read_env_int("OPENAI_RETRIES", 2, allow_zero=True)
    if args.retry_backoff is not None:
        if args.retry_backoff <= 0:
            raise SystemExit("Valor invalido em --retry-backoff. Use numero > 0.")
        retry_backoff = float(args.retry_backoff)
    else:
        retry_backoff = read_env_float("OPENAI_RETRY_BACKOFF", 2.0)

    def parse_bool_env(name: str) -> bool:
        raw = os.getenv(name, "").strip().lower()
        return raw in {"1", "true", "yes", "y", "sim"}

    background = args.background or parse_bool_env("OPENAI_BACKGROUND")
    poll_interval = args.poll_interval if args.poll_interval is not None else read_env_float("OPENAI_POLL_INTERVAL", 5.0)
    max_wait = args.max_wait if args.max_wait is not None else read_env_int("OPENAI_MAX_WAIT", 900, allow_zero=True)
    reasoning_effort = args.reasoning_effort or os.getenv("OPENAI_REASONING_EFFORT", "").strip().lower() or None
    if reasoning_effort and reasoning_effort not in {"medium", "high", "xhigh"}:
        raise SystemExit("OPENAI_REASONING_EFFORT invalido. Use medium, high ou xhigh.")
    max_output_tokens = None
    if args.max_output_tokens is not None:
        max_output_tokens = parse_positive_int(args.max_output_tokens, "--max-output-tokens")
    else:
        env_max_output = os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "").strip()
        if env_max_output:
            try:
                env_val = int(env_max_output)
            except ValueError as exc:
                raise SystemExit(f"Valor invalido em OPENAI_MAX_OUTPUT_TOKENS: {env_max_output}") from exc
            if env_val <= 0:
                raise SystemExit("OPENAI_MAX_OUTPUT_TOKENS invalido. Use inteiro > 0.")
            max_output_tokens = env_val

    provider = resolve_provider(
        provider_name,
        timeout,
        retries,
        retry_backoff,
        args.endpoint,
        background,
        poll_interval,
        max_wait,
        reasoning_effort,
        max_output_tokens,
    )
    generated_text = sanitize_text(provider.generate_text(final_prompt))
    generated_text, rewrites = rewrite_forbidden_terms(generated_text)
    violations = detect_forbidden_terms(generated_text)
    has_violation = len(violations) > 0
    has_rewrite = len(rewrites) > 0
    fallback_used = provider_name in {"mock", "none"}
    if rewrites:
        print(f"INFO: reescritas aplicadas: {', '.join(rewrites)}")
    if has_violation:
        print(f"WARNING: termos proibidos detectados: {', '.join(violations)}")

    out_dir = resolve_path(args.out, ROOT)
    out_dir.mkdir(parents=True, exist_ok=True)

    texto_path = out_dir / "texto_relatorio.md"
    meta_path = out_dir / "interpretation.json"
    qa_path = out_dir / "qa.json"
    generated_at = datetime.now(timezone.utc).isoformat()

    qa_notes: List[str] = []
    alerts: List[str] = []
    if volume_status == "baixo" and volume_warning:
        qa_notes.append("Aviso: base abaixo do volume minimo definido; interpretacao pode ser menos robusta.")
        alerts.append("volume_baixo")
    low_coverage = [m for m, info in coverage_status.items() if info.get("status") == "baixo"]
    if low_coverage:
        qa_notes.append("Aviso: ha metricas com cobertura baixa de dados, o que limita comparacoes.")
        alerts.append("cobertura_baixa")

    meta_payload = {
        "provider": args.provider,
        "model": getattr(provider, "model", None),
        "endpoint": getattr(provider, "endpoint", None),
        "background": getattr(provider, "background", None),
        "timestamp": generated_at,
        "input_path": str(input_path),
        "prompt_path": str(prompt_path),
        "prompt": final_prompt,
        "violacao": has_violation,
        "reescrita": has_rewrite,
        "fallback": fallback_used,
        "termos_proibidos": violations,
        "reescritas_aplicadas": rewrites,
        "coverage_status": coverage_status,
        "alerts": alerts,
    }
    qa_payload = {
        "timestamp": generated_at,
        "min_posts": min_posts,
        "posts_total": posts_total,
        "volume_status": volume_status,
        "volume_warning": volume_warning,
        "coverage_status": coverage_status,
    }

    final_text = generated_text.strip()
    if qa_notes:
        final_text = final_text + "\n\n" + " ".join(qa_notes)

    checklist = build_linguistic_checklist(final_text)
    qa_payload["linguistic_checklist"] = checklist

    texto_path.write_text(final_text.strip() + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    qa_path.write_text(json.dumps(qa_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print(f"Input: {input_path}")
    print(f"Out: {out_dir}")
    print(f"Output texto: {texto_path}")
    print(f"Output metadata: {meta_path}")
    print(f"Output QA: {qa_path}")
    print(f"Provider: {args.provider}")
    print(f"Prompt: {prompt_path}")
    print(f"User: {args.user}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
