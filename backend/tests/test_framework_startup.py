import importlib

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db.database import get_session
from app.models.framework_models import FrameworkProject


def load_app():
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
    assert payload["structured_payload"]["problem_statement"].startswith("O PM")
    assert payload["known_gaps"] == []
    assert payload["ready_for_prd"] is True
    assert payload["version_history"][0]["version_number"] == 1
