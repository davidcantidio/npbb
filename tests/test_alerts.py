"""Unit tests for observability alert generation rules."""

from __future__ import annotations

from etl.validate.alerts import alerts_to_dicts, generate_alerts


def test_generate_alerts_covers_partial_drift_and_missing_required_datasets() -> None:
    """Alert generator should emit all required categories with severities."""

    health_payload = {
        "items": [
            {
                "source_id": "SRC_OPTIN_NOTURNO_DOZE",
                "latest_ingestion_id": 101,
                "latest_status": "partial",
                "health_status": "partial",
            }
        ]
    }
    coverage_payload = {
        "sessions": [
            {
                "session_id": 12,
                "session_key": "TMJ2025_20251212_SHOW",
                "session_date": "2025-12-12",
                "session_type": "NOTURNO_SHOW",
                "status": "gap",
                "missing_datasets": ["ticket_sales", "optin"],
            }
        ],
        "matrix": [
            {
                "session_id": 12,
                "session_key": "TMJ2025_20251212_SHOW",
                "session_date": "2025-12-12",
                "session_type": "NOTURNO_SHOW",
                "dataset": "ticket_sales",
                "status": "gap",
                "coverage_status": "unknown",
            }
        ],
        "unresolved_without_session": {"optin": 3},
    }

    alerts = generate_alerts(health_payload, coverage_payload)
    payload = alerts_to_dicts(alerts)
    by_code = {item["code"]: item for item in payload}

    assert "ALERT_PARTIAL_INGESTION" in by_code
    assert "ALERT_DRIFT_UNRESOLVED_SESSION" in by_code
    assert "ALERT_DRIFT_METRIC_MISSING" in by_code
    assert "ALERT_MISSING_REQUIRED_DATASET" in by_code

    assert by_code["ALERT_PARTIAL_INGESTION"]["severity"] == "warning"
    assert by_code["ALERT_DRIFT_UNRESOLVED_SESSION"]["dataset"] == "optin"
    assert by_code["ALERT_MISSING_REQUIRED_DATASET"]["severity"] == "critical"
    assert "show por dia" in by_code["ALERT_MISSING_REQUIRED_DATASET"]["message"].lower()


def test_generate_alerts_returns_empty_when_no_signal_exists() -> None:
    """Alert generator should return empty list when no rule is triggered."""

    health_payload = {"items": [{"source_id": "SRC_OK", "latest_status": "success"}]}
    coverage_payload = {
        "sessions": [
            {
                "session_id": 1,
                "session_key": "TMJ2025_20251213_SHOW",
                "session_date": "2025-12-13",
                "session_type": "NOTURNO_SHOW",
                "status": "ok",
                "missing_datasets": [],
            }
        ],
        "matrix": [],
        "unresolved_without_session": {"optin": 0},
    }

    alerts = generate_alerts(health_payload, coverage_payload)
    assert alerts == []
