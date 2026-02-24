"""Alert rules for ETL observability signals (health + coverage).

This module converts operational signals into actionable alerts covering:
- partial ingestions;
- drift symptoms (missing metrics / unresolved session mapping);
- missing required datasets per session.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


_SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class Alert:
    """One actionable observability alert.

    Args:
        code: Stable alert code for automation and triage.
        severity: Alert severity (`critical`, `warning`, `info`).
        category: Alert category (`partial_ingestion`, `drift`, `coverage_gap`).
        title: Short alert title.
        message: Human-readable context of the issue.
        recommended_action: Objective recommendation for next action.
        source_id: Optional source identifier.
        ingestion_id: Optional ingestion run identifier.
        session_id: Optional session identifier.
        session_key: Optional session key.
        session_date: Optional session date in ISO format.
        session_type: Optional canonical session type.
        dataset: Optional dataset identifier.
    """

    code: str
    severity: str
    category: str
    title: str
    message: str
    recommended_action: str
    source_id: str | None = None
    ingestion_id: int | None = None
    session_id: int | None = None
    session_key: str | None = None
    session_date: str | None = None
    session_type: str | None = None
    dataset: str | None = None


def _severity_for_session_type(session_type: str | None) -> str:
    """Resolve alert severity for session-level gaps.

    Args:
        session_type: Canonical session type value.

    Returns:
        `critical` for show sessions, otherwise `warning`.
    """

    if str(session_type or "").upper() == "NOTURNO_SHOW":
        return "critical"
    return "warning"


def _collect_health_items(health_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """Extract health items from a payload.

    Args:
        health_payload: Health payload containing `items`.

    Returns:
        List of source-health dictionaries.
    """

    if not isinstance(health_payload, Mapping):
        return []
    items = health_payload.get("items", [])
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


def _collect_coverage_sessions(coverage_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """Extract coverage sessions from a payload.

    Args:
        coverage_payload: Coverage payload containing `sessions`.

    Returns:
        List of session coverage dictionaries.
    """

    if not isinstance(coverage_payload, Mapping):
        return []
    sessions = coverage_payload.get("sessions", [])
    if isinstance(sessions, list):
        return [item for item in sessions if isinstance(item, dict)]
    return []


def _collect_coverage_matrix(coverage_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """Extract coverage matrix rows from a payload.

    Args:
        coverage_payload: Coverage payload containing `matrix`.

    Returns:
        List of coverage matrix dictionaries.
    """

    if not isinstance(coverage_payload, Mapping):
        return []
    matrix = coverage_payload.get("matrix", [])
    if isinstance(matrix, list):
        return [item for item in matrix if isinstance(item, dict)]
    return []


def _collect_unresolved_counts(coverage_payload: Mapping[str, Any] | None) -> dict[str, int]:
    """Extract unresolved staging counts by dataset.

    Args:
        coverage_payload: Coverage payload containing `unresolved_without_session`.

    Returns:
        Dataset-to-count mapping.
    """

    if not isinstance(coverage_payload, Mapping):
        return {}
    raw = coverage_payload.get("unresolved_without_session", {})
    if not isinstance(raw, Mapping):
        return {}
    out: dict[str, int] = {}
    for dataset, value in raw.items():
        try:
            count = int(value)
        except (TypeError, ValueError):
            continue
        if count > 0:
            out[str(dataset)] = count
    return out


def generate_alerts(
    health_payload: Mapping[str, Any] | None,
    coverage_payload: Mapping[str, Any] | None,
) -> list[Alert]:
    """Generate actionable alerts from health and coverage payloads.

    Rules implemented:
    - partial ingestion by source;
    - drift symptoms (`unknown`/`ingestion_failed`, unresolved session mapping);
    - missing required datasets per session.

    Args:
        health_payload: Source-health payload (typically `/internal/health/sources`).
        coverage_payload: Coverage payload (typically `/internal/health/coverage`).

    Returns:
        Sorted list of alerts with severity and recommended actions.
    """

    alerts: list[Alert] = []
    seen: set[tuple[str, str, str | None, str | None]] = set()

    for item in _collect_health_items(health_payload):
        latest_status = str(item.get("latest_status") or "").lower()
        health_status = str(item.get("health_status") or "").lower()
        if latest_status != "partial" and health_status != "partial":
            continue
        source_id = str(item.get("source_id") or "")
        ingestion_id_raw = item.get("latest_ingestion_id")
        ingestion_id = int(ingestion_id_raw) if ingestion_id_raw is not None else None
        dedup_key = ("partial_ingestion", source_id, None, None)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        alerts.append(
            Alert(
                code="ALERT_PARTIAL_INGESTION",
                severity="warning",
                category="partial_ingestion",
                title=f"Ingestao parcial em {source_id}",
                message=(
                    f"Fonte {source_id} terminou com status parcial na ultima execucao."
                ),
                recommended_action=(
                    "Revisar notas/logs da ingestao, corrigir falhas de extracao e rerodar a carga."
                ),
                source_id=source_id or None,
                ingestion_id=ingestion_id,
            )
        )

    for dataset, unresolved_count in _collect_unresolved_counts(coverage_payload).items():
        dedup_key = ("drift_unresolved", dataset, None, None)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        alerts.append(
            Alert(
                code="ALERT_DRIFT_UNRESOLVED_SESSION",
                severity="warning",
                category="drift",
                title=f"Drift de mapeamento em {dataset}",
                message=(
                    f"{unresolved_count} registro(s) sem session_id para dataset {dataset}."
                ),
                recommended_action=(
                    "Revisar regras de session_resolver e mapeamento de layout para recuperar session_id."
                ),
                dataset=dataset,
            )
        )

    matrix_rows = _collect_coverage_matrix(coverage_payload)
    for row in matrix_rows:
        matrix_status = str(row.get("status") or "").lower()
        coverage_status = str(row.get("coverage_status") or "").lower()
        if matrix_status != "gap":
            continue
        if coverage_status not in {"unknown", "ingestion_failed"}:
            continue
        session_key = str(row.get("session_key") or "")
        dataset = str(row.get("dataset") or "")
        session_type = str(row.get("session_type") or "")
        severity = _severity_for_session_type(session_type)
        dedup_key = ("drift_metric_missing", session_key, dataset, None)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        alerts.append(
            Alert(
                code="ALERT_DRIFT_METRIC_MISSING",
                severity=severity,
                category="drift",
                title=f"Metrica ausente em {session_key}",
                message=(
                    f"Dataset {dataset} com coverage_status={coverage_status} na sessao {session_key}."
                ),
                recommended_action=(
                    "Validar spec do extractor e labels esperados para identificar drift de layout."
                ),
                session_id=int(row["session_id"]) if row.get("session_id") is not None else None,
                session_key=session_key or None,
                session_date=str(row.get("session_date") or "") or None,
                session_type=session_type or None,
                dataset=dataset or None,
            )
        )

    for session_row in _collect_coverage_sessions(coverage_payload):
        missing_raw = session_row.get("missing_datasets") or []
        if not isinstance(missing_raw, Sequence):
            continue
        missing_datasets = [str(item) for item in missing_raw if str(item)]
        if not missing_datasets:
            continue
        session_type = str(session_row.get("session_type") or "")
        severity = _severity_for_session_type(session_type)
        session_key = str(session_row.get("session_key") or "")
        session_date = str(session_row.get("session_date") or "")
        missing_text = ", ".join(sorted(set(missing_datasets)))
        dedup_key = ("coverage_gap", session_key, missing_text, None)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        show_hint = ""
        if session_type.upper() == "NOTURNO_SHOW":
            show_hint = " Sessao de show por dia exige cobertura completa antes do fechamento."

        alerts.append(
            Alert(
                code="ALERT_MISSING_REQUIRED_DATASET",
                severity=severity,
                category="coverage_gap",
                title=f"Datasets obrigatorios ausentes em {session_key}",
                message=(
                    f"Sessao {session_key} ({session_date}) sem datasets obrigatorios: {missing_text}.{show_hint}"
                ),
                recommended_action=(
                    "Solicitar fontes faltantes e rerodar extract/load antes da geracao do relatorio final."
                ),
                session_id=int(session_row["session_id"]) if session_row.get("session_id") is not None else None,
                session_key=session_key or None,
                session_date=session_date or None,
                session_type=session_type or None,
            )
        )

    return sorted(
        alerts,
        key=lambda item: (
            _SEVERITY_ORDER.get(item.severity, 99),
            item.category,
            item.session_date or "",
            item.session_key or "",
            item.source_id or "",
            item.dataset or "",
            item.code,
        ),
    )


def alerts_to_dicts(alerts: Iterable[Alert]) -> list[dict[str, Any]]:
    """Serialize alerts to JSON-friendly dictionaries.

    Args:
        alerts: Iterable of alert objects.

    Returns:
        List of dictionaries preserving alert fields.
    """

    payload: list[dict[str, Any]] = []
    for alert in alerts:
        payload.append(
            {
                "code": alert.code,
                "severity": alert.severity,
                "category": alert.category,
                "title": alert.title,
                "message": alert.message,
                "recommended_action": alert.recommended_action,
                "source_id": alert.source_id,
                "ingestion_id": alert.ingestion_id,
                "session_id": alert.session_id,
                "session_key": alert.session_key,
                "session_date": alert.session_date,
                "session_type": alert.session_type,
                "dataset": alert.dataset,
            }
        )
    return payload


def render_alerts_markdown(alerts: Iterable[Alert]) -> str:
    """Render alerts as a markdown section.

    Args:
        alerts: Iterable of alert objects.

    Returns:
        Markdown with one bullet per alert and objective recommendation.
    """

    alerts_list = list(alerts)
    lines: list[str] = []
    lines.append("## Alerts")
    if not alerts_list:
        lines.append("- nenhum")
        lines.append("")
        return "\n".join(lines)

    for alert in alerts_list:
        lines.append(
            "- "
            + f"[{alert.severity}] {alert.code} - {alert.title}: {alert.message}"
        )
        lines.append(f"  Acao recomendada: {alert.recommended_action}")
    lines.append("")
    return "\n".join(lines)
