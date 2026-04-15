from fastapi.testclient import TestClient

from app.main import app


def test_health_ready_returns_database_status():
    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["database"]["status"] == "ok"
    assert isinstance(payload["database"]["elapsed_ms"], int)
