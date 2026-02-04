"""Data health scoring for events."""

from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from app.models.models import now_utc

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "base_fields": {
        "nome": 3,
        "cidade": 6,
        "estado": 6,
        "data_inicio_prevista": 8,
        "data_fim_prevista": 6,
        "descricao": 2,
        "diretoria_id": 9,
        "gestor_id": 6,
        "tipo_id": 5,
        "status_id": 4,
        "divisao_demandante_id": 4,
        "investimento": 14,
        "concorrencia": 2,
        "publico_projetado": 6,
        "agencia_id": 14,
        "territorio_ids": 3,
        "tag_ids": 3,
        "thumbnail": 4,
        "qr_code_url": 2,
    },
    "conditional_fields": {
        "subtipo_id": {"weight": 3, "applies_when": "tipo_id_present"},
    },
    "post_event_fields": {
        "data_inicio_realizada": 4,
        "data_fim_realizada": 4,
        "publico_realizado": 6,
    },
    "urgency": {
        "date_field": "data_inicio_prevista",
        "tiers": [
            {"max_days": 7, "factor": 0.7},
            {"max_days": 30, "factor": 0.85},
            {"max_days": 90, "factor": 0.95},
            {"max_days": None, "factor": 1.0},
        ],
        "no_date_factor": 1.0,
        "past_event_factor": 1.0,
        "complete_score_factor_override": 1.0,
    },
    "exceptions": {"status_cancelado": "N/A", "status_arquivado": "N/A"},
}


@lru_cache(maxsize=1)
def _load_config() -> dict[str, Any]:
    config_path = Path(__file__).resolve().parents[2] / "docs" / "eventos_saude_dados_config.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_CONFIG
    return data


def _safe_get(source: Any, field: str) -> Any:
    if isinstance(source, dict):
        return source.get(field)
    return getattr(source, field, None)


def _is_missing(field: str, value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    if isinstance(value, bool):
        return False
    return False


def _humanize_field(field: str) -> str:
    return field.replace("_", " ").strip().capitalize()


def _score_to_band(score: int | None) -> str:
    if score is None:
        return "na"
    if score <= 33:
        return "critical"
    if score <= 50:
        return "low"
    if score <= 75:
        return "medium"
    if score <= 90:
        return "high"
    return "excellent"


def _status_exception(status_name: str | None, config: dict[str, Any]) -> bool:
    if not status_name:
        return False
    status_key = status_name.strip().lower()
    exceptions = config.get("exceptions", {})
    for key, value in exceptions.items():
        if not isinstance(key, str):
            continue
        if key.startswith("status_") and key.replace("status_", "") == status_key:
            return str(value).strip().lower() == "n/a"
    return False


def _urgency_factor(event_date: date | None, config: dict[str, Any]) -> float:
    urgency = config.get("urgency", {})
    if not event_date:
        return float(urgency.get("no_date_factor", 1.0))
    days = (event_date - date.today()).days
    if days < 0:
        return float(urgency.get("past_event_factor", 1.0))
    for tier in urgency.get("tiers", []):
        max_days = tier.get("max_days")
        if max_days is None or days <= int(max_days):
            return float(tier.get("factor", 1.0))
    return 1.0


def _collect_missing_fields(
    evento: Any, status_name: str | None, config: dict[str, Any]
) -> list[tuple[str, int]]:
    missing: list[tuple[str, int]] = []

    for field, weight in config.get("base_fields", {}).items():
        value = _safe_get(evento, field)
        if _is_missing(field, value):
            missing.append((field, int(weight)))

    for field, rule in config.get("conditional_fields", {}).items():
        applies_when = rule.get("applies_when")
        if applies_when == "tipo_id_present":
            tipo_value = _safe_get(evento, "tipo_id")
            if _is_missing("tipo_id", tipo_value):
                continue
        weight = int(rule.get("weight", 0))
        value = _safe_get(evento, field)
        if _is_missing(field, value):
            missing.append((field, weight))

    if status_name and status_name.strip().lower() == "realizado":
        for field, weight in config.get("post_event_fields", {}).items():
            value = _safe_get(evento, field)
            if _is_missing(field, value):
                missing.append((field, int(weight)))

    missing.sort(key=lambda item: (-item[1], item[0]))
    return missing


def compute_event_data_health(evento: Any, status_name: str | None = None) -> dict[str, Any]:
    config = _load_config()
    version = int(config.get("version", 1))

    if _status_exception(status_name, config):
        return {
            "version": version,
            "score": None,
            "band": "na",
            "missing_fields": [],
            "filled_weight": 0,
            "total_weight": 0,
            "urgency_factor": 1.0,
            "last_calculated_at": now_utc(),
        }

    missing = _collect_missing_fields(evento, status_name, config)
    missing_fields = [field for field, _ in missing]

    total_weight = 0
    filled_weight = 0
    for field, weight in config.get("base_fields", {}).items():
        total_weight += int(weight)
        if not _is_missing(field, _safe_get(evento, field)):
            filled_weight += int(weight)

    for field, rule in config.get("conditional_fields", {}).items():
        applies_when = rule.get("applies_when")
        if applies_when == "tipo_id_present":
            if _is_missing("tipo_id", _safe_get(evento, "tipo_id")):
                continue
        weight = int(rule.get("weight", 0))
        total_weight += weight
        if not _is_missing(field, _safe_get(evento, field)):
            filled_weight += weight

    if status_name and status_name.strip().lower() == "realizado":
        for field, weight in config.get("post_event_fields", {}).items():
            total_weight += int(weight)
            if not _is_missing(field, _safe_get(evento, field)):
                filled_weight += int(weight)

    score = None
    urgency_factor = 1.0
    if total_weight > 0:
        base_score = filled_weight / total_weight
        date_field = config.get("urgency", {}).get("date_field", "data_inicio_prevista")
        raw_date = _safe_get(evento, date_field)
        if isinstance(raw_date, datetime):
            event_date = raw_date.date()
        else:
            event_date = raw_date if isinstance(raw_date, date) else None
        urgency_factor = _urgency_factor(event_date, config)
        if base_score >= 1:
            urgency_factor = float(
                config.get("urgency", {}).get("complete_score_factor_override", urgency_factor)
            )
        score = int(max(0, min(100, round(base_score * urgency_factor * 100))))

    return {
        "version": version,
        "score": score,
        "band": _score_to_band(score),
        "missing_fields": missing_fields,
        "filled_weight": filled_weight,
        "total_weight": total_weight,
        "urgency_factor": urgency_factor,
        "last_calculated_at": now_utc(),
    }


def compute_event_missing_fields_details(
    evento: Any, status_name: str | None = None
) -> list[dict[str, Any]]:
    config = _load_config()
    missing = _collect_missing_fields(evento, status_name, config)
    details: list[dict[str, Any]] = []
    for field, weight in missing:
        if weight >= 10:
            priority = "high"
        elif weight >= 5:
            priority = "medium"
        else:
            priority = "low"
        details.append(
            {
                "field": field,
                "label": _humanize_field(field),
                "weight": weight,
                "priority": priority,
            }
        )
    return details
