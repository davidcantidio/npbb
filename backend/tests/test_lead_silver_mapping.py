"""Tests for F2 Silver mapping endpoints (GET /colunas, POST /mapear)."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import BatchStage, LeadBatch, LeadColumnAlias, LeadSilver
from app.models.models import (
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    StatusEvento,
    TipoLead,
    TipoResponsavel,
    Usuario,
)
from app.services.imports.contracts import ImportPreviewResult
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


def _seed_user(
    session: Session,
    *,
    email: str = "silver@npbb.com.br",
    password: str = "senha123",
) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password(password),
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


def _auth_header(
    client: TestClient,
    session: Session,
    *,
    email: str = "silver@npbb.com.br",
    password: str = "senha123",
) -> dict[str, str]:
    _seed_user(session, email=email, password=password)
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


CSV_CANONICAL = b"nome,cpf,email,telefone\nAlice,12345678901,alice@ex.com,11999990000\n"
CSV_CANONICAL_MULTIROW = (
    b"nome,cpf,email,telefone\n"
    b"Alice,12345678901,alice@ex.com,11999990000\n"
    b"Bob,98765432100,bob@ex.com,11888880000\n"
)
CSV_SYNONYMS = b"full_name,documento,phone\nBob,98765432100,11888880000\n"
CSV_EXTENDED_SYNONYMS = b"last_name,sexo,rg\nSilva,Feminino,1234567\n"
CSV_WITH_PREAMBLE = (
    b"linha solta 1,,\n"
    b"linha solta 2,,\n"
    b"linha solta 3,,\n"
    b"linha solta 4,,\n"
    b"linha solta 5,,\n"
    b"linha solta 6,,\n"
    b"linha solta 7,,\n"
    b"linha solta 8,,\n"
    b"nome,cpf,email\n"
    b"Alice,12345678901,alice@ex.com\n"
    b"Bob,98765432100,bob@ex.com\n"
)


def _upload_batch(client: TestClient, auth: dict, csv_content: bytes, plataforma: str = "email") -> int:
    resp = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", io.BytesIO(csv_content), "text/csv")},
        data={"plataforma_origem": plataforma, "data_envio": "2026-03-01T10:00:00"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _set_batch_evento(engine, batch_id: int, evento_id: int | None) -> None:
    with Session(engine) as s:
        batch = s.get(LeadBatch, batch_id)
        assert batch is not None
        batch.evento_id = evento_id
        s.add(batch)
        s.commit()


def _make_xlsx_with_preamble() -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    for idx in range(8):
        ws.append([f"linha solta {idx + 1}", "", ""])
    ws.append(["nome", "cpf", "email"])
    ws.append(["Alice", "12345678901", "alice@ex.com"])
    ws.append(["Bob", "98765432100", "bob@ex.com"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def _upload_xlsx_batch(client: TestClient, auth: dict, workbook: io.BytesIO, plataforma: str = "manual") -> int:
    resp = client.post(
        "/leads/batches",
        headers=auth,
        files={
            "file": (
                "leads.xlsx",
                workbook,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        data={"plataforma_origem": plataforma, "data_envio": "2026-03-01T10:00:00"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# GET /leads/batches/{id}/colunas
# ---------------------------------------------------------------------------


class TestGetColunas:
    def test_uses_header_only_reader(self, monkeypatch, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, CSV_WITH_PREAMBLE)

        def fake_headers(raw: bytes, *, filename: str) -> ImportPreviewResult:
            assert filename == "leads.csv"
            return ImportPreviewResult(
                filename=filename,
                headers=["nome", "cpf", "email"],
                rows=[],
                delimiter=",",
                start_index=8,
                physical_line_numbers=[],
            )

        def fail_full_read(*args, **kwargs):
            raise AssertionError("suggest_column_mapping should not read the full file")

        monkeypatch.setattr("app.services.lead_mapping.read_raw_file_headers", fake_headers)
        monkeypatch.setattr("app.services.lead_mapping.read_raw_file_rows", fail_full_read)

        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        assert [col["coluna_original"] for col in resp.json()["colunas"]] == ["nome", "cpf", "email"]

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

    def test_synonym_match_for_extended_lead_fields(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, CSV_EXTENDED_SYNONYMS)
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        colunas = {c["coluna_original"]: c for c in resp.json()["colunas"]}
        assert colunas["last_name"]["campo_sugerido"] == "sobrenome"
        assert colunas["last_name"]["confianca"] == "synonym_match"
        assert colunas["sexo"]["campo_sugerido"] == "genero"
        assert colunas["sexo"]["confianca"] == "synonym_match"
        assert colunas["rg"]["campo_sugerido"] == "rg"
        assert colunas["rg"]["confianca"] == "exact_match"

    def test_cidade_is_suggested_as_exact_canonical_field(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, b"cidade\nSao Paulo\n")
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        colunas = {c["coluna_original"]: c for c in resp.json()["colunas"]}
        assert colunas["cidade"]["campo_sugerido"] == "cidade"
        assert colunas["cidade"]["confianca"] == "exact_match"

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

    def test_detects_real_header_after_preamble_rows(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth, CSV_WITH_PREAMBLE)
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        colunas = {c["coluna_original"]: c for c in body["colunas"]}
        assert set(colunas) == {"nome", "cpf", "email"}
        assert "linha solta 1" not in colunas

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.get("/leads/batches/9999/colunas", headers=auth)
        assert resp.status_code == 404

    def test_hides_batch_from_other_user(self, client, engine):
        with Session(engine) as s:
            owner_auth = _auth_header(client, s, email="silver-owner@npbb.com.br", password="senha123")
            other_auth = _auth_header(client, s, email="silver-other@npbb.com.br", password="senha456")

        batch_id = _upload_batch(client, owner_auth, CSV_CANONICAL)
        resp = client.get(f"/leads/batches/{batch_id}/colunas", headers=other_auth)
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
            assert silver_rows[0].dados_brutos["source_file"] == "leads.csv"
            assert silver_rows[0].dados_brutos["source_sheet"] == ""
            assert silver_rows[0].dados_brutos["source_row"] == 2
            assert silver_rows[0].dados_brutos["source_row_original"] == 2

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
            assert silver_rows[0].dados_brutos == {
                "email": "alice@ex.com",
                "source_file": "leads.csv",
                "source_sheet": "",
                "source_row": 2,
                "source_row_original": 2,
            }

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

    def test_hides_single_mapping_from_other_user(self, client, engine):
        with Session(engine) as s:
            owner_auth = _auth_header(client, s, email="single-owner@npbb.com.br", password="senha123")
            other_auth = _auth_header(client, s, email="single-other@npbb.com.br", password="senha456")
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, owner_auth, CSV_CANONICAL)
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**other_auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {"cpf": "cpf", "nome": "nome"},
            },
        )
        assert resp.status_code == 404

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

    def test_remapping_replaces_existing_silver_rows_without_duplicates_for_multiple_rows(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, CSV_CANONICAL_MULTIROW)
        payload = {
            "evento_id": evento.id,
            "mapeamento": {"nome": "nome", "email": "email"},
        }
        first_resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json=payload,
        )
        second_resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json=payload,
        )

        assert first_resp.status_code == 200, first_resp.text
        assert second_resp.status_code == 200, second_resp.text

        with Session(engine) as s:
            silver_rows = s.exec(
                select(LeadSilver)
                .where(LeadSilver.batch_id == batch_id)
                .order_by(LeadSilver.row_index)
            ).all()
            assert len(silver_rows) == 2
            assert [row.row_index for row in silver_rows] == [0, 1]
            assert silver_rows[0].dados_brutos["nome"] == "Alice"
            assert silver_rows[1].dados_brutos["nome"] == "Bob"

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

    def test_mapping_skips_preamble_rows_for_xlsx_batches(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_xlsx_batch(client, auth, _make_xlsx_with_preamble())
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {"nome": "nome", "cpf": "cpf", "email": "email"},
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["silver_count"] == 2

        with Session(engine) as s:
            silver_rows = s.exec(
                select(LeadSilver).where(LeadSilver.batch_id == batch_id).order_by(LeadSilver.row_index)
            ).all()
            assert len(silver_rows) == 2
            assert silver_rows[0].dados_brutos == {
                "nome": "Alice",
                "cpf": "12345678901",
                "email": "alice@ex.com",
                "source_file": "leads.xlsx",
                "source_sheet": "Sheet",
                "source_row": 10,
                "source_row_original": 10,
            }
            assert silver_rows[1].dados_brutos == {
                "nome": "Bob",
                "cpf": "98765432100",
                "email": "bob@ex.com",
                "source_file": "leads.xlsx",
                "source_sheet": "Sheet",
                "source_row": 11,
                "source_row_original": 11,
            }

    def test_mapping_csv_blank_line_between_rows_sets_physical_source_rows(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        csv_data = (
            b"nome,cpf,email\n"
            b"Alice,12345678901,alice@ex.com\n"
            b"\n"
            b"Bob,98765432100,bob@ex.com\n"
        )
        batch_id = _upload_batch(client, auth, csv_data)
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {"nome": "nome", "cpf": "cpf", "email": "email"},
            },
        )
        assert resp.status_code == 200, resp.text

        with Session(engine) as s:
            silver_rows = s.exec(
                select(LeadSilver).where(LeadSilver.batch_id == batch_id).order_by(LeadSilver.row_index)
            ).all()
            assert len(silver_rows) == 2
            assert silver_rows[0].dados_brutos["source_row"] == 2
            assert silver_rows[0].dados_brutos["source_row_original"] == 2
            assert silver_rows[1].dados_brutos["source_row"] == 4
            assert silver_rows[1].dados_brutos["source_row_original"] == 4

    def test_mapping_persists_extended_lead_fields(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        csv_data = b"nome,last_name,sexo,rg\nAlice,Silva,Feminino,1234567\n"
        batch_id = _upload_batch(client, auth, csv_data)
        resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {
                    "nome": "nome",
                    "last_name": "sobrenome",
                    "sexo": "genero",
                    "rg": "rg",
                },
            },
        )
        assert resp.status_code == 200, resp.text

        with Session(engine) as s:
            silver_row = s.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).first()
            assert silver_row is not None
            assert silver_row.dados_brutos["nome"] == "Alice"
            assert silver_row.dados_brutos["sobrenome"] == "Silva"
            assert silver_row.dados_brutos["genero"] == "Feminino"
            assert silver_row.dados_brutos["rg"] == "1234567"


class TestBatchMappingEndpoints:
    def test_batch_colunas_groups_repeated_headers_with_coverage(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_a = _upload_batch(client, auth, b"CPF,Email\n12345678901,alice@ex.com\n", plataforma="email")
        batch_b = _upload_batch(client, auth, b"cpf,Telefone\n98765432100,11999990000\n", plataforma="email")
        _set_batch_evento(engine, batch_a, evento.id)
        _set_batch_evento(engine, batch_b, evento.id)

        resp = client.post("/leads/batches/colunas", headers=auth, json={"batch_ids": [batch_a, batch_b]})
        assert resp.status_code == 200, resp.text

        body = resp.json()
        assert body["batch_ids"] == [batch_a, batch_b]
        assert body["primary_batch_id"] == batch_a
        assert body["warnings"] == []
        assert body["blockers"] == []
        assert body["blocked_batch_ids"] == []

        cpf_group = next(group for group in body["colunas"] if group["chave_agregada"] == "cpf")
        assert cpf_group["aparece_em_arquivos"] == 2
        assert cpf_group["campo_sugerido"] == "cpf"
        assert cpf_group["confianca"] == "exact_match"
        assert [item["batch_id"] for item in cpf_group["ocorrencias"]] == [batch_a, batch_b]

    def test_batch_colunas_hides_batches_from_other_user(self, client, engine):
        with Session(engine) as s:
            owner_auth = _auth_header(client, s, email="batch-owner@npbb.com.br", password="senha123")
            other_auth = _auth_header(client, s, email="batch-other@npbb.com.br", password="senha456")
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, owner_auth, b"cpf\n12345678901\n")
        _set_batch_evento(engine, batch_id, evento.id)

        resp = client.post("/leads/batches/colunas", headers=other_auth, json={"batch_ids": [batch_id]})
        assert resp.status_code == 404

    def test_batch_colunas_warns_when_group_suggestions_diverge(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento_a = _seed_evento(s)
            evento_b = Evento(
                nome="Evento Batch Divergente",
                cidade="Rio de Janeiro",
                estado="RJ",
                status_id=evento_a.status_id,
            )
            s.add(evento_b)
            s.commit()
            s.refresh(evento_b)
            evento_a_id = evento_a.id
            evento_b_id = evento_b.id
            user = s.exec(select(Usuario)).first()
            assert user is not None
            s.add(
                LeadColumnAlias(
                    nome_coluna_original="Data",
                    campo_canonico="data_nascimento",
                    plataforma_origem="email",
                    criado_por=user.id,
                )
            )
            s.add(
                LeadColumnAlias(
                    nome_coluna_original="Data",
                    campo_canonico="data_compra",
                    plataforma_origem="manual",
                    criado_por=user.id,
                )
            )
            s.commit()

        batch_a = _upload_batch(client, auth, b"Data\n01/02/1990\n", plataforma="email")
        batch_b = _upload_batch(client, auth, b"Data\n2026-03-01\n", plataforma="manual")
        _set_batch_evento(engine, batch_a, evento_a_id)
        _set_batch_evento(engine, batch_b, evento_b_id)

        resp = client.post("/leads/batches/colunas", headers=auth, json={"batch_ids": [batch_a, batch_b]})
        assert resp.status_code == 200, resp.text
        body = resp.json()

        data_group = next(group for group in body["colunas"] if group["chave_agregada"] == "data")
        assert data_group["campo_sugerido"] is None
        assert "Sugestoes automaticas divergentes entre os arquivos." in data_group["warnings"]
        assert "A coluna aparece em arquivos de plataformas diferentes." in data_group["warnings"]
        assert "A coluna aparece em arquivos de eventos diferentes." in data_group["warnings"]
        assert len(body["warnings"]) == 2

    def test_batch_colunas_reports_blockers_for_missing_event_and_collision(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_ok = _upload_batch(client, auth, b"nome,cpf\nAlice,12345678901\n")
        batch_collision = _upload_batch(client, auth, b"Data,data\n01/02/1990,2026-03-01\n")
        _set_batch_evento(engine, batch_ok, evento.id)
        _set_batch_evento(engine, batch_collision, evento.id)

        resp = client.post("/leads/batches/colunas", headers=auth, json={"batch_ids": [batch_ok, batch_collision]})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        blockers = body["blockers"]
        assert any("nao possui evento de referencia salvo" in blocker for blocker in blockers) is False
        assert any("colidem na regra de agregacao batch" in blocker for blocker in blockers)
        assert body["blocked_batch_ids"] == [batch_collision]

        _set_batch_evento(engine, batch_ok, None)
        resp_missing = client.post("/leads/batches/colunas", headers=auth, json={"batch_ids": [batch_ok]})
        assert resp_missing.status_code == 200, resp_missing.text
        assert resp_missing.json()["blocked_batch_ids"] == [batch_ok]
        assert any(
            "nao possui evento de referencia salvo" in blocker for blocker in resp_missing.json()["blockers"]
        )

    def test_batch_mapping_blocks_non_bronze_batches(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, b"cpf\n12345678901\n")
        single_resp = client.post(
            f"/leads/batches/{batch_id}/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "evento_id": evento.id,
                "mapeamento": {"cpf": "cpf"},
            },
        )
        assert single_resp.status_code == 200, single_resp.text

        preview_resp = client.post("/leads/batches/colunas", headers=auth, json={"batch_ids": [batch_id]})
        assert preview_resp.status_code == 200, preview_resp.text
        preview_body = preview_resp.json()
        assert preview_body["blocked_batch_ids"] == [batch_id]
        assert any("nao e elegivel para o mapeamento batch" in blocker for blocker in preview_body["blockers"])

        blocked_resp = client.post(
            "/leads/batches/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "batch_ids": [batch_id],
                "mapeamento": {"cpf": "cpf"},
            },
        )
        assert blocked_resp.status_code == 400, blocked_resp.text
        assert blocked_resp.json()["detail"]["code"] == "BATCH_MAPPING_BLOCKED"

        with Session(engine) as s:
            batch_db = s.get(LeadBatch, batch_id)
            assert batch_db is not None and batch_db.stage == BatchStage.SILVER
            silver_rows = s.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).all()
            assert len(silver_rows) == 1

    def test_mapear_batches_applies_mapping_in_single_transaction(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_a = _upload_batch(client, auth, b"CPF,Nome\n12345678901,Alice\n")
        batch_b = _upload_batch(client, auth, b"cpf,nome\n98765432100,Bob\n")
        _set_batch_evento(engine, batch_a, evento.id)
        _set_batch_evento(engine, batch_b, evento.id)

        resp = client.post(
            "/leads/batches/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "batch_ids": [batch_a, batch_b],
                "mapeamento": {"cpf": "cpf", "nome": "nome"},
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["primary_batch_id"] == batch_a
        assert body["total_silver_count"] == 2
        assert [item["batch_id"] for item in body["results"]] == [batch_a, batch_b]

        with Session(engine) as s:
            batch_a_db = s.get(LeadBatch, batch_a)
            batch_b_db = s.get(LeadBatch, batch_b)
            assert batch_a_db is not None and batch_a_db.stage == BatchStage.SILVER
            assert batch_b_db is not None and batch_b_db.stage == BatchStage.SILVER

            silver_rows = s.exec(select(LeadSilver).order_by(LeadSilver.batch_id, LeadSilver.row_index)).all()
            assert len(silver_rows) == 2
            assert silver_rows[0].dados_brutos["cpf"] == "12345678901"
            assert silver_rows[1].dados_brutos["cpf"] == "98765432100"

    def test_mapear_batches_rolls_back_when_request_is_blocked(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_ok = _upload_batch(client, auth, b"cpf\n12345678901\n")
        batch_missing_event = _upload_batch(client, auth, b"cpf\n98765432100\n")
        _set_batch_evento(engine, batch_ok, evento.id)

        resp = client.post(
            "/leads/batches/mapear",
            headers={**auth, "Content-Type": "application/json"},
            json={
                "batch_ids": [batch_ok, batch_missing_event],
                "mapeamento": {"cpf": "cpf"},
            },
        )
        assert resp.status_code == 400, resp.text
        detail = resp.json()["detail"]
        assert detail["code"] == "BATCH_MAPPING_BLOCKED"
        assert detail["blockers"]

        with Session(engine) as s:
            batch_ok_db = s.get(LeadBatch, batch_ok)
            batch_missing_db = s.get(LeadBatch, batch_missing_event)
            assert batch_ok_db is not None and batch_ok_db.stage == BatchStage.BRONZE
            assert batch_missing_db is not None and batch_missing_db.stage == BatchStage.BRONZE
            assert s.exec(select(LeadSilver)).all() == []

    def test_batch_mapear_hides_batches_from_other_user(self, client, engine):
        with Session(engine) as s:
            owner_auth = _auth_header(client, s, email="map-owner@npbb.com.br", password="senha123")
            other_auth = _auth_header(client, s, email="map-other@npbb.com.br", password="senha456")
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, owner_auth, b"cpf\n12345678901\n")
        _set_batch_evento(engine, batch_id, evento.id)

        resp = client.post(
            "/leads/batches/mapear",
            headers={**other_auth, "Content-Type": "application/json"},
            json={
                "batch_ids": [batch_id],
                "mapeamento": {"cpf": "cpf"},
            },
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Tests for LeadEvento resolution by evento_nome (ISSUE-F1-03-002)
# ---------------------------------------------------------------------------


class TestResolveUniqueEventoByName:
    """Tests for resolve_unique_evento_by_name function."""

    def test_resolve_returns_resolved_when_single_match(self, client, engine):
        """Given unique evento match by name, When resolved, Then returns resolved status with evento_id."""
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento_id = evento.id
            evento_nome = evento.nome

        # Import the function to test
        from app.services.lead_event_service import resolve_unique_evento_by_name

        with Session(engine) as s:
            result = resolve_unique_evento_by_name(s, evento_nome)

        assert result.status == "resolved"
        assert result.evento_id == evento_id

    def test_resolve_returns_missing_when_no_event_match(self, client, engine):
        """Given no evento matches the name, When resolved, Then returns missing status."""
        with Session(engine) as s:
            auth = _auth_header(client, s)
            _seed_evento(s)

        from app.services.lead_event_service import resolve_unique_evento_by_name

        with Session(engine) as s:
            result = resolve_unique_evento_by_name(s, "Evento Inexistente 12345")

        assert result.status == "missing"
        assert result.evento_id is None

    def test_resolve_returns_ambiguous_when_multiple_matches(self, client, engine):
        """Given multiple eventos with same normalized name, When resolved, Then returns ambiguous status."""
        with Session(engine) as s:
            auth = _auth_header(client, s)
            status = _seed_status(s)

            # Create two eventos with same normalized name
            evento1 = Evento(
                nome="Evento Duplicado",
                cidade="São Paulo",
                estado="SP",
                status_id=status.id,
            )
            evento2 = Evento(
                nome="EVENTO DUPLICADO",  # Same name, different case
                cidade="Rio de Janeiro",
                estado="RJ",
                status_id=status.id,
            )
            s.add(evento1)
            s.add(evento2)
            s.commit()
            s.refresh(evento1)
            s.refresh(evento2)

        from app.services.lead_event_service import resolve_unique_evento_by_name

        with Session(engine) as s:
            result = resolve_unique_evento_by_name(s, "Evento Duplicado")

        assert result.status == "ambiguous"
        assert result.evento_id is None

    def test_resolve_returns_missing_when_event_name_is_none(self, client, engine):
        """Given None as event name, When resolved, Then returns missing status."""
        from app.services.lead_event_service import resolve_unique_evento_by_name

        with Session(engine) as s:
            result = resolve_unique_evento_by_name(s, None)

        assert result.status == "missing"
        assert result.evento_id is None

    def test_resolve_returns_missing_when_event_name_is_empty(self, client, engine):
        """Given empty string as event name, When resolved, Then returns missing status."""
        from app.services.lead_event_service import resolve_unique_evento_by_name

        with Session(engine) as s:
            result = resolve_unique_evento_by_name(s, "")

        assert result.status == "missing"
        assert result.evento_id is None


class TestEnsureCanonicalEventLink:
    """Tests for _ensure_canonical_event_link function behavior."""

    def test_creates_lead_evento_when_unique_match(self, client, engine):
        """Given unique evento match, When link is ensured, Then LeadEvento is created."""
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento_nome = evento.nome
            evento_id = evento.id

            lead = Lead(
                nome="Test Lead",
                email="testlead@example.com",
                evento_nome=evento_nome,
            )
            s.add(lead)
            s.commit()
            s.refresh(lead)
            lead_id = lead.id

        from app.modules.lead_imports.application.etl_import import persistence

        with Session(engine) as s:
            lead = s.get(Lead, lead_id)
            payload = {"evento_nome": evento_nome}
            persistence._ensure_canonical_event_link(s, lead=lead, payload=payload)
            s.commit()

            from app.models.models import LeadEvento
            lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead_id)).all()

        assert len(lead_eventos) == 1
        assert lead_eventos[0].evento_id == evento_id
        assert lead_eventos[0].source_kind == LeadEventoSourceKind.EVENT_NAME_BACKFILL
        assert lead_eventos[0].tipo_lead == TipoLead.ENTRADA_EVENTO
        assert lead_eventos[0].responsavel_tipo == TipoResponsavel.PROPONENTE
        assert lead_eventos[0].responsavel_nome == evento_nome
        assert lead_eventos[0].responsavel_agencia_id is None

    def test_does_not_create_lead_evento_when_ambiguous_match(self, client, engine):
        """Given ambiguous evento match, When link is ensured, Then LeadEvento is NOT created."""
        with Session(engine) as s:
            auth = _auth_header(client, s)
            status = _seed_status(s)

            # Create two eventos with same normalized name
            evento1 = Evento(
                nome="Evento Duplicado Teste",
                cidade="São Paulo",
                estado="SP",
                status_id=status.id,
            )
            evento2 = Evento(
                nome="EVENTO DUPLICADO TESTE",
                cidade="Rio de Janeiro",
                estado="RJ",
                status_id=status.id,
            )
            s.add(evento1)
            s.add(evento2)
            s.commit()

            # Create a lead with ambiguous evento_nome
            lead = Lead(
                nome="Test Lead Ambiguous",
                email="testambiguous@example.com",
                evento_nome="Evento Duplicado Teste",
            )
            s.add(lead)
            s.commit()
            s.refresh(lead)

        from app.modules.lead_imports.application.etl_import import persistence

        with Session(engine) as s:
            lead = s.get(Lead, lead.id)
            payload = {"evento_nome": "Evento Duplicado Teste"}
            persistence._ensure_canonical_event_link(s, lead=lead, payload=payload)
            s.commit()

            # Verify LeadEvento was NOT created (ambiguous match)
            from app.models.models import LeadEvento
            lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()

        assert len(lead_eventos) == 0

    def test_does_not_create_lead_evento_when_no_match(self, client, engine):
        """Given no evento match, When link is ensured, Then LeadEvento is NOT created."""
        with Session(engine) as s:
            auth = _auth_header(client, s)
            _seed_evento(s)

            # Create a lead with non-existent evento_nome
            lead = Lead(
                nome="Test Lead No Match",
                email="testnomatch@example.com",
                evento_nome="Evento Inexistente 999",
            )
            s.add(lead)
            s.commit()
            s.refresh(lead)

        from app.modules.lead_imports.application.etl_import import persistence

        with Session(engine) as s:
            lead = s.get(Lead, lead.id)
            payload = {"evento_nome": "Evento Inexistente 999"}
            persistence._ensure_canonical_event_link(s, lead=lead, payload=payload)
            s.commit()

            # Verify LeadEvento was NOT created (no match)
            from app.models.models import LeadEvento
            lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()

        assert len(lead_eventos) == 0
