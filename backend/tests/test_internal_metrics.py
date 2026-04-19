"""Tests for Prometheus /internal/metrics access control."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_metrics_requires_auth_without_scrape_token(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NPBB_METRICS_SCRAPE_TOKEN", raising=False)
    res = client.get("/internal/metrics")
    assert res.status_code == 401


def test_metrics_accepts_scrape_token_query(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NPBB_METRICS_SCRAPE_TOKEN", "test-metrics-secret-please-change")
    res = client.get("/internal/metrics", params={"token": "test-metrics-secret-please-change"})
    assert res.status_code == 200
    assert b"npbb_lead_import_upload_rejected_total" in res.content
