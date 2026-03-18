import importlib

from fastapi.testclient import TestClient


def load_app():
    module = importlib.import_module("app.main")
    return module.app


def test_app_main_registers_framework_routes():
    app = load_app()

    framework_routes = {route.path for route in app.routes if route.path.startswith("/framework")}

    assert "/framework/projects" in framework_routes
    assert "/framework/projects/" in framework_routes


def test_health_endpoint_smoke():
    app = load_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
