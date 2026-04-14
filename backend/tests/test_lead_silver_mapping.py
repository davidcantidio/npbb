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
            }
            assert silver_rows[1].dados_brutos == {
                "nome": "Bob",
                "cpf": "98765432100",
                "email": "bob@ex.com",
            }

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

        from app.modules.leads_publicidade.application.etl_import import persistence

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

        from app.modules.leads_publicidade.application.etl_import import persistence

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

        from app.modules.leads_publicidade.application.etl_import import persistence

        with Session(engine) as s:
            lead = s.get(Lead, lead.id)
            payload = {"evento_nome": "Evento Inexistente 999"}
            persistence._ensure_canonical_event_link(s, lead=lead, payload=payload)
            s.commit()

            # Verify LeadEvento was NOT created (no match)
            from app.models.models import LeadEvento
            lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()

        assert len(lead_eventos) == 0
