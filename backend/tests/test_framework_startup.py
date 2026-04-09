import importlib
import sys
import types

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db.database import get_session
from app.models.framework_models import FrameworkProject


def load_app():
    if "pandas" not in sys.modules:
        pandas_stub = types.ModuleType("pandas")
        pandas_stub.DataFrame = object
        sys.modules["pandas"] = pandas_stub
    sys.modules.pop("app.main", None)
    module = importlib.import_module("app.main")
    return module.app


def _complete_raw_context() -> str:
    return """
Problema ou oportunidade: O PM ainda depende de montagem manual de artefatos.
Publico principal: PM
Job to be done dominante: Abrir um projeto governado no FW5.
Fluxo principal:
- Receber contexto bruto
- Gerar intake estruturado
- Validar prontidao para PRD
Escopo dentro:
- Captura de contexto bruto
- Estruturacao do intake
Escopo fora:
- Geracao do PRD
Objetivo de negocio: Reduzir o trabalho manual de abertura do projeto.
Metricas de sucesso:
- tempo_manual_reduzido
Restricoes:
- Manter compatibilidade com a governanca vigente
Nao objetivos:
- Nao substituir toda a governanca markdown nesta task
Dependencias:
- GOV-INTAKE.md
Integracoes:
- framework-governanca
Superficies impactadas:
- backend-api
- admin-panel
Riscos:
- Consolidar hipoteses como fatos
""".strip()


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


def test_framework_intake_endpoint_returns_structured_payload(test_engine):
    app = load_app()

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    with Session(test_engine) as session:
        project = FrameworkProject(
            canonical_name="fw5-http",
            title="FW5 HTTP",
            created_by="pm",
            owner="pm",
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        project_id = project.id

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        response = client.post(
            f"/framework/projects/{project_id}/intake",
            json={
                "title": "FW5 Intake",
                "raw_context": _complete_raw_context(),
                "intake_kind": "new-capability",
                "source_mode": "original",
            },
        )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project_id
    assert payload["approval_status"] == "pending"
    assert payload["is_current"] is True
    assert payload["structured_payload"]["problem_statement"].startswith("O PM")
    assert payload["known_gaps"] == []
    assert payload["ready_for_prd"] is True
    assert payload["version_history"][0]["version_number"] == 1


def test_framework_prd_generate_endpoint_uses_current_intake_and_updates_status(test_engine):
    app = load_app()

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    with Session(test_engine) as session:
        project = FrameworkProject(
            canonical_name="fw5-http-prd",
            title="FW5 HTTP PRD",
            created_by="pm",
            owner="pm",
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        project_id = project.id

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        intake_response = client.post(
            f"/framework/projects/{project_id}/intake",
            json={
                "title": "FW5 Intake",
                "raw_context": _complete_raw_context(),
                "intake_kind": "new-capability",
                "source_mode": "original",
            },
        )
        prd_response = client.post(f"/framework/projects/{project_id}/prd/generate")
        status_response = client.get(f"/framework/projects/{project_id}/status")
    app.dependency_overrides.clear()

    assert intake_response.status_code == 200
    assert prd_response.status_code == 200
    assert prd_response.json()["prd_id"] > 0
    assert prd_response.json()["auto_approved"] is False
    assert status_response.status_code == 200
    assert status_response.json()["has_intake"] is True
    assert status_response.json()["has_prd"] is True
    assert status_response.json()["status"] == "prd"


def test_framework_prd_generate_endpoint_returns_404_without_current_intake(test_engine):
    app = load_app()

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    with Session(test_engine) as session:
        project = FrameworkProject(
            canonical_name="fw5-http-prd-missing-intake",
            title="FW5 HTTP PRD Missing Intake",
            created_by="pm",
            owner="pm",
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        project_id = project.id

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        prd_response = client.post(f"/framework/projects/{project_id}/prd/generate")
        status_response = client.get(f"/framework/projects/{project_id}/status")
    app.dependency_overrides.clear()

    assert prd_response.status_code == 404
    assert "Intake corrente nao encontrado" in prd_response.json()["detail"]
    assert status_response.status_code == 200
    assert status_response.json()["has_intake"] is False
    assert status_response.json()["has_prd"] is False
    assert status_response.json()["status"] == "draft"
