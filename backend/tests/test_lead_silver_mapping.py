"""Tests for F2 Silver mapping endpoints (GET /colunas, POST /mapear)."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import BatchStage, LeadBatch, LeadColumnAlias, LeadSilver
from app.models.models import Evento, StatusEvento, Usuario
from app.utils.security import hash_password


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    eng = _make_engine()
    SQLModel.metadata.create_all(eng)
    return eng


@pytest.fixture
def client(engine):
    def override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_user(session: Session) -> Usuario:
    user = Usuario(
        email="silver@npbb.com.br",
        password_hash=hash_password("senha123"),
        tipo_usuario="npbb",
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_status(session: Session) -> StatusEvento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    if not status:
        status = StatusEvento(nome="Previsto")
        session.add(status)
        session.commit()
        session.refresh(status)
    return status


def _seed_evento(session: Session) -> Evento:
    status = _seed_status(session)
    evento = Evento(
        nome="Evento Teste Silver",
        cidade="São Paulo",
        estado="SP",
        status_id=status.id,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _auth_header(client: TestClient, session: Session) -> dict[str, str]:
    _seed_user(session)
    resp = client.post("/auth/login", json={"email": "silver@npbb.com.br", "password": "senha123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


CSV_CANONICAL = b"nome,cpf,email,telefone\nAlice,12345678901,alice@ex.com,11999990000\n"
CSV_SYNONYMS = b"full_name,documento,phone\nBob,98765432100,11888880000\n"


def _upload_batch(client: TestClient, auth: dict, csv_content: bytes, plataforma: str = "email") -> int:
    resp = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", io.BytesIO(csv_content), "text/csv")},
        data={"plataforma_origem": plataforma, "data_envio": "2026-03-01T10:00:00"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# GET /leads/batches/{id}/colunas
# ---------------------------------------------------------------------------


class TestGetColunas:
    def test_exact_match_canonical_fields(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, CSV_CANONICAL)
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["batch_id"] == batch_id
        colunas = {c["coluna_original"]: c for c in body["colunas"]}
        assert colunas["nome"]["campo_sugerido"] == "nome"
        assert colunas["nome"]["confianca"] == "exact_match"
        assert colunas["cpf"]["campo_sugerido"] == "cpf"
        assert colunas["email"]["campo_sugerido"] == "email"
        assert colunas["telefone"]["campo_sugerido"] == "telefone"

    def test_synonym_match(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, CSV_SYNONYMS)
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        colunas = {c["coluna_original"]: c for c in body["colunas"]}
        assert colunas["full_name"]["campo_sugerido"] == "nome"
        assert colunas["full_name"]["confianca"] == "synonym_match"
        assert colunas["documento"]["campo_sugerido"] == "cpf"
        assert colunas["documento"]["confianca"] == "synonym_match"
        assert colunas["phone"]["campo_sugerido"] == "telefone"
        assert colunas["phone"]["confianca"] == "synonym_match"

    def test_alias_match_from_saved_aliases(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            user = s.exec(select(Usuario)).first()

        # Salva um alias manualmente no banco
        with Session(engine) as s:
            alias = LeadColumnAlias(
                nome_coluna_original="nome_cliente",
                campo_canonico="nome",
                plataforma_origem="whatsapp",
                criado_por=user.id,
            )
            s.add(alias)
            s.commit()

        csv_with_alias = b"nome_cliente,cpf\nCarlos,11122233344\n"
        batch_id = _upload_batch(client, auth, csv_with_alias, plataforma="whatsapp")
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        colunas = {c["coluna_original"]: c for c in resp.json()["colunas"]}
        assert colunas["nome_cliente"]["campo_sugerido"] == "nome"
        assert colunas["nome_cliente"]["confianca"] == "alias_match"

    def test_no_suggestion_for_unknown_column(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        csv_unknown = b"coluna_desconhecida\nvalor\n"
        batch_id = _upload_batch(client, auth, csv_unknown)
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        col = body["colunas"][0]
        assert col["campo_sugerido"] is None
        assert col["confianca"] == "none"

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.get("/leads/batches/9999/colunas", headers=auth)
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.get("/leads/batches/1/colunas")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /leads/batches/{id}/mapear
# ---------------------------------------------------------------------------


class TestPostMapear:
    def test_full_mapping_creates_silver_rows(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, CSV_CANONICAL)
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {
                    "nome": "nome",
                    "cpf": "cpf",
                    "email": "email",
                    "telefone": "telefone",
                },
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["batch_id"] == batch_id
        assert body["silver_count"] == 1
        assert body["stage"] == "silver"

        # Verifica que o batch foi atualizado para silver
        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.stage == BatchStage.SILVER
            assert batch.evento_id == evento.id

        # Verifica que o LeadSilver foi criado
        with Session(engine) as s:
            silver_rows = s.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).all()
            assert len(silver_rows) == 1
            assert silver_rows[0].dados_brutos["nome"] == "Alice"
            assert silver_rows[0].dados_brutos["email"] == "alice@ex.com"

    def test_partial_mapping_ignores_unmapped_columns(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, CSV_CANONICAL)
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {"email": "email"},
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["silver_count"] == 1

        with Session(engine) as s:
            silver_rows = s.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).all()
            assert len(silver_rows) == 1
            # Apenas email deve estar nos dados_brutos
            assert list(silver_rows[0].dados_brutos.keys()) == ["email"]

    def test_aliases_saved_after_mapping(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        csv_data = b"nome_do_cliente,cpf_lead\nDiana,55566677788\n"
        batch_id = _upload_batch(client, auth, csv_data, plataforma="drive")
        client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {"nome_do_cliente": "nome", "cpf_lead": "cpf"},
            },
        )

        with Session(engine) as s:
            aliases = s.exec(
                select(LeadColumnAlias).where(LeadColumnAlias.plataforma_origem == "drive")
            ).all()
            by_col = {a.nome_coluna_original: a.campo_canonico for a in aliases}
            assert by_col["nome_do_cliente"] == "nome"
            assert by_col["cpf_lead"] == "cpf"

    def test_remapping_is_idempotent(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, CSV_CANONICAL)
        payload = {
            "evento_id": evento.id,
            "mapeamento": {"nome": "nome", "email": "email"},
        }
        client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json=payload,
        )
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json=payload,
        )
        assert resp.status_code == 200
        # Não deve duplicar silver rows
        with Session(engine) as s:
            count = len(s.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).all())
            assert count == 1

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.post(
            "/leads/batches/9999/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={"evento_id": 1, "mapeamento": {"nome": "nome"}},
        )
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.post(
            "/leads/batches/1/mapear",
            json={"evento_id": 1, "mapeamento": {"nome": "nome"}},
        )
        assert resp.status_code == 401

    def test_rejects_empty_mapeamento(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, CSV_CANONICAL)
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={"evento_id": 1, "mapeamento": {}},
        )
        assert resp.status_code == 400
