import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.models import EventPublicity, Evento, StatusEvento, Usuario
from app.utils.security import hash_password


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_user(engine, email="importador@example.com", password="senha123") -> Usuario:
    with Session(engine) as session:
        user = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario="bb",
            ativo=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def seed_event(engine, *, code: str, nome: str = "Evento Publicidade") -> Evento:
    with Session(engine) as session:
        status = StatusEvento(nome=f"Status {code}")
        session.add(status)
        session.flush()
        evento = Evento(
            nome=nome,
            cidade="Sao Paulo",
            estado="SP",
            concorrencia=False,
            status_id=int(status.id),
            external_project_code=code,
        )
        session.add(evento)
        session.commit()
        session.refresh(evento)
        return evento


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _default_mappings() -> list[dict]:
    return [
        {"coluna": "Codigo Projeto", "campo": "codigo_projeto", "confianca": 0.9},
        {"coluna": "Projeto", "campo": "projeto", "confianca": 0.9},
        {"coluna": "Data Vinculacao", "campo": "data_vinculacao", "confianca": 0.9},
        {"coluna": "Meio", "campo": "meio", "confianca": 0.9},
        {"coluna": "Veiculo", "campo": "veiculo", "confianca": 0.9},
        {"coluna": "UF", "campo": "uf", "confianca": 0.9},
        {"coluna": "UF Extenso", "campo": "uf_extenso", "confianca": 0.8},
        {"coluna": "Municipio", "campo": "municipio", "confianca": 0.8},
        {"coluna": "Camada", "campo": "camada", "confianca": 0.9},
    ]


def _csv_payload(codigo_projeto: str) -> bytes:
    return (
        "Relatorio Publicidade;;;;;;;\n"
        "Codigo Projeto;Projeto;Data Vinculacao;Meio;Veiculo;UF;UF Extenso;Municipio;Camada\n"
        f"{codigo_projeto};Projeto Primavera;2026-01-15;digital;Portal X;sp;Sao Paulo;Sao Paulo;nacional\n"
    ).encode("utf-8")


def test_publicidade_validate_mapping_returns_structured_error(client, engine):
    user = seed_user(engine)
    token = login_and_get_token(client, user.email, "senha123")

    response = client.post(
        "/publicidade/import/validate",
        headers=_headers(token),
        json=[{"coluna": "Codigo Projeto", "campo": "codigo_projeto", "confianca": 0.9}],
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"]["code"] == "MAPPING_MISSING_REQUIRED_FIELDS"
    assert "missing_required_fields" in payload["detail"]


def test_publicidade_import_is_idempotent_for_same_file(client, engine):
    user = seed_user(engine, email="idempotente@example.com")
    token = login_and_get_token(client, user.email, "senha123")
    seed_event(engine, code="PRJ-001")

    mappings = _default_mappings()
    data = {"mappings_json": json.dumps(mappings), "dry_run": "false"}
    file_bytes = _csv_payload("PRJ-001")

    first = client.post(
        "/publicidade/import",
        headers=_headers(token),
        data=data,
        files={"file": ("publicidade.csv", file_bytes, "text/csv")},
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["staged_inserted"] == 1
    assert first_payload["staged_skipped"] == 0
    assert first_payload["upsert_inserted"] == 1
    assert first_payload["upsert_updated"] == 0
    assert first_payload["unresolved_event_id"] == 0

    second = client.post(
        "/publicidade/import",
        headers=_headers(token),
        data=data,
        files={"file": ("publicidade.csv", file_bytes, "text/csv")},
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["staged_inserted"] == 0
    assert second_payload["staged_skipped"] == 1
    assert second_payload["upsert_inserted"] == 0
    assert second_payload["upsert_updated"] == 0


def test_publicidade_alias_resolves_event_by_external_project_code(client, engine):
    user = seed_user(engine, email="alias@example.com")
    token = login_and_get_token(client, user.email, "senha123")
    evento = seed_event(engine, code="PRJ-CANON", nome="Evento Alias")

    alias_response = client.post(
        "/publicidade/aliases",
        headers=_headers(token),
        json={
            "field_name": "codigo_projeto",
            "valor_origem": "Projeto Sem Codigo",
            "canonical_value": "PRJ-CANON",
            "canonical_ref_id": int(evento.id),
        },
    )
    assert alias_response.status_code == 201

    mappings = _default_mappings()
    import_response = client.post(
        "/publicidade/import",
        headers=_headers(token),
        data={"mappings_json": json.dumps(mappings), "dry_run": "false"},
        files={"file": ("publicidade_alias.csv", _csv_payload("Projeto Sem Codigo"), "text/csv")},
    )
    assert import_response.status_code == 200
    payload = import_response.json()
    assert payload["unresolved_event_id"] == 0

    with Session(engine) as session:
        saved = session.exec(select(EventPublicity).order_by(EventPublicity.id.desc())).first()
        assert saved is not None
        assert saved.event_id == evento.id
