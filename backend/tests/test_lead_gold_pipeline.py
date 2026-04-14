"""Tests for F3 Gold pipeline endpoints.

GET  /leads/batches/{id}
POST /leads/batches/{id}/executar-pipeline
"""

from __future__ import annotations

import asyncio
import io
import json
from datetime import date as date_type, datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.database import get_session
from app.main import app
from app.models.lead_batch import BatchStage, LeadBatch, LeadSilver, PipelineStatus
from app.models.models import (
    Agencia,
    Ativacao,
    AtivacaoLead,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    StatusEvento,
    TipoEvento,
    TipoLead,
    TipoResponsavel,
    Usuario,
)
from app.utils.security import hash_password
from lead_pipeline.constants import ALL_COLUMNS, FINAL_FILENAME
from lead_pipeline.contracts import validate_databricks_contract
from lead_pipeline.normalization import BirthDateIssue, normalize_data_nascimento
from lead_pipeline.pipeline import PipelineProgressEvent, PipelineResult, _normalize_row


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    tmp_root = Path("backend/tmp-pytest") / f"lead-pipeline-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        "app.services.lead_pipeline_service.TMP_ROOT",
        tmp_root,
    )
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
        email="gold@npbb.com.br",
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


def _seed_evento(session: Session, *, agencia_id: int | None = None) -> Evento:
    ev_status = _seed_status(session)
    evento = Evento(
        nome="Park Challenge 2025",
        cidade="SP",
        estado="SP",
        status_id=ev_status.id,
        agencia_id=agencia_id,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _seed_agencia(session: Session) -> Agencia:
    ag = Agencia(nome="Agencia Teste", dominio="ag-teste-import.npbb", lote=1)
    session.add(ag)
    session.commit()
    session.refresh(ag)
    return ag


def _auth_header(client: TestClient, session: Session) -> dict[str, str]:
    _seed_user(session)
    resp = client.post("/auth/login", json={"email": "gold@npbb.com.br", "password": "senha123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


CSV_CONTENT = b"nome,cpf,email,telefone\nAlice,52998224725,alice@ex.com,11999990000\n"


def _base_gold_row(
    *,
    cpf: str = "52998224725",
    data_nascimento: str = "1990-01-15",
    local: str = "Sao Paulo-SP",
    cidade: str = "",
    estado: str = "",
) -> dict[str, str]:
    return {
        "nome": "Alice",
        "cpf": cpf,
        "email": "alice@ex.com",
        "telefone": "11999990000",
        "evento": "Park Challenge 2025",
        "tipo_evento": "ESPORTE",
        "local": local,
        "data_evento": "2026-06-08",
        "data_nascimento": data_nascimento,
        "cidade": cidade,
        "estado": estado,
    }


def _contract_frame(*, data_nascimento: str) -> pd.DataFrame:
    row = {column: "" for column in ALL_COLUMNS}
    row.update(_base_gold_row(data_nascimento=data_nascimento))
    return pd.DataFrame([row], columns=ALL_COLUMNS)


def _upload_batch(
    client: TestClient,
    auth: dict,
    plataforma: str = "email",
    *,
    evento_id: int | None = None,
    origem_lote: str | None = None,
    ativacao_id: int | None = None,
    tipo_lead_proponente: str | None = None,
) -> int:
    data: dict[str, str] = {
        "plataforma_origem": plataforma,
        "data_envio": "2026-03-05T10:00:00",
    }
    if evento_id is not None:
        data["evento_id"] = str(evento_id)
    if origem_lote is not None:
        data["origem_lote"] = origem_lote
    if ativacao_id is not None:
        data["ativacao_id"] = str(ativacao_id)
    if tipo_lead_proponente is not None:
        data["tipo_lead_proponente"] = tipo_lead_proponente

    resp = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", io.BytesIO(CSV_CONTENT), "text/csv")},
        data=data,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _promote_to_silver(
    engine,
    batch_id: int,
    evento_id: int,
    *,
    dados_brutos_extra: dict[str, str] | None = None,
) -> None:
    """Directly set batch to silver stage and add a silver row."""
    with Session(engine) as s:
        batch = s.get(LeadBatch, batch_id)
        batch.stage = BatchStage.SILVER
        batch.evento_id = evento_id
        s.add(batch)
        dados_brutos = _base_gold_row()
        if dados_brutos_extra:
            dados_brutos.update(dados_brutos_extra)
        silver = LeadSilver(
            batch_id=batch_id,
            row_index=0,
            evento_id=evento_id,
            dados_brutos=dados_brutos,
        )
        s.add(silver)
        s.commit()


def test_materializar_silver_csv_preenche_evento_tipo_via_evento_referencia(engine, monkeypatch):
    """Linhas Silver sem evento/tipo no JSON devem herdar nome e tipo do Evento referenciado (F3 Gold)."""
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    with Session(engine) as s:
        user = _seed_user(s)
        ag = _seed_agencia(s)
        st = _seed_status(s)
        tipo = TipoEvento(nome="Entretenimento Catalogo")
        s.add(tipo)
        s.commit()
        s.refresh(tipo)
        ev = Evento(
            nome="Festival Fora Da Taxonomia",
            cidade="RJ",
            estado="RJ",
            status_id=st.id,
            agencia_id=ag.id,
            tipo_id=tipo.id,
        )
        s.add(ev)
        s.commit()
        s.refresh(ev)

        batch = LeadBatch(
            enviado_por=user.id,
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="x.csv",
            arquivo_bronze=b"a,b\n1,2\n",
            stage=BatchStage.SILVER,
            evento_id=ev.id,
        )
        s.add(batch)
        s.commit()
        s.refresh(batch)

        dados = _base_gold_row()
        dados["evento"] = ""
        dados["tipo_evento"] = ""
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=dados, evento_id=ev.id))
        s.commit()
        batch_id = batch.id

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["evento"] == "Festival Fora Da Taxonomia"
    assert rows[0]["tipo_evento"] == "Entretenimento Catalogo"


class TestGetBatch:
    def test_returns_batch_info(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth)
        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == batch_id
        assert body["stage"] == "bronze"
        assert body["pipeline_status"] == "pending"
        assert body["pipeline_progress"] is None

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.get("/leads/batches/9999", headers=auth)
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.get("/leads/batches/1")
        assert resp.status_code == 401

    def test_returns_pipeline_report_when_present(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        fake_report = {"gate": {"status": "PASS", "decision": "promote", "fail_reasons": [], "warnings": []}}
        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            batch.pipeline_report = fake_report
            batch.pipeline_status = PipelineStatus.PASS
            batch.stage = BatchStage.GOLD
            batch.gold_dq_discarded_rows = 1
            batch.gold_dq_issue_counts = {"cpf_invalid_discarded": 1}
            batch.gold_dq_invalid_records_total = 1
            s.add(batch)
            s.commit()

        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_report"]["gate"]["status"] == "PASS"
        assert body["gold_dq_discarded_rows"] == 1
        assert body["gold_dq_issue_counts"] == {"cpf_invalid_discarded": 1}
        assert body["gold_dq_invalid_records_total"] == 1
        assert body["stage"] == "gold"
        assert body["pipeline_progress"] is None

    def test_returns_pipeline_progress_when_present(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            batch.pipeline_progress = {
                "step": "normalize_rows",
                "label": "Normalizando campos (CPF, datas, telefone, local…)",
                "pct": 40,
                "updated_at": "2026-04-14T12:34:56.789Z",
            }
            s.add(batch)
            s.commit()

        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_progress"] == {
            "step": "normalize_rows",
            "label": "Normalizando campos (CPF, datas, telefone, local…)",
            "pct": 40,
            "updated_at": "2026-04-14T12:34:56.789Z",
        }


class TestExecutarPipeline:
    def test_returns_400_if_stage_not_silver(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        batch_id = _upload_batch(client, auth)
        resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)
        assert resp.status_code == 400
        body = resp.json()
        assert body["detail"]["code"] == "INVALID_STAGE"

    def test_returns_404_for_unknown_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)

        resp = client.post("/leads/batches/9999/executar-pipeline", headers=auth)
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.post("/leads/batches/1/executar-pipeline")
        assert resp.status_code == 401

    def test_queues_pipeline_for_silver_batch(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            batch.pipeline_status = PipelineStatus.PASS
            batch.pipeline_report = {"gate": {"status": "PASS"}}
            batch.gold_dq_discarded_rows = 9
            batch.gold_dq_issue_counts = {"cpf_invalid_discarded": 9}
            batch.gold_dq_invalid_records_total = 9
            s.add(batch)
            s.commit()

        with patch(
            "app.routers.leads.executar_pipeline_gold",
            new_callable=AsyncMock,
        ):
            resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert resp.status_code == 202, resp.text
        body = resp.json()
        assert body["batch_id"] == batch_id
        assert body["status"] == "queued"

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.pipeline_status == PipelineStatus.PENDING
            assert batch.pipeline_report is None
            assert batch.gold_dq_discarded_rows is None
            assert batch.gold_dq_issue_counts is None
            assert batch.gold_dq_invalid_records_total is None
            assert batch.pipeline_progress == {
                "step": "queued",
                "label": "Na fila para processamento",
                "pct": None,
                "updated_at": batch.pipeline_progress["updated_at"],
            }
            assert str(batch.pipeline_progress["updated_at"]).endswith("Z")

        with patch(
            "app.routers.leads.executar_pipeline_gold",
            new_callable=AsyncMock,
        ):
            duplicate_resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert duplicate_resp.status_code == 409
        assert duplicate_resp.json()["detail"]["code"] == "PIPELINE_ALREADY_RUNNING"


class TestExecutarPipelineServiceProgress:
    def test_persists_intermediate_progress_and_clears_it_on_success(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        seen_steps: list[str] = []

        def fake_run_pipeline(config):
            assert config.on_progress is not None

            with Session(engine) as s:
                batch = s.get(LeadBatch, batch_id)
                assert batch.pipeline_progress is not None
                assert batch.pipeline_progress["step"] == "silver_csv"
                seen_steps.append(batch.pipeline_progress["step"])

            config.on_progress(
                PipelineProgressEvent(
                    step="normalize_rows",
                    label="Normalizando campos (CPF, datas, telefone, local…)",
                    pct=40,
                )
            )

            with Session(engine) as s:
                batch = s.get(LeadBatch, batch_id)
                assert batch.pipeline_progress is not None
                assert batch.pipeline_progress["step"] == "normalize_rows"
                assert batch.pipeline_progress["pct"] == 40
                seen_steps.append(batch.pipeline_progress["step"])

            output_dir = config.output_root / config.lote_id
            output_dir.mkdir(parents=True, exist_ok=True)

            consolidated_path = output_dir / FINAL_FILENAME
            consolidated_path.write_text(
                (
                    "nome,cpf,email,telefone,evento,tipo_evento,local,data_evento,data_nascimento\n"
                    "Alice,52998224725,alice@ex.com,11999990000,Park Challenge 2025,ESPORTE,"
                    "Sao Paulo-SP,2026-06-08,1990-01-15\n"
                ),
                encoding="utf-8",
            )

            report_path = output_dir / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "gate": {
                            "status": "PASS",
                            "decision": "promote",
                            "fail_reasons": [],
                            "warnings": [],
                        },
                        "totals": {"discarded_rows": 0},
                        "quality_metrics": {"cpf_invalid_discarded": 0},
                        "invalid_records": [],
                        "exit_code": 0,
                    }
                ),
                encoding="utf-8",
            )

            summary_path = output_dir / "validation-summary.md"
            summary_path.write_text("# summary\n", encoding="utf-8")

            return PipelineResult(
                lote_id=config.lote_id,
                status="PASS",
                decision="promote",
                output_dir=output_dir,
                report_path=report_path,
                summary_path=summary_path,
                consolidated_path=consolidated_path,
                exit_code=0,
            )

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", fake_run_pipeline)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        assert seen_steps == ["silver_csv", "normalize_rows"]

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.pipeline_status == PipelineStatus.PASS
            assert batch.stage == BatchStage.GOLD
            assert batch.pipeline_progress is None


class TestNormalizeRowCPFValidation:
    @pytest.mark.parametrize("cpf", ["52998224726", "11111111111", "12345678909"])
    def test_marks_invalid_cpf_reasons(self, cpf: str) -> None:
        _, reasons, _, _ = _normalize_row(
            _base_gold_row(cpf=cpf),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
        )

        assert "CPF_INVALIDO" in reasons

    def test_accepts_valid_cpf(self) -> None:
        _, reasons, _, _ = _normalize_row(
            _base_gold_row(cpf="52998224725"),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
        )

        assert "CPF_INVALIDO" not in reasons


class TestNormalizeRowLocalidade:
    def test_normalizes_locality_from_local_field(self) -> None:
        normalized, reasons, _, locality = _normalize_row(
            _base_gold_row(local="Sao Paulo-SP"),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
        )

        assert reasons == []
        assert locality.issue_code is None
        assert normalized["cidade"] == "São Paulo"
        assert normalized["estado"] == "SP"
        assert normalized["local"] == "São Paulo-SP"

    def test_marks_city_uf_mismatch_without_promoting_raw_location(self) -> None:
        normalized, reasons, _, locality = _normalize_row(
            _base_gold_row(cidade="Sao Paulo", estado="RJ", local="Sao Paulo-RJ"),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
        )

        assert reasons == []
        assert locality.issue_code == "cidade_uf_mismatch"
        assert normalized["cidade"] == ""
        assert normalized["estado"] == ""
        assert normalized["local"] == ""


class TestNormalizeDataNascimento:
    @pytest.mark.parametrize(
        ("raw_value", "expected_value", "expected_issue"),
        [
            ("", "", BirthDateIssue.MISSING),
            ("   ", "", BirthDateIssue.MISSING),
            ("1990-01-15", "1990-01-15", None),
            ("2099-01-01", "", BirthDateIssue.FUTURE),
            ("1899-12-31", "", BirthDateIssue.BEFORE_MIN),
            ("lixo", "", BirthDateIssue.UNPARSEABLE),
        ],
    )
    def test_normalize_data_nascimento_returns_expected_status(
        self,
        raw_value: str,
        expected_value: str,
        expected_issue: BirthDateIssue | None,
    ) -> None:
        normalized, issue = normalize_data_nascimento(raw_value, ref_date=date_type(2026, 1, 1))

        assert normalized == expected_value
        assert issue == expected_issue


class TestNormalizeRowBirthDateDQ:
    @pytest.mark.parametrize(
        ("raw_value", "expected_issue"),
        [
            ("", BirthDateIssue.MISSING),
            ("lixo", BirthDateIssue.UNPARSEABLE),
            ("2099-01-01", BirthDateIssue.FUTURE),
            ("1899-12-31", BirthDateIssue.BEFORE_MIN),
        ],
    )
    def test_birth_date_issue_does_not_discard_row(
        self,
        raw_value: str,
        expected_issue: BirthDateIssue,
    ) -> None:
        normalized, reasons, issue, _ = _normalize_row(
            _base_gold_row(data_nascimento=raw_value),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
        )

        assert normalized["data_nascimento"] == ""
        assert "DATA_NASCIMENTO_INVALIDA" not in reasons
        assert issue == expected_issue


class TestDatabricksContractBirthDate:
    @pytest.mark.parametrize("data_nascimento", ["2099-01-01", "1899-12-31"])
    def test_rejects_birth_date_outside_allowed_range(self, data_nascimento: str) -> None:
        violations = validate_databricks_contract(
            _contract_frame(data_nascimento=data_nascimento),
            ref_date=date_type(2026, 1, 1),
        )

        assert violations == ["DATA_NASCIMENTO_INVALIDA_NO_PROCESSADO: 1 linha(s)"]


class TestLeadEventoInGoldPipeline:
    """Guarantee LeadEvento creation and idempotency in the Gold pipeline."""

    def test_promote_to_gold_creates_lead_evento(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.gold_dq_discarded_rows == 0
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_issue_counts is not None
            for metric_key in (
                "cpf_invalid_discarded",
                "telefone_invalid",
                "data_evento_invalid",
                "data_nascimento_invalid",
                "data_nascimento_missing",
                "duplicidades_cpf_evento",
                "cidade_fora_mapeamento",
                "localidade_invalida",
                "localidade_nao_resolvida",
                "localidade_fora_brasil",
                "localidade_cidade_uf_inconsistente",
            ):
                assert batch.gold_dq_issue_counts.get(metric_key, 0) == 0

            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id)).all()
            assert len(leads) > 0, "Deve ter criado pelo menos um Lead Gold"

            for lead in leads:
                lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
                assert len(lead_eventos) == 1, f"Lead {lead.id} deve ter exatamente 1 LeadEvento"
                lead_evento = lead_eventos[0]
                assert lead_evento.evento_id == evento.id
                assert lead_evento.source_kind == LeadEventoSourceKind.LEAD_BATCH
                assert lead_evento.source_ref_id == batch_id
                assert lead_evento.tipo_lead == TipoLead.ENTRADA_EVENTO
                assert lead_evento.responsavel_tipo == TipoResponsavel.PROPONENTE
                assert lead_evento.responsavel_nome == evento.nome
                assert lead_evento.responsavel_agencia_id is None

    def test_promote_to_gold_persists_extended_lead_fields(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={
                "id_salesforce": "sf-001",
                "sobrenome": "Silva",
                "sessao": "Sessao VIP",
                "data_compra": "2026-02-10T14:35:00",
                "data_compra_data": "2026-02-10",
                "data_compra_hora": "14:35:00",
                "opt_in": "newsletter",
                "opt_in_id": "opt-123",
                "opt_in_flag": "Sim",
                "metodo_entrega": "digital",
                "rg": "1234567",
                "endereco_rua": "Rua A",
                "endereco_numero": "123",
                "complemento": "Apto 4",
                "bairro": "Centro",
                "cep": "01001-000",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "genero": "Feminino",
                "codigo_promocional": "PROMO10",
                "ingresso_tipo": "VIP",
                "ingresso_qtd": "2",
                "fonte_origem": "crm",
                "is_cliente_bb": "Sim",
                "is_cliente_estilo": "Nao",
            },
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.id_salesforce == "sf-001"
            assert lead.sobrenome == "Silva"
            assert lead.sessao == "Sessao VIP"
            assert lead.data_compra is not None
            assert lead.data_compra.date() == date_type.fromisoformat("2026-02-10")
            assert str(lead.data_compra.time()) == "14:35:00"
            assert lead.data_compra_data == date_type.fromisoformat("2026-02-10")
            assert str(lead.data_compra_hora) == "14:35:00"
            assert lead.opt_in == "newsletter"
            assert lead.opt_in_id == "opt-123"
            assert lead.opt_in_flag is True
            assert lead.metodo_entrega == "digital"
            assert lead.rg == "1234567"
            assert lead.endereco_rua == "Rua A"
            assert lead.endereco_numero == "123"
            assert lead.complemento == "Apto 4"
            assert lead.bairro == "Centro"
            assert lead.cep == "01001-000"
            assert lead.cidade == "São Paulo"
            assert lead.estado == "SP"
            assert lead.genero == "Feminino"
            assert lead.codigo_promocional == "PROMO10"
            assert lead.ingresso_tipo == "VIP"
            assert lead.ingresso_qtd == 2
            assert lead.fonte_origem == "crm"
            assert lead.is_cliente_bb is True
            assert lead.is_cliente_estilo is False

    def test_promote_to_gold_activation_batch_creates_ativacao_lead_and_lead_evento(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            agencia = _seed_agencia(s)
            evento = _seed_evento(s, agencia_id=agencia.id)
            ativacao = Ativacao(nome="Stand import", evento_id=evento.id)
            s.add(ativacao)
            s.commit()
            s.refresh(ativacao)
            evento_id = evento.id
            ativacao_id = ativacao.id

        batch_id = _upload_batch(
            client,
            auth,
            evento_id=evento_id,
            origem_lote="ativacao",
            ativacao_id=ativacao_id,
        )
        _promote_to_silver(engine, batch_id, evento_id)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id)).all()
            assert len(leads) > 0
            for lead in leads:
                al = s.exec(
                    select(AtivacaoLead)
                    .where(AtivacaoLead.ativacao_id == ativacao_id)
                    .where(AtivacaoLead.lead_id == lead.id)
                ).first()
                assert al is not None
                lead_eventos = s.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
                assert len(lead_eventos) == 1
                le = lead_eventos[0]
                assert le.evento_id == evento_id
                assert le.source_kind == LeadEventoSourceKind.ACTIVATION
                assert le.source_ref_id == al.id
                assert le.tipo_lead == TipoLead.ATIVACAO
                assert le.responsavel_tipo == TipoResponsavel.AGENCIA

    def test_failed_rerun_clears_previous_pipeline_snapshot(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            batch.pipeline_status = PipelineStatus.PASS
            batch.pipeline_report = {"gate": {"status": "PASS"}}
            batch.gold_dq_discarded_rows = 7
            batch.gold_dq_issue_counts = {"cpf_invalid_discarded": 7}
            batch.gold_dq_invalid_records_total = 7
            s.add(batch)
            s.commit()

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        def _raise_pipeline_error(*_args, **_kwargs):
            raise RuntimeError("pipeline exploded")

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", _raise_pipeline_error)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.pipeline_status == PipelineStatus.FAIL
            assert batch.pipeline_report is None
            assert batch.pipeline_progress is None
            assert batch.gold_dq_discarded_rows is None
            assert batch.gold_dq_issue_counts is None
            assert batch.gold_dq_invalid_records_total is None

        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_status"] == "fail"
        assert body["pipeline_report"] is None
        assert body["pipeline_progress"] is None
        assert body["gold_dq_discarded_rows"] is None
        assert body["gold_dq_issue_counts"] is None
        assert body["gold_dq_invalid_records_total"] is None

    def test_missing_birth_date_keeps_lead_and_records_dq(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={"data_nascimento": "   "},
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS_WITH_WARNINGS
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("data_nascimento_missing") == 1
            assert batch.gold_dq_issue_counts.get("data_nascimento_invalid") == 0
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["invalid_records"] == []
            assert batch.pipeline_report["gate"]["warnings"] == ["DATA_NASCIMENTO_AUSENTE"]
            controle = batch.pipeline_report["data_nascimento_controle"]
            assert len(controle) == 1
            assert controle[0]["source_file"] == "silver_input.csv"
            assert controle[0]["source_sheet"] == ""
            assert controle[0]["source_row"] > 0
            assert controle[0]["issue"] == "missing"

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.data_nascimento is None

    def test_invalid_locality_keeps_lead_and_records_dq(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={
                "cidade": "Sao Paulo",
                "estado": "RJ",
                "local": "Sao Paulo-RJ",
            },
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS_WITH_WARNINGS
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("localidade_invalida") == 1
            assert batch.gold_dq_issue_counts.get("localidade_cidade_uf_inconsistente") == 1
            assert batch.gold_dq_issue_counts.get("localidade_nao_resolvida") == 0
            assert batch.gold_dq_issue_counts.get("localidade_fora_brasil") == 0
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["invalid_records"] == []
            assert batch.pipeline_report["gate"]["warnings"] == ["LOCALIDADE_INVALIDA"]
            controle = batch.pipeline_report["localidade_controle"]
            assert len(controle) == 1
            assert controle[0]["source_file"] == "silver_input.csv"
            assert controle[0]["source_sheet"] == ""
            assert controle[0]["source_row"] > 0
            assert controle[0]["issue"] == "cidade_uf_mismatch"
            assert controle[0]["raw_cidade"] == "Sao Paulo"
            assert controle[0]["raw_estado"] == "RJ"
            assert controle[0]["raw_local"] == "Sao Paulo-RJ"

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.cidade is None
            assert lead.estado is None
            assert lead.sessao is None

    @pytest.mark.parametrize(
        ("raw_birth_date", "expected_issue"),
        [
            ("lixo", "unparseable"),
            ("2099-01-01", "future"),
            ("1899-12-31", "before_min"),
        ],
    )
    def test_invalid_birth_date_keeps_lead_and_records_dq(
        self,
        client,
        engine,
        monkeypatch,
        raw_birth_date: str,
        expected_issue: str,
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={"data_nascimento": raw_birth_date},
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS_WITH_WARNINGS
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("data_nascimento_missing") == 0
            assert batch.gold_dq_issue_counts.get("data_nascimento_invalid") == 1
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["invalid_records"] == []
            assert batch.pipeline_report["gate"]["warnings"] == ["DATA_NASCIMENTO_INVALIDA"]
            controle = batch.pipeline_report["data_nascimento_controle"]
            assert len(controle) == 1
            assert controle[0]["source_file"] == "silver_input.csv"
            assert controle[0]["source_sheet"] == ""
            assert controle[0]["source_row"] > 0
            assert controle[0]["issue"] == expected_issue

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.data_nascimento is None

    def test_reprocess_does_not_duplicate_lead_evento(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))
        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id)).all()
            for lead in leads:
                lead_eventos = s.exec(
                    select(LeadEvento)
                    .where(LeadEvento.lead_id == lead.id)
                    .where(LeadEvento.evento_id == evento.id)
                ).all()
                assert len(lead_eventos) == 1, "Nao deve duplicar LeadEvento"
