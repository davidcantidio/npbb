"""Testes de integração HTTP do router ``/sponsorship``.

Monta uma aplicação FastAPI mínima com autenticação e patrocínios, banco SQLite
em memória com ``foreign_keys`` habilitado e sessão injetada via override de
``get_session``. Cobre fluxos felizes, contagens agregadas e regras de
integridade (responsáveis, rejeição de ocorrência, metadados de arquivo).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.database import get_session
from app.models.models import Usuario
from app.routers.auth import router as auth_router
from app.routers.sponsorship import router as sponsorship_router
from app.utils.security import hash_password


def create_test_app() -> FastAPI:
    """Instancia FastAPI com rotas de autenticação e patrocínios.

    Returns:
        Aplicação pronta para ``TestClient`` e overrides de dependência.
    """
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(sponsorship_router)
    return app


def make_engine():
    """Cria engine SQLite em memória com pool estático e FKs forçadas.

    Returns:
        ``Engine`` SQLAlchemy configurado para testes isolados.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(
        engine,
        "connect",
        lambda dbapi_connection, _connection_record: dbapi_connection.execute(
            "PRAGMA foreign_keys=ON"
        ),
    )
    return engine


@pytest.fixture
def engine(monkeypatch):
    """Engine SQLite com schema SQLModel criado e ``SECRET_KEY`` de teste.

    Args:
        monkeypatch: Fixture pytest para variáveis de ambiente.

    Returns:
        Engine com tabelas materializadas.
    """
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    eng = make_engine()
    SQLModel.metadata.create_all(eng)
    return eng


@pytest.fixture
def app(engine):
    """Aplicação FastAPI com ``get_session`` sobrescrito para o engine de teste.

    Args:
        engine: Engine SQLite da fixture homônima.

    Yields:
        ``FastAPI`` com override de sessão ativo.
    """
    application = create_test_app()

    def override_get_session():
        with Session(engine) as session:
            yield session

    application.dependency_overrides[get_session] = override_get_session
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Cliente HTTP síncrono contra a app de teste.

    Args:
        app: Aplicação FastAPI da fixture homônima.

    Yields:
        ``TestClient`` context manager.
    """
    with TestClient(app) as test_client:
        yield test_client


def seed_npbb_user(session: Session, email: str, password: str) -> Usuario:
    """Persiste usuário NPBB ativo com senha hasheada.

    Args:
        session: Sessão SQLModel gravável.
        email: E-mail único de login.
        password: Senha em texto (será hasheada).

    Returns:
        Entidade ``Usuario`` com ``id`` após commit.
    """
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.expunge(user)
    return user


def login_and_get_token(client: TestClient, email: str, password: str) -> str:
    """Autentica via ``/auth/login`` e retorna JWT de acesso.

    Args:
        client: Cliente de teste.
        email: Credencial.
        password: Credencial.

    Returns:
        Token Bearer (string).

    Raises:
        AssertionError: Se o status HTTP não for 200.
    """
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(client: TestClient, engine, email: str) -> dict[str, str]:
    """Cria usuário único e retorna cabeçalho ``Authorization: Bearer``.

    Args:
        client: Cliente de teste.
        engine: Engine para abrir sessão e semear usuário.
        email: Base do e-mail (único por teste).

    Returns:
        Dicionário com chave ``Authorization``.
    """
    with Session(engine) as session:
        user = seed_npbb_user(session, email, "Senha123!")
    token = login_and_get_token(client, user.email, "Senha123!")
    return {"Authorization": f"Bearer {token}"}


def _assert_same_timestamp(actual: str, expected: str) -> None:
    """Compara duas ISO8601 ignorando apenas diferenças triviais de fuso.

    Args:
        actual: Valor retornado pela API.
        expected: Valor esperado no teste.

    Raises:
        AssertionError: Se os instantes normalizados divergirem.
    """
    actual_dt = datetime.fromisoformat(actual.replace("Z", "+00:00"))
    expected_dt = datetime.fromisoformat(expected.replace("Z", "+00:00"))
    if actual_dt.tzinfo is not None:
        actual_dt = actual_dt.astimezone(timezone.utc).replace(tzinfo=None)
    if expected_dt.tzinfo is not None:
        expected_dt = expected_dt.astimezone(timezone.utc).replace(tzinfo=None)
    assert actual_dt == expected_dt


def test_sponsorship_requires_auth(client):
    """Garante que a API de patrocínios exige autenticação.

    Args:
        client: Cliente HTTP sem token ``Authorization``.

    Returns:
        Nada; o teste passa se ``GET /sponsorship/groups`` retornar 401.
    """
    response = client.get("/sponsorship/groups")
    assert response.status_code == 401


def test_person_owner_first_flow_with_counts(client, engine):
    """Exercita fluxo feliz pessoa patrocinada com métricas agregadas.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; valida criação de pessoa, perfil social, grupo, contrato e
        contagens ``groups_count``, ``contracts_count`` e ``social_profiles_count``
        nas leituras subsequentes.
    """
    headers = auth_headers(client, engine, "person-owner@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta Teste",
            "role": "atleta",
            "cpf": None,
            "email": "atleta@example.com",
            "phone": None,
            "notes": "capitao",
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person = person_response.json()
    person_id = person["id"]
    assert person["groups_count"] == 0
    assert person["contracts_count"] == 0
    assert person["social_profiles_count"] == 0

    profile_response = client.post(
        "/sponsorship/social_profiles",
        json={
            "owner_type": "person",
            "owner_id": person_id,
            "platform": "instagram",
            "handle": "@atleta.teste",
            "url": None,
            "is_primary": True,
        },
        headers=headers,
    )
    assert profile_response.status_code == 201

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={
            "name": "Squad Atleta Teste",
            "description": "grupo principal",
            "role_in_group": "titular",
        },
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]
    assert group_response.json()["members_count"] == 1

    contract_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-PERSON-001",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
        },
        headers=headers,
    )
    assert contract_response.status_code == 201

    person_detail = client.get(f"/sponsorship/persons/{person_id}", headers=headers)
    assert person_detail.status_code == 200
    assert person_detail.json()["groups_count"] == 1
    assert person_detail.json()["contracts_count"] == 1
    assert person_detail.json()["social_profiles_count"] == 1

    groups_response = client.get(f"/sponsorship/persons/{person_id}/groups", headers=headers)
    assert groups_response.status_code == 200
    assert len(groups_response.json()) == 1
    assert groups_response.json()[0]["id"] == group_id

    persons_response = client.get("/sponsorship/persons", headers=headers)
    assert persons_response.status_code == 200
    assert persons_response.json()[0]["groups_count"] == 1


def test_institution_owner_first_flow_with_counts(client, engine):
    """Exercita fluxo feliz instituição patrocinada com métricas agregadas.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; valida criação de instituição, perfil social, grupo e contagens
        na leitura do cadastro e na listagem de grupos vinculados.
    """
    headers = auth_headers(client, engine, "institution-owner@example.com")

    institution_response = client.post(
        "/sponsorship/institutions",
        json={
            "name": "Instituto Exemplo",
            "cnpj": "12.345.678/0001-99",
            "email": "contato@instituto.example",
            "phone": None,
            "notes": "parceiro tecnico",
        },
        headers=headers,
    )
    assert institution_response.status_code == 201
    institution = institution_response.json()
    institution_id = institution["id"]

    profile_response = client.post(
        "/sponsorship/social_profiles",
        json={
            "owner_type": "institution",
            "owner_id": institution_id,
            "platform": "instagram",
            "handle": "@instituto.exemplo",
            "url": None,
            "is_primary": True,
        },
        headers=headers,
    )
    assert profile_response.status_code == 201

    group_response = client.post(
        f"/sponsorship/institutions/{institution_id}/groups",
        json={
            "name": "Grupo Instituto Exemplo",
            "description": "grupo institucional",
            "role_in_group": "parceiro",
        },
        headers=headers,
    )
    assert group_response.status_code == 201
    assert group_response.json()["members_count"] == 1

    institution_detail = client.get(f"/sponsorship/institutions/{institution_id}", headers=headers)
    assert institution_detail.status_code == 200
    assert institution_detail.json()["groups_count"] == 1
    assert institution_detail.json()["contracts_count"] == 0
    assert institution_detail.json()["social_profiles_count"] == 1

    groups_response = client.get(
        f"/sponsorship/institutions/{institution_id}/groups", headers=headers
    )
    assert groups_response.status_code == 200
    assert len(groups_response.json()) == 1


def test_social_profile_rejects_missing_person_owner(client, engine):
    """Rejeita perfil social quando o dono pessoa não existe.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera ``POST /sponsorship/social_profiles`` com ``owner_id``
        inexistente retornando 404 e detalhe ``Pessoa nao encontrada``.
    """
    headers = auth_headers(client, engine, "missing-person-owner@example.com")

    response = client.post(
        "/sponsorship/social_profiles",
        json={
            "owner_type": "person",
            "owner_id": 999999,
            "platform": "instagram",
            "handle": "@ghost.person",
            "url": None,
            "is_primary": False,
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Pessoa nao encontrada"


def test_social_profile_rejects_missing_institution_owner(client, engine):
    """Rejeita perfil social quando o dono instituição não existe.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera 404 com detalhe ``Instituicao nao encontrada``.
    """
    headers = auth_headers(client, engine, "missing-institution-owner@example.com")

    response = client.post(
        "/sponsorship/social_profiles",
        json={
            "owner_type": "institution",
            "owner_id": 999999,
            "platform": "instagram",
            "handle": "@ghost.institution",
            "url": None,
            "is_primary": False,
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Instituicao nao encontrada"


def test_social_profile_list_rejects_invalid_owner_type(client, engine):
    """Rejeita filtro de listagem com ``owner_type`` fora do domínio.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera 400 e mensagem contendo ``owner_type invalido``.
    """
    headers = auth_headers(client, engine, "invalid-owner-type-list@example.com")

    response = client.get(
        "/sponsorship/social_profiles",
        params={"owner_type": "foo"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "owner_type invalido" in response.json()["detail"]


def test_social_profile_list_rejects_missing_filtered_owner(client, engine):
    """Rejeita listagem quando o par dono/tipo aponta para registro inexistente.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera 404 ao combinar ``owner_type=person`` com ``owner_id`` inexistente.
    """
    headers = auth_headers(client, engine, "missing-filtered-owner@example.com")

    response = client.get(
        "/sponsorship/social_profiles",
        params={"owner_type": "person", "owner_id": 999999},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Pessoa nao encontrada"


def test_group_operational_flow_to_delivery_evidence(client, engine):
    """Percorre a cadeia operacional até evidência de entrega e contagens.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; valida membro, contrato, cláusula, requisito, ocorrência,
        responsável, entrega, evidência e contagens em listagens e detalhe do grupo.
    """
    headers = auth_headers(client, engine, "operational-flow@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta Operacional",
            "role": "atleta",
            "cpf": None,
            "email": "operacional@example.com",
            "phone": None,
            "notes": None,
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={
            "name": "Grupo Operacional",
            "description": "fluxo completo",
            "role_in_group": "titular",
        },
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    members_response = client.get(f"/sponsorship/groups/{group_id}/members", headers=headers)
    assert members_response.status_code == 200
    member_id = members_response.json()[0]["id"]

    contract_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-OPS-001",
            "group_id": group_id,
            "start_date": str(date(2026, 2, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
        },
        headers=headers,
    )
    assert contract_response.status_code == 201
    contract_id = contract_response.json()["id"]

    clause_response = client.post(
        f"/sponsorship/contracts/{contract_id}/clauses",
        json={
            "contract_id": contract_id,
            "clause_identifier": "2.1",
            "title": "Postagem obrigatoria",
            "clause_text": "Publicar um post com a marca.",
            "display_order": 1,
            "page_reference": "5",
        },
        headers=headers,
    )
    assert clause_response.status_code == 201
    clause_id = clause_response.json()["id"]

    requirement_response = client.post(
        f"/sponsorship/contracts/{contract_id}/requirements",
        json={
            "contract_id": contract_id,
            "clause_id": clause_id,
            "requirement_type": "post_social",
            "description": "Postar 1 vez por mes",
            "is_recurring": True,
            "period_type": "month",
            "period_rule_description": "1 publicacao por mes",
            "expected_occurrences": 10,
            "recurrence_start_date": str(date(2026, 2, 1)),
            "recurrence_end_date": str(date(2026, 11, 30)),
            "responsibility_type": "individual",
            "status": "planned",
        },
        headers=headers,
    )
    assert requirement_response.status_code == 201
    requirement_id = requirement_response.json()["id"]

    occurrence_response = client.post(
        f"/sponsorship/requirements/{requirement_id}/occurrences",
        json={
            "requirement_id": requirement_id,
            "period_label": "2026-03",
            "due_date": str(date(2026, 3, 31)),
            "status": "pending",
            "internal_notes": "primeira entrega",
        },
        headers=headers,
    )
    assert occurrence_response.status_code == 201
    occurrence_id = occurrence_response.json()["id"]

    responsible_response = client.post(
        f"/sponsorship/occurrences/{occurrence_id}/responsibles",
        json={
            "occurrence_id": occurrence_id,
            "member_id": member_id,
            "is_primary": True,
            "role_description": "responsavel principal",
        },
        headers=headers,
    )
    assert responsible_response.status_code == 201

    delivery_response = client.post(
        f"/sponsorship/occurrences/{occurrence_id}/deliveries",
        json={
            "occurrence_id": occurrence_id,
            "description": "Post publicado no feed",
            "observations": "conforme briefing",
        },
        headers=headers,
    )
    assert delivery_response.status_code == 201
    delivery_id = delivery_response.json()["id"]

    evidence_response = client.post(
        f"/sponsorship/deliveries/{delivery_id}/evidences",
        json={
            "delivery_id": delivery_id,
            "evidence_type": "social_post",
            "url": "https://instagram.example/post/1",
            "description": "link publico",
            "platform": "instagram",
            "external_id": "abc123",
            "posted_at": "2026-03-20T10:00:00Z",
        },
        headers=headers,
    )
    assert evidence_response.status_code == 201

    clauses_response = client.get(f"/sponsorship/contracts/{contract_id}/clauses", headers=headers)
    requirements_response = client.get(
        f"/sponsorship/contracts/{contract_id}/requirements", headers=headers
    )
    occurrences_response = client.get(
        f"/sponsorship/requirements/{requirement_id}/occurrences", headers=headers
    )
    deliveries_response = client.get(
        f"/sponsorship/occurrences/{occurrence_id}/deliveries", headers=headers
    )
    evidences_response = client.get(
        f"/sponsorship/deliveries/{delivery_id}/evidences", headers=headers
    )
    group_detail = client.get(f"/sponsorship/groups/{group_id}", headers=headers)

    assert clauses_response.status_code == 200
    assert len(clauses_response.json()) == 1
    assert requirements_response.status_code == 200
    assert requirements_response.json()[0]["occurrences_count"] == 1
    assert occurrences_response.status_code == 200
    assert len(occurrences_response.json()) == 1
    assert deliveries_response.status_code == 200
    assert len(deliveries_response.json()) == 1
    assert evidences_response.status_code == 200
    assert len(evidences_response.json()) == 1
    assert group_detail.status_code == 200
    assert group_detail.json()["members_count"] == 1
    assert group_detail.json()["contracts_count"] == 1


def test_create_responsible_rejects_missing_member_with_real_foreign_key(client, engine):
    """Impede responsável com ``member_id`` inválido ou fora do grupo do contrato.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera 400 ao postar ``member_id`` inexistente e lista de
        responsáveis vazia após a tentativa.
    """
    headers = auth_headers(client, engine, "responsible-fk@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta FK Real",
            "role": "atleta",
            "email": "fk-real@example.com",
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={"name": "Grupo FK Real"},
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    contract_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-FK-001",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
        },
        headers=headers,
    )
    assert contract_response.status_code == 201
    contract_id = contract_response.json()["id"]

    clause_response = client.post(
        f"/sponsorship/contracts/{contract_id}/clauses",
        json={
            "contract_id": contract_id,
            "clause_identifier": "1.1",
            "title": "Clausula base",
            "clause_text": "Texto base.",
            "display_order": 1,
        },
        headers=headers,
    )
    assert clause_response.status_code == 201
    clause_id = clause_response.json()["id"]

    requirement_response = client.post(
        f"/sponsorship/contracts/{contract_id}/requirements",
        json={
            "contract_id": contract_id,
            "clause_id": clause_id,
            "requirement_type": "post_social",
            "description": "Provar FK real em occurrence_responsible",
            "is_recurring": False,
            "expected_occurrences": 1,
            "responsibility_type": "individual",
            "status": "planned",
        },
        headers=headers,
    )
    assert requirement_response.status_code == 201
    requirement_id = requirement_response.json()["id"]

    occurrence_response = client.post(
        f"/sponsorship/requirements/{requirement_id}/occurrences",
        json={
            "requirement_id": requirement_id,
            "period_label": "2026-05",
            "status": "pending",
        },
        headers=headers,
    )
    assert occurrence_response.status_code == 201
    occurrence_id = occurrence_response.json()["id"]

    resp = client.post(
        f"/sponsorship/occurrences/{occurrence_id}/responsibles",
        json={
            "occurrence_id": occurrence_id,
            "member_id": 999999,
            "is_primary": True,
        },
        headers=headers,
    )
    assert resp.status_code == 400
    assert "nao pertence ao grupo" in resp.json()["detail"]

    list_response = client.get(f"/sponsorship/occurrences/{occurrence_id}/responsibles", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_create_requirement_rejects_clause_from_another_contract(client, engine):
    """Garante que requisito referencia apenas cláusula do mesmo contrato.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera 404 ``Clausula nao encontrada`` e lista de requisitos do
        contrato A permanece vazia.
    """
    headers = auth_headers(client, engine, "requirement-clause-mismatch@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta Clausula Errada",
            "role": "atleta",
            "cpf": None,
            "email": "clausula-errada@example.com",
            "phone": None,
            "notes": None,
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={
            "name": "Grupo Clausula Errada",
            "description": "grupo para validar contrato x clausula",
            "role_in_group": "titular",
        },
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    contract_a_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-MISMATCH-A",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 6, 30)),
            "status": "active",
        },
        headers=headers,
    )
    assert contract_a_response.status_code == 201
    contract_a_id = contract_a_response.json()["id"]

    contract_b_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-MISMATCH-B",
            "group_id": group_id,
            "start_date": str(date(2026, 7, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
        },
        headers=headers,
    )
    assert contract_b_response.status_code == 201
    contract_b_id = contract_b_response.json()["id"]

    clause_b_response = client.post(
        f"/sponsorship/contracts/{contract_b_id}/clauses",
        json={
            "contract_id": contract_b_id,
            "clause_identifier": "9.1",
            "title": "Clausula do contrato B",
            "clause_text": "Aplica somente ao contrato B.",
            "display_order": 1,
            "page_reference": "9",
        },
        headers=headers,
    )
    assert clause_b_response.status_code == 201
    clause_b_id = clause_b_response.json()["id"]

    requirement_response = client.post(
        f"/sponsorship/contracts/{contract_a_id}/requirements",
        json={
            "contract_id": contract_a_id,
            "clause_id": clause_b_id,
            "requirement_type": "post_social",
            "description": "Nao deve criar com clausula de outro contrato",
            "is_recurring": False,
            "period_type": None,
            "period_rule_description": None,
            "expected_occurrences": 1,
            "recurrence_start_date": None,
            "recurrence_end_date": None,
            "responsibility_type": "individual",
            "status": "planned",
        },
        headers=headers,
    )
    assert requirement_response.status_code == 404
    assert requirement_response.json()["detail"] == "Clausula nao encontrada"

    requirements_a_response = client.get(
        f"/sponsorship/contracts/{contract_a_id}/requirements",
        headers=headers,
    )
    assert requirements_a_response.status_code == 200
    assert requirements_a_response.json() == []


def test_occurrence_rejected_requires_rejection_reason(client, engine):
    """Valida regras de rejeição de ocorrência e normalização de motivo.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; cobre erro 400 sem motivo, motivo em branco, patch neutro e
        sucesso com ``rejection_reason`` aparado.
    """
    headers = auth_headers(client, engine, "occurrence-rejection@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta Rejeicao",
            "role": "atleta",
            "cpf": None,
            "email": "rejeicao@example.com",
            "phone": None,
            "notes": None,
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={
            "name": "Grupo Rejeicao",
            "description": "grupo para testes de rejeicao",
            "role_in_group": "titular",
        },
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    contract_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-REJ-001",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
        },
        headers=headers,
    )
    assert contract_response.status_code == 201
    contract_id = contract_response.json()["id"]

    clause_response = client.post(
        f"/sponsorship/contracts/{contract_id}/clauses",
        json={
            "contract_id": contract_id,
            "clause_identifier": "3.1",
            "title": "Entrega mensal",
            "clause_text": "Executar entrega mensal.",
            "display_order": 1,
            "page_reference": "3",
        },
        headers=headers,
    )
    assert clause_response.status_code == 201
    clause_id = clause_response.json()["id"]

    requirement_response = client.post(
        f"/sponsorship/contracts/{contract_id}/requirements",
        json={
            "contract_id": contract_id,
            "clause_id": clause_id,
            "requirement_type": "post_social",
            "description": "Post mensal",
            "is_recurring": True,
            "period_type": "month",
            "period_rule_description": "1 post por mes",
            "expected_occurrences": 12,
            "recurrence_start_date": str(date(2026, 1, 1)),
            "recurrence_end_date": str(date(2026, 12, 31)),
            "responsibility_type": "individual",
            "status": "planned",
        },
        headers=headers,
    )
    assert requirement_response.status_code == 201
    requirement_id = requirement_response.json()["id"]

    occurrence_response = client.post(
        f"/sponsorship/requirements/{requirement_id}/occurrences",
        json={
            "requirement_id": requirement_id,
            "period_label": "2026-04",
            "due_date": str(date(2026, 4, 30)),
            "responsibility_type": "collective",
            "status": "pending",
        },
        headers=headers,
    )
    assert occurrence_response.status_code == 201
    occurrence_id = occurrence_response.json()["id"]
    assert occurrence_response.json()["responsibility_type"] == "collective"

    rejected_without_reason = client.patch(
        f"/sponsorship/requirements/{requirement_id}/occurrences/{occurrence_id}",
        json={"status": "rejected"},
        headers=headers,
    )
    assert rejected_without_reason.status_code == 400
    assert rejected_without_reason.json()["detail"] == {
        "code": "INTEGRITY",
        "message": "rejection_reason e obrigatorio quando status=rejected",
    }

    rejected_with_blank_reason = client.patch(
        f"/sponsorship/requirements/{requirement_id}/occurrences/{occurrence_id}",
        json={"status": "rejected", "rejection_reason": "   "},
        headers=headers,
    )
    assert rejected_with_blank_reason.status_code == 400

    occurrence_list_response = client.get(
        f"/sponsorship/requirements/{requirement_id}/occurrences", headers=headers
    )
    assert occurrence_list_response.status_code == 200
    occurrence = occurrence_list_response.json()[0]
    assert occurrence["status"] == "pending"
    assert occurrence["responsibility_type"] == "collective"
    assert occurrence["rejection_reason"] is None

    non_rejected_patch = client.patch(
        f"/sponsorship/requirements/{requirement_id}/occurrences/{occurrence_id}",
        json={"internal_notes": "sem rejeicao", "responsibility_type": "individual"},
        headers=headers,
    )
    assert non_rejected_patch.status_code == 200
    assert non_rejected_patch.json()["status"] == "pending"
    assert non_rejected_patch.json()["responsibility_type"] == "individual"
    assert non_rejected_patch.json()["internal_notes"] == "sem rejeicao"

    rejected_with_reason = client.patch(
        f"/sponsorship/requirements/{requirement_id}/occurrences/{occurrence_id}",
        json={"status": "rejected", "rejection_reason": "  comprovante invalido  "},
        headers=headers,
    )
    assert rejected_with_reason.status_code == 200
    assert rejected_with_reason.json()["status"] == "rejected"
    assert rejected_with_reason.json()["rejection_reason"] == "comprovante invalido"


def test_contract_create_persists_original_file_metadata(client, engine):
    """Persiste metadados de arquivo na criação do contrato e na leitura GET.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; compara chave de armazenamento, nome original, checksum e
        ``uploaded_at`` entre POST 201 e GET do contrato.
    """
    headers = auth_headers(client, engine, "contract-file-create@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta Contrato Arquivo",
            "role": "atleta",
            "email": "arquivo@example.com",
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={"name": "Grupo Contrato Arquivo"},
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    uploaded_at = "2026-02-03T10:15:00Z"
    create_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-FILE-001",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
            "file_storage_key": "contracts/2026/CTR-FILE-001.pdf",
            "original_filename": "CTR-FILE-001-original.pdf",
            "file_checksum": "sha256:abc123",
            "uploaded_at": uploaded_at,
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    created_contract = create_response.json()
    contract_id = created_contract["id"]
    assert created_contract["file_storage_key"] == "contracts/2026/CTR-FILE-001.pdf"
    assert created_contract["original_filename"] == "CTR-FILE-001-original.pdf"
    assert created_contract["file_checksum"] == "sha256:abc123"
    _assert_same_timestamp(created_contract["uploaded_at"], uploaded_at)

    get_response = client.get(
        f"/sponsorship/groups/{group_id}/contracts/{contract_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["file_storage_key"] == "contracts/2026/CTR-FILE-001.pdf"
    assert get_response.json()["original_filename"] == "CTR-FILE-001-original.pdf"
    assert get_response.json()["file_checksum"] == "sha256:abc123"
    _assert_same_timestamp(get_response.json()["uploaded_at"], uploaded_at)


def test_contract_patch_updates_original_file_metadata(client, engine):
    """Atualiza metadados de arquivo do contrato via PATCH.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; valida resposta 200 com novos campos de arquivo e timestamp
        coerente com o payload.
    """
    headers = auth_headers(client, engine, "contract-file-patch@example.com")

    person_response = client.post(
        "/sponsorship/persons",
        json={
            "full_name": "Atleta Contrato Patch",
            "role": "atleta",
            "email": "patch@example.com",
        },
        headers=headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    group_response = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={"name": "Grupo Contrato Patch"},
        headers=headers,
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    create_response = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-FILE-002",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
            "status": "active",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    contract_id = create_response.json()["id"]

    uploaded_at = "2026-04-11T12:00:00Z"
    patch_response = client.patch(
        f"/sponsorship/groups/{group_id}/contracts/{contract_id}",
        json={
            "original_filename": "CTR-FILE-002-signed.pdf",
            "file_storage_key": "contracts/2026/CTR-FILE-002-signed.pdf",
            "file_checksum": "sha256:def456",
            "uploaded_at": uploaded_at,
        },
        headers=headers,
    )
    assert patch_response.status_code == 200
    patched_contract = patch_response.json()
    assert patched_contract["original_filename"] == "CTR-FILE-002-signed.pdf"
    assert patched_contract["file_storage_key"] == "contracts/2026/CTR-FILE-002-signed.pdf"
    assert patched_contract["file_checksum"] == "sha256:def456"
    _assert_same_timestamp(patched_contract["uploaded_at"], uploaded_at)


def test_create_responsible_rejects_member_from_different_group(client, engine):
    """Impede responsável cujo membro pertence a grupo distinto do contrato.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; espera HTTP 400 com mensagem indicando que o membro não pertence
        ao grupo do contrato da ocorrência.
    """
    headers = auth_headers(client, engine, "responsible-diff-group@example.com")

    person_a = client.post(
        "/sponsorship/persons",
        json={"full_name": "Atleta Grupo A", "role": "atleta"},
        headers=headers,
    )
    assert person_a.status_code == 201

    person_b = client.post(
        "/sponsorship/persons",
        json={"full_name": "Atleta Grupo B", "role": "atleta"},
        headers=headers,
    )
    assert person_b.status_code == 201

    group_a = client.post(
        f"/sponsorship/persons/{person_a.json()['id']}/groups",
        json={"name": "Grupo A"},
        headers=headers,
    )
    assert group_a.status_code == 201
    group_a_id = group_a.json()["id"]

    group_b = client.post(
        f"/sponsorship/persons/{person_b.json()['id']}/groups",
        json={"name": "Grupo B"},
        headers=headers,
    )
    assert group_b.status_code == 201
    group_b_id = group_b.json()["id"]

    members_b = client.get(f"/sponsorship/groups/{group_b_id}/members", headers=headers)
    member_b_id = members_b.json()[0]["id"]

    contract_a = client.post(
        f"/sponsorship/groups/{group_a_id}/contracts",
        json={
            "contract_number": "CTR-DIFF-GRP",
            "group_id": group_a_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
        },
        headers=headers,
    )
    assert contract_a.status_code == 201
    contract_a_id = contract_a.json()["id"]

    clause = client.post(
        f"/sponsorship/contracts/{contract_a_id}/clauses",
        json={"contract_id": contract_a_id, "clause_identifier": "1", "display_order": 1},
        headers=headers,
    )
    assert clause.status_code == 201

    req = client.post(
        f"/sponsorship/contracts/{contract_a_id}/requirements",
        json={
            "contract_id": contract_a_id,
            "clause_id": clause.json()["id"],
            "requirement_type": "post",
            "description": "test",
            "responsibility_type": "individual",
        },
        headers=headers,
    )
    assert req.status_code == 201

    occ = client.post(
        f"/sponsorship/requirements/{req.json()['id']}/occurrences",
        json={"requirement_id": req.json()["id"], "period_label": "2026-06"},
        headers=headers,
    )
    assert occ.status_code == 201

    resp = client.post(
        f"/sponsorship/occurrences/{occ.json()['id']}/responsibles",
        json={
            "occurrence_id": occ.json()["id"],
            "member_id": member_b_id,
            "is_primary": True,
        },
        headers=headers,
    )
    assert resp.status_code == 400
    assert "nao pertence ao grupo" in resp.json()["detail"]


def test_occurrence_validated_fills_validated_by_and_at(client, engine):
    """Preenche e limpa ``validated_by_user_id`` e ``validated_at`` conforme status.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; valida que ``validated`` preenche rastreio e retorno a ``pending``
        zera os campos de validação.
    """
    headers = auth_headers(client, engine, "validated-by@example.com")

    person = client.post(
        "/sponsorship/persons",
        json={"full_name": "Atleta Validacao", "role": "atleta"},
        headers=headers,
    )
    assert person.status_code == 201

    group = client.post(
        f"/sponsorship/persons/{person.json()['id']}/groups",
        json={"name": "Grupo Validacao"},
        headers=headers,
    )
    assert group.status_code == 201
    group_id = group.json()["id"]

    members = client.get(f"/sponsorship/groups/{group_id}/members", headers=headers)
    member_id = members.json()[0]["id"]

    contract = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": "CTR-VAL-001",
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
        },
        headers=headers,
    )
    assert contract.status_code == 201
    contract_id = contract.json()["id"]

    clause = client.post(
        f"/sponsorship/contracts/{contract_id}/clauses",
        json={"contract_id": contract_id, "clause_identifier": "1", "display_order": 1},
        headers=headers,
    )
    assert clause.status_code == 201

    req = client.post(
        f"/sponsorship/contracts/{contract_id}/requirements",
        json={
            "contract_id": contract_id,
            "clause_id": clause.json()["id"],
            "requirement_type": "presenca",
            "description": "validar rastreabilidade",
        },
        headers=headers,
    )
    assert req.status_code == 201

    occ = client.post(
        f"/sponsorship/requirements/{req.json()['id']}/occurrences",
        json={"requirement_id": req.json()["id"], "period_label": "2026-07"},
        headers=headers,
    )
    assert occ.status_code == 201
    occ_id = occ.json()["id"]
    req_id = req.json()["id"]

    assert occ.json()["validated_by_user_id"] is None
    assert occ.json()["validated_at"] is None

    client.post(
        f"/sponsorship/occurrences/{occ_id}/responsibles",
        json={"occurrence_id": occ_id, "member_id": member_id, "is_primary": True},
        headers=headers,
    )

    validated = client.patch(
        f"/sponsorship/requirements/{req_id}/occurrences/{occ_id}",
        json={"status": "validated"},
        headers=headers,
    )
    assert validated.status_code == 200
    assert validated.json()["status"] == "validated"
    assert validated.json()["validated_by_user_id"] is not None
    assert validated.json()["validated_at"] is not None

    reverted = client.patch(
        f"/sponsorship/requirements/{req_id}/occurrences/{occ_id}",
        json={"status": "pending"},
        headers=headers,
    )
    assert reverted.status_code == 200
    assert reverted.json()["status"] == "pending"
    assert reverted.json()["validated_by_user_id"] is None
    assert reverted.json()["validated_at"] is None


def _setup_occurrence_with_member(client, engine, email_suffix, contract_number):
    """Monta grafo mínimo até ocorrência individual com um membro no grupo.

    Args:
        client: Cliente de teste.
        engine: Engine SQLite.
        email_suffix: Sufixo para e-mail único do usuário semeado.
        contract_number: Número único do contrato criado.

    Returns:
        Dicionário com ``headers``, ``group_id``, ``member_id``, ``req_id`` e
        ``occ_id``.
    """
    headers = auth_headers(client, engine, f"cardinality-{email_suffix}@example.com")

    person = client.post(
        "/sponsorship/persons",
        json={"full_name": f"Atleta Card {email_suffix}", "role": "atleta"},
        headers=headers,
    )
    assert person.status_code == 201
    person_id = person.json()["id"]

    group = client.post(
        f"/sponsorship/persons/{person_id}/groups",
        json={"name": f"Grupo Card {email_suffix}"},
        headers=headers,
    )
    assert group.status_code == 201
    group_id = group.json()["id"]

    members = client.get(f"/sponsorship/groups/{group_id}/members", headers=headers)
    member_id = members.json()[0]["id"]

    contract = client.post(
        f"/sponsorship/groups/{group_id}/contracts",
        json={
            "contract_number": contract_number,
            "group_id": group_id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2026, 12, 31)),
        },
        headers=headers,
    )
    assert contract.status_code == 201
    contract_id = contract.json()["id"]

    clause = client.post(
        f"/sponsorship/contracts/{contract_id}/clauses",
        json={"contract_id": contract_id, "clause_identifier": "1", "display_order": 1},
        headers=headers,
    )
    assert clause.status_code == 201

    req = client.post(
        f"/sponsorship/contracts/{contract_id}/requirements",
        json={
            "contract_id": contract_id,
            "clause_id": clause.json()["id"],
            "requirement_type": "post",
            "description": "cardinalidade test",
            "responsibility_type": "individual",
        },
        headers=headers,
    )
    assert req.status_code == 201

    occ = client.post(
        f"/sponsorship/requirements/{req.json()['id']}/occurrences",
        json={
            "requirement_id": req.json()["id"],
            "period_label": "2026-08",
            "responsibility_type": "individual",
        },
        headers=headers,
    )
    assert occ.status_code == 201

    return {
        "headers": headers,
        "group_id": group_id,
        "member_id": member_id,
        "req_id": req.json()["id"],
        "occ_id": occ.json()["id"],
    }


def _create_member_for_group(client, headers, group_id, full_name):
    """Cria nova pessoa e adiciona como membro ao grupo informado.

    Args:
        client: Cliente de teste.
        headers: Cabeçalhos autenticados.
        group_id: Grupo de destino.
        full_name: Nome da pessoa a criar.

    Returns:
        ``id`` do ``GroupMember`` criado.
    """
    person = client.post(
        "/sponsorship/persons",
        json={"full_name": full_name, "role": "atleta"},
        headers=headers,
    )
    assert person.status_code == 201
    person_id = person.json()["id"]
    member = client.post(
        f"/sponsorship/groups/{group_id}/members",
        json={"group_id": group_id, "person_id": person_id, "role_in_group": "apoio"},
        headers=headers,
    )
    assert member.status_code == 201
    return member.json()["id"]


def test_individual_occurrence_rejects_transition_without_exactly_one_responsible(client, engine):
    """Bloqueia transição operacional individual sem exatamente um responsável.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; primeiro PATCH ``in_review`` falha; após criar responsável,
        o mesmo PATCH retorna 200.
    """
    ctx = _setup_occurrence_with_member(client, engine, "indiv-0", "CTR-CARD-IND0")

    resp = client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"status": "in_review"},
        headers=ctx["headers"],
    )
    assert resp.status_code == 400
    assert "exatamente 1 responsavel" in resp.json()["detail"]["message"]

    client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": ctx["member_id"], "is_primary": True},
        headers=ctx["headers"],
    )

    resp = client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"status": "in_review"},
        headers=ctx["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_review"


def test_collective_occurrence_rejects_transition_with_fewer_than_two(client, engine):
    """Exige pelo menos dois responsáveis para ``delivered`` em modo coletivo.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; com apenas um responsável, PATCH para ``delivered`` retorna 400.
    """
    ctx = _setup_occurrence_with_member(client, engine, "coll-1", "CTR-CARD-COL1")

    client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"responsibility_type": "collective"},
        headers=ctx["headers"],
    )

    client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": ctx["member_id"], "is_primary": True},
        headers=ctx["headers"],
    )

    resp = client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"status": "delivered"},
        headers=ctx["headers"],
    )
    assert resp.status_code == 400
    assert "2 ou mais responsaveis" in resp.json()["detail"]["message"]


def test_individual_occurrence_rejects_second_responsible_on_create(client, engine):
    """Impede segundo responsável quando a ocorrência é ``individual``.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; segundo ``POST .../responsibles`` retorna 400 com código
        ``INTEGRITY``.
    """
    ctx = _setup_occurrence_with_member(client, engine, "indiv-2", "CTR-CARD-IND2")
    second_member_id = _create_member_for_group(
        client,
        ctx["headers"],
        ctx["group_id"],
        "Atleta Card indiv-2 segundo",
    )

    first = client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": ctx["member_id"], "is_primary": True},
        headers=ctx["headers"],
    )
    assert first.status_code == 201

    second = client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": second_member_id, "is_primary": False},
        headers=ctx["headers"],
    )
    assert second.status_code == 400
    assert second.json()["detail"]["code"] == "INTEGRITY"
    assert "nao e permitido adicionar um segundo responsavel" in second.json()["detail"]["message"]


def test_occurrence_rejects_switch_to_collective_until_two_responsibles_exist(client, engine):
    """Falha ao combinar ``collective`` com ``delivered`` se houver só um responsável.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; PATCH conjunto retorna 400 com regra de cardinalidade coletiva.
    """
    ctx = _setup_occurrence_with_member(client, engine, "switch-coll", "CTR-CARD-SWCOL")

    first = client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": ctx["member_id"], "is_primary": True},
        headers=ctx["headers"],
    )
    assert first.status_code == 201

    switch_type = client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"responsibility_type": "collective", "status": "delivered"},
        headers=ctx["headers"],
    )
    assert switch_type.status_code == 400
    assert switch_type.json()["detail"]["code"] == "INTEGRITY"
    assert "2 ou mais responsaveis" in switch_type.json()["detail"]["message"]


def test_occurrence_rejects_switch_to_individual_with_two_responsibles(client, engine):
    """Impede ``individual`` com status operacional quando há dois responsáveis.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; após dois responsáveis em modo coletivo, PATCH para individual +
        ``validated`` retorna 400.
    """
    ctx = _setup_occurrence_with_member(client, engine, "switch-indiv", "CTR-CARD-SWIND")
    second_member_id = _create_member_for_group(
        client,
        ctx["headers"],
        ctx["group_id"],
        "Atleta Card switch-indiv segundo",
    )

    client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"responsibility_type": "collective"},
        headers=ctx["headers"],
    )
    first = client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": ctx["member_id"], "is_primary": True},
        headers=ctx["headers"],
    )
    second = client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": second_member_id, "is_primary": False},
        headers=ctx["headers"],
    )
    assert first.status_code == 201
    assert second.status_code == 201

    switch_type = client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"responsibility_type": "individual", "status": "validated"},
        headers=ctx["headers"],
    )
    assert switch_type.status_code == 400
    assert switch_type.json()["detail"]["code"] == "INTEGRITY"
    assert "exatamente 1 responsavel" in switch_type.json()["detail"]["message"]


def test_delete_responsible_rejects_breaking_operational_cardinality(client, engine):
    """Impede remover o único responsável quando a ocorrência está ``in_review``.

    Args:
        client: Aplicação FastAPI com sessão sobrescrita.
        engine: SQLite em memória com schema completo.

    Returns:
        Nada; ``DELETE`` do responsável retorna 400 com código ``INTEGRITY``.
    """
    ctx = _setup_occurrence_with_member(client, engine, "delete-card", "CTR-CARD-DEL")

    created = client.post(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles",
        json={"occurrence_id": ctx["occ_id"], "member_id": ctx["member_id"], "is_primary": True},
        headers=ctx["headers"],
    )
    assert created.status_code == 201
    responsible_id = created.json()["id"]

    promoted = client.patch(
        f"/sponsorship/requirements/{ctx['req_id']}/occurrences/{ctx['occ_id']}",
        json={"status": "in_review"},
        headers=ctx["headers"],
    )
    assert promoted.status_code == 200

    delete_response = client.delete(
        f"/sponsorship/occurrences/{ctx['occ_id']}/responsibles/{responsible_id}",
        headers=ctx["headers"],
    )
    assert delete_response.status_code == 400
    assert delete_response.json()["detail"]["code"] == "INTEGRITY"
    assert "exatamente 1 responsavel" in delete_response.json()["detail"]["message"]
