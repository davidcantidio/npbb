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
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect as sa_inspect
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
from lead_pipeline.constants import ALL_COLUMNS, FINAL_FILENAME, TIPO_EVENTO_PADRAO
from lead_pipeline.contracts import validate_databricks_contract
from lead_pipeline.normalization import BirthDateIssue, normalize_data_nascimento
from lead_pipeline.pipeline import PipelineConfig, PipelineProgressEvent, PipelineResult, _normalize_row, run_pipeline
from lead_pipeline.source_adapter import AdaptedInput, CITY_OUT_COL, REJECT_REASON_COL, ROW_COL_SOURCE, SHEET_COL_SOURCE


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


def _seed_user(
    session: Session,
    *,
    email: str = "gold@npbb.com.br",
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


def _seed_evento(session: Session, *, agencia_id: int | None = None) -> Evento:
    ev_status = _seed_status(session)
    evento = Evento(
        nome="Park Challenge 2025",
        cidade="Sao Paulo",
        estado="SP",
        data_inicio_prevista=date_type(2026, 6, 8),
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


def _auth_header(
    client: TestClient,
    session: Session,
    *,
    email: str = "gold@npbb.com.br",
    password: str = "senha123",
) -> dict[str, str]:
    _seed_user(session, email=email, password=password)
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


CSV_CONTENT = b"nome,cpf,email,telefone\nAlice,52998224725,alice@ex.com,11999990000\n"


def _xlsx_with_preamble(*, sheet_name: str = "Participantes") -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    for idx in range(8):
        ws.append([f"linha solta {idx + 1}", "", ""])
    ws.append(["nome", "cpf", "email"])
    ws.append(["Alice", "52998224725", "alice@ex.com"])
    ws.append(["Bob", "39053344705", "bob@ex.com"])

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _base_gold_row(
    *,
    cpf: str = "52998224725",
    data_nascimento: str = "1990-01-15",
    data_evento: str = "2026-06-08",
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
        "data_evento": data_evento,
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
    enrichment_only: bool | None = None,
    origem_lote: str | None = None,
    ativacao_id: int | None = None,
    tipo_lead_proponente: str | None = None,
    file_content: bytes | None = None,
) -> int:
    data: dict[str, str] = {
        "plataforma_origem": plataforma,
        "data_envio": "2026-03-05T10:00:00",
    }
    if evento_id is not None:
        data["evento_id"] = str(evento_id)
    if enrichment_only is not None:
        data["enrichment_only"] = "true" if enrichment_only else "false"
    if origem_lote is not None:
        data["origem_lote"] = origem_lote
    if ativacao_id is not None:
        data["ativacao_id"] = str(ativacao_id)
    if tipo_lead_proponente is not None:
        data["tipo_lead_proponente"] = tipo_lead_proponente

    payload = file_content if file_content is not None else CSV_CONTENT
    resp = client.post(
        "/leads/batches",
        headers=auth,
        files={"file": ("leads.csv", io.BytesIO(payload), "text/csv")},
        data=data,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _promote_to_silver(
    engine,
    batch_id: int,
    evento_id: int | None,
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


def test_materializar_silver_csv_sobrescreve_evento_espurio_pelo_referencial(engine, monkeypatch):
    """Planilha com texto em `evento` que nao bate na taxonomia nao deve bloquear o nome do Evento no banco."""
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
        dados["evento"] = "lixo-nao-mapeado"
        dados["tipo_evento"] = ""
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=dados, evento_id=ev.id))
        s.commit()
        batch_id = batch.id

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["evento"] == "Festival Fora Da Taxonomia"
    assert rows[0]["tipo_evento"] == "Entretenimento Catalogo"


def test_materializar_silver_csv_tipo_padrao_quando_evento_sem_tipo_no_banco(engine, monkeypatch):
    """Evento sem `tipo_id` ainda deve gerar `tipo_evento` para a taxonomia nao falhar no gate."""
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    with Session(engine) as s:
        user = _seed_user(s)
        ag = _seed_agencia(s)
        st = _seed_status(s)
        ev = Evento(
            nome="Festival Fora Da Taxonomia",
            cidade="RJ",
            estado="RJ",
            status_id=st.id,
            agencia_id=ag.id,
            tipo_id=None,
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
    assert rows[0]["evento"] == "Festival Fora Da Taxonomia"
    assert rows[0]["tipo_evento"] == TIPO_EVENTO_PADRAO


def test_materializar_silver_csv_sobrescreve_data_evento_pela_data_canonica_do_evento(engine, monkeypatch):
    """Lote ancorado em evento_id deve materializar data_evento a partir do cadastro do Evento."""
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    with Session(engine) as s:
        user = _seed_user(s)
        ag = _seed_agencia(s)
        st = _seed_status(s)
        tipo = TipoEvento(nome="Corrida")
        s.add(tipo)
        s.commit()
        s.refresh(tipo)
        ev = Evento(
            nome="Evento Com Data Canonica",
            cidade="RJ",
            estado="RJ",
            status_id=st.id,
            agencia_id=ag.id,
            tipo_id=tipo.id,
            data_inicio_prevista=date_type(2026, 6, 8),
            data_inicio_realizada=date_type(2026, 6, 10),
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

        dados = _base_gold_row(data_evento="nao-e-data")
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=dados, evento_id=ev.id))
        s.commit()
        batch_id = batch.id

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["evento"] == "Evento Com Data Canonica"
    assert rows[0]["tipo_evento"] == "Corrida"
    assert rows[0]["data_evento"] == "2026-06-10"


def test_materializar_silver_csv_sobrescreve_local_pela_localidade_canonica_do_evento(engine, monkeypatch):
    """Lote ancorado em evento_id deve materializar `local` a partir do cadastro do Evento."""
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    with Session(engine) as s:
        user = _seed_user(s)
        ag = _seed_agencia(s)
        st = _seed_status(s)
        ev = Evento(
            nome="Evento Com Local Canonico",
            cidade="Rio de Janeiro",
            estado="RJ",
            status_id=st.id,
            agencia_id=ag.id,
            data_inicio_prevista=date_type(2026, 6, 8),
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

        dados = _base_gold_row(local="Londres-UK")
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=dados, evento_id=ev.id))
        s.commit()
        batch_id = batch.id

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["local"] == "Rio de Janeiro-RJ"


def test_materializar_silver_csv_orders_rows_by_row_index(engine, monkeypatch):
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    with Session(engine) as s:
        user = _seed_user(s)
        evento = _seed_evento(s)
        batch = LeadBatch(
            enviado_por=user.id,
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="leads.xlsx",
            arquivo_bronze=b"a,b\n1,2\n",
            stage=BatchStage.SILVER,
            evento_id=evento.id,
        )
        s.add(batch)
        s.commit()
        s.refresh(batch)

        rows = [
            (
                10,
                {
                    **_base_gold_row(cpf="11144477735"),
                    "nome": "Linha Dez",
                    "source_file": "leads.xlsx",
                    "source_sheet": "Participantes",
                    "source_row": 21,
                },
            ),
            (
                0,
                {
                    **_base_gold_row(cpf="52998224725"),
                    "nome": "Linha Zero",
                    "source_file": "leads.xlsx",
                    "source_sheet": "Participantes",
                    "source_row": 11,
                },
            ),
            (
                1,
                {
                    **_base_gold_row(cpf="39053344705"),
                    "nome": "Linha Um",
                    "source_file": "leads.xlsx",
                    "source_sheet": "Participantes",
                    "source_row": 12,
                },
            ),
        ]
        for row_index, dados in rows:
            s.add(LeadSilver(batch_id=batch.id, row_index=row_index, dados_brutos=dados, evento_id=evento.id))
        s.commit()
        batch_id = int(batch.id)

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        materialized_rows = list(csv.DictReader(fh))

    assert [row["nome"] for row in materialized_rows] == ["Linha Zero", "Linha Um", "Linha Dez"]
    assert [row["source_row"] for row in materialized_rows] == ["11", "12", "21"]
    assert all(row["source_file"] == "leads.xlsx" for row in materialized_rows)
    assert all(row["source_sheet"] == "Participantes" for row in materialized_rows)


def test_materializar_prefers_source_row_original_over_source_row(engine, monkeypatch):
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-orig-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    def _unexpected_bronze_reread(*args, **kwargs):
        raise AssertionError("CSV com source_row_original nao deve reler o Bronze so porque source_sheet e vazio.")

    monkeypatch.setattr("app.services.lead_pipeline_service.read_raw_file_rows", _unexpected_bronze_reread)

    with Session(engine) as s:
        user = _seed_user(s)
        evento = _seed_evento(s)
        batch = LeadBatch(
            enviado_por=user.id,
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="leads.csv",
            arquivo_bronze=b"a,b\n1,2\n",
            stage=BatchStage.SILVER,
            evento_id=evento.id,
        )
        s.add(batch)
        s.commit()
        s.refresh(batch)
        dados = _base_gold_row()
        dados["source_file"] = "leads.csv"
        dados["source_sheet"] = ""
        dados["source_row"] = 99
        dados["source_row_original"] = 42
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=dados, evento_id=evento.id))
        s.commit()
        batch_id = int(batch.id)

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        row = next(csv.DictReader(fh))
    assert row["source_row"] == "42"


def test_materializar_legacy_csv_recovers_physical_source_rows_from_bronze(engine, monkeypatch):
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-legacy-csv-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    bronze_csv = (
        b"nome,cpf,email\n"
        b"Alice,52998224725,alice@ex.com\n"
        b"\n"
        b"Bob,39053344705,bob@ex.com\n"
    )

    with Session(engine) as s:
        user = _seed_user(s)
        evento = _seed_evento(s)
        batch = LeadBatch(
            enviado_por=user.id,
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="legacy.csv",
            arquivo_bronze=bronze_csv,
            stage=BatchStage.SILVER,
            evento_id=evento.id,
        )
        s.add(batch)
        s.commit()
        s.refresh(batch)

        first = _base_gold_row()
        first["nome"] = "Alice"
        second = _base_gold_row(cpf="39053344705")
        second["nome"] = "Bob"
        second["email"] = "bob@ex.com"
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=first, evento_id=evento.id))
        s.add(LeadSilver(batch_id=batch.id, row_index=1, dados_brutos=second, evento_id=evento.id))
        s.commit()
        batch_id = int(batch.id)

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert [row["nome"] for row in rows] == ["Alice", "Bob"]
    assert [row["source_file"] for row in rows] == ["legacy.csv", "legacy.csv"]
    assert [row["source_sheet"] for row in rows] == ["", ""]
    assert [row["source_row"] for row in rows] == ["2", "4"]


def test_materializar_legacy_xlsx_recovers_sheet_and_physical_source_rows_from_bronze(engine, monkeypatch):
    import csv

    tmp_root = Path("backend/tmp-pytest") / f"mat-legacy-xlsx-{uuid4().hex}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.services.lead_pipeline_service.TMP_ROOT", tmp_root)

    from app.services.lead_pipeline_service import materializar_silver_como_csv

    with Session(engine) as s:
        user = _seed_user(s)
        evento = _seed_evento(s)
        batch = LeadBatch(
            enviado_por=user.id,
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="legacy.xlsx",
            arquivo_bronze=_xlsx_with_preamble(),
            stage=BatchStage.SILVER,
            evento_id=evento.id,
        )
        s.add(batch)
        s.commit()
        s.refresh(batch)

        first = _base_gold_row()
        first["nome"] = "Alice"
        second = _base_gold_row(cpf="39053344705")
        second["nome"] = "Bob"
        second["email"] = "bob@ex.com"
        s.add(LeadSilver(batch_id=batch.id, row_index=0, dados_brutos=first, evento_id=evento.id))
        s.add(LeadSilver(batch_id=batch.id, row_index=1, dados_brutos=second, evento_id=evento.id))
        s.commit()
        batch_id = int(batch.id)

    with Session(engine) as s:
        path = materializar_silver_como_csv(batch_id, s)

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert [row["nome"] for row in rows] == ["Alice", "Bob"]
    assert [row["source_file"] for row in rows] == ["legacy.xlsx", "legacy.xlsx"]
    assert [row["source_sheet"] for row in rows] == ["Participantes", "Participantes"]
    assert [row["source_row"] for row in rows] == ["10", "11"]


def test_configure_lead_gold_statement_timeout_sets_local_timeout_for_postgres(monkeypatch):
    from app.services.lead_pipeline_service import _configure_lead_gold_statement_timeout

    executed: list[str] = []

    class _FakeDialect:
        name = "postgresql"

    class _FakeBind:
        dialect = _FakeDialect()

    class _FakeSession:
        def get_bind(self):
            return _FakeBind()

        def exec(self, statement):
            executed.append(str(statement))

    monkeypatch.setenv("LEAD_GOLD_STATEMENT_TIMEOUT_MS", "12345")

    _configure_lead_gold_statement_timeout(_FakeSession())

    assert executed == ["SET LOCAL statement_timeout = 12345"]


def test_configure_lead_gold_statement_timeout_is_noop_on_sqlite():
    from app.services.lead_pipeline_service import _configure_lead_gold_statement_timeout

    executed: list[str] = []

    class _FakeDialect:
        name = "sqlite"

    class _FakeBind:
        dialect = _FakeDialect()

    class _FakeSession:
        def get_bind(self):
            return _FakeBind()

        def exec(self, statement):
            executed.append(str(statement))

    _configure_lead_gold_statement_timeout(_FakeSession())

    assert executed == []


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

    def test_hides_batch_from_other_user(self, client, engine):
        with Session(engine) as s:
            owner_auth = _auth_header(client, s, email="gold-owner@npbb.com.br", password="senha123")
            other_auth = _auth_header(client, s, email="gold-other@npbb.com.br", password="senha456")

        batch_id = _upload_batch(client, owner_auth)
        resp = client.get(f"/leads/batches/{batch_id}", headers=other_auth)
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
                # Futuro: garante que o heuristica de orfao nao marca como stale neste teste.
                "updated_at": "2099-01-01T12:34:56.789Z",
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
            "updated_at": "2099-01-01T12:34:56.789Z",
        }
        assert isinstance(body.get("gold_pipeline_stale_after_seconds"), int)
        assert body.get("gold_pipeline_progress_is_stale") is False

    def test_get_batch_marks_progress_stale_when_updated_at_old(self, client, engine):
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
                "pct": 10,
                "updated_at": "2000-01-01T00:00:00Z",
            }
            s.add(batch)
            s.commit()

        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["gold_pipeline_progress_is_stale"] is True


def test_load_batch_without_bronze_defers_blob_column(engine):
    from app.services.lead_pipeline_service import load_batch_without_bronze

    with Session(engine) as s:
        user = _seed_user(s)
        batch = LeadBatch(
            enviado_por=user.id or 0,
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            data_upload=datetime.now(timezone.utc),
            nome_arquivo_original="gigante.xlsx",
            arquivo_bronze=b"x" * 1024,
            stage=BatchStage.SILVER,
            pipeline_status=PipelineStatus.PENDING,
        )
        s.add(batch)
        s.commit()
        s.refresh(batch)
        batch_id = int(batch.id)

    with Session(engine) as s:
        batch = load_batch_without_bronze(s, batch_id)
        assert batch is not None
        assert "arquivo_bronze" in sa_inspect(batch).unloaded
        assert batch.nome_arquivo_original == "gigante.xlsx"
        assert "arquivo_bronze" in sa_inspect(batch).unloaded
        assert batch.arquivo_bronze == b"x" * 1024
        assert "arquivo_bronze" not in sa_inspect(batch).unloaded


def test_claim_next_gold_pipeline_batch_does_not_touch_expired_batch_after_commit(monkeypatch):
    from app.services import lead_pipeline_service

    class _CommitExpiringBatch:
        def __init__(self) -> None:
            self._id = 244
            self.pipeline_progress = {"step": "queued"}
            self.pipeline_report = None
            self._expired_after_commit = False

        @property
        def id(self):
            if self._expired_after_commit:
                raise RuntimeError("post-commit reload attempted")
            return self._id

    class _ExecResult:
        def __init__(self, batch: _CommitExpiringBatch) -> None:
            self._batch = batch

        def first(self):
            return self._batch

    class _FakeSession:
        def __init__(self, batch: _CommitExpiringBatch) -> None:
            self.batch = batch
            self.committed = False

        def exec(self, _stmt):
            return _ExecResult(self.batch)

        def add(self, _obj) -> None:
            return None

        def commit(self) -> None:
            self.committed = True
            self.batch._expired_after_commit = True

    batch = _CommitExpiringBatch()
    session = _FakeSession(batch)

    monkeypatch.setattr(lead_pipeline_service, "_resume_context_from_batch", lambda _batch: None)

    def _set_pipeline_progress(fake_batch: _CommitExpiringBatch, *, step: str, **_kwargs) -> None:
        fake_batch.pipeline_progress = {"step": step}

    monkeypatch.setattr(lead_pipeline_service, "set_pipeline_progress", _set_pipeline_progress)

    claimed = lead_pipeline_service.claim_next_gold_pipeline_batch(session)

    assert claimed == 244
    assert session.committed is True
    assert batch.pipeline_progress == {"step": "silver_csv"}


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

    def test_hides_pipeline_dispatch_from_other_user(self, client, engine):
        with Session(engine) as s:
            owner_auth = _auth_header(client, s, email="dispatch-owner@npbb.com.br", password="senha123")
            other_auth = _auth_header(client, s, email="dispatch-other@npbb.com.br", password="senha456")
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, owner_auth)
        _promote_to_silver(engine, batch_id, evento.id)

        resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=other_auth)
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
            "app.routers.leads.executar_pipeline_gold_em_thread",
        ):
            resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert resp.status_code == 202, resp.text
        body = resp.json()
        assert body["batch_id"] == batch_id
        assert body["status"] == "queued"
        assert body.get("reclaimed_stale_lock") is False

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
            "app.routers.leads.executar_pipeline_gold_em_thread",
        ):
            duplicate_resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert duplicate_resp.status_code == 409
        assert duplicate_resp.json()["detail"]["code"] == "PIPELINE_ALREADY_RUNNING"

    def test_dispatch_does_not_touch_expired_batch_after_commit(self, monkeypatch):
        from app.routers import leads as leads_router

        class _CommitExpiringBatch:
            def __init__(self) -> None:
                self.id = 243
                self.pipeline_progress = None
                self.pipeline_report = None
                self._stage = BatchStage.SILVER
                self._pipeline_status = PipelineStatus.PASS
                self._evento_id = 12
                self._expired_after_commit = False

            def _read(self, value):
                if self._expired_after_commit:
                    raise RuntimeError("post-commit reload attempted")
                return value

            @property
            def stage(self):
                return self._read(self._stage)

            @stage.setter
            def stage(self, value):
                self._stage = value

            @property
            def pipeline_status(self):
                return self._read(self._pipeline_status)

            @pipeline_status.setter
            def pipeline_status(self, value):
                self._pipeline_status = value

            @property
            def evento_id(self):
                return self._read(self._evento_id)

            @evento_id.setter
            def evento_id(self, value):
                self._evento_id = value

        class _FakeSession:
            def __init__(self, batch: _CommitExpiringBatch) -> None:
                self.batch = batch
                self.committed = False

            def add(self, _obj) -> None:
                return None

            def commit(self) -> None:
                self.committed = True
                self.batch._expired_after_commit = True

        batch = _CommitExpiringBatch()
        session = _FakeSession(batch)

        monkeypatch.setattr(
            leads_router,
            "load_batch_without_bronze_for_update",
            lambda _session, _batch_id, **_kwargs: batch,
        )

        def _queue_pipeline(fake_batch: _CommitExpiringBatch) -> None:
            fake_batch.pipeline_status = PipelineStatus.PENDING
            fake_batch.pipeline_progress = {
                "step": "queued",
                "label": "Na fila para processamento",
                "pct": None,
                "updated_at": "2026-01-01T00:00:00Z",
            }

        monkeypatch.setattr(leads_router, "queue_pipeline_batch", _queue_pipeline)

        response = asyncio.run(
            leads_router.disparar_pipeline(
                batch_id=243,
                session=session,
                current_user=SimpleNamespace(id=999),
            )
        )

        assert session.committed is True
        assert response.batch_id == 243
        assert response.status == "queued"
        assert response.reclaimed_stale_lock is False

    def test_failed_insert_rerun_keeps_resume_checkpoint_in_queued_progress(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            batch.pipeline_status = PipelineStatus.FAIL
            batch.pipeline_report = {
                "gate": {"status": "FAIL", "decision": "hold", "fail_reasons": [], "warnings": []},
                "failure_context": {
                    "step": "insert_leads",
                    "resume_context": {
                        "step": "insert_leads",
                        "committed_rows": 2,
                        "total_rows": 3,
                    },
                },
            }
            s.add(batch)
            s.commit()

        with patch("app.routers.leads.executar_pipeline_gold_em_thread"):
            resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert resp.status_code == 202, resp.text
        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_report is None
            assert batch.pipeline_progress is not None
            assert batch.pipeline_progress["step"] == "queued"
            assert batch.pipeline_progress["resume_step"] == "insert_leads"
            assert batch.pipeline_progress["committed_rows"] == 2
            assert batch.pipeline_progress["total_rows"] == 3

    def test_reclaims_stale_pipeline_progress_lock(self, client, engine):
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
                "pct": 22,
                "updated_at": "2000-01-01T00:00:00Z",
            }
            batch.pipeline_status = PipelineStatus.PENDING
            s.add(batch)
            s.commit()

        with patch("app.routers.leads.executar_pipeline_gold_em_thread"):
            resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert resp.status_code == 202, resp.text
        body = resp.json()
        assert body.get("reclaimed_stale_lock") is True
        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.pipeline_progress is not None
            assert batch.pipeline_progress["step"] == "queued"

    def test_allows_dispatch_when_pipeline_status_stalled(self, client, engine):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            batch.pipeline_status = PipelineStatus.STALLED
            batch.pipeline_report = {
                "gate": {"status": "FAIL", "decision": "hold", "fail_reasons": ["WORKER_LOST"], "warnings": []},
                "failure_context": {
                    "step": "normalize_rows",
                    "message": "Execucao interrompida",
                    "resume_context": {
                        "step": "insert_leads",
                        "committed_rows": 1,
                        "total_rows": 5,
                    },
                },
            }
            batch.pipeline_progress = None
            s.add(batch)
            s.commit()

        with patch("app.routers.leads.executar_pipeline_gold_em_thread"):
            resp = client.post(f"/leads/batches/{batch_id}/executar-pipeline", headers=auth)

        assert resp.status_code == 202, resp.text
        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.pipeline_status == PipelineStatus.PENDING
            assert batch.pipeline_progress is not None
            assert batch.pipeline_progress["step"] == "queued"


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
        persisted_events: list[tuple[str, str, int | None]] = []

        original_persist_progress = lead_pipeline_service._persist_pipeline_progress

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

        def record_progress(engine_arg, persisted_batch_id, event):
            persisted_events.append((event.step, event.label, event.pct))
            original_persist_progress(engine_arg, persisted_batch_id, event)

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", fake_run_pipeline)
        monkeypatch.setattr(lead_pipeline_service, "_persist_pipeline_progress", record_progress)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        assert seen_steps == ["silver_csv", "normalize_rows"]
        assert persisted_events[0][0] == "normalize_rows"
        assert "Normalizando campos" in persisted_events[0][1]
        assert persisted_events[0][2] == 40
        assert persisted_events[1:] == [
            ("insert_leads", "Inserindo leads Gold no banco (0/1)", 0),
            ("insert_leads", "Inserindo leads Gold no banco (1/1)", 100),
        ]

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch.pipeline_status == PipelineStatus.PASS
            assert batch.stage == BatchStage.GOLD
            assert batch.pipeline_progress is None

    def test_insert_failure_persists_resume_context_from_last_committed_chunk(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        tmp_root = Path("backend/tmp-pytest") / f"insert-resume-fail-{uuid4().hex}"
        report_dir = tmp_root / "output" / str(batch_id)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.json"
        consolidated_path = report_dir / FINAL_FILENAME
        summary_path = report_dir / "summary.md"
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
        consolidated_path.write_text(
            "nome,cpf,email\nA,1,a@example.com\nB,2,b@example.com\nC,3,c@example.com\n",
            encoding="utf-8",
        )
        summary_path.write_text("# summary\n", encoding="utf-8")

        def fake_run_pipeline(_config):
            return PipelineResult(
                lote_id=str(batch_id),
                status="PASS",
                decision="promote",
                output_dir=report_dir,
                report_path=report_path,
                summary_path=summary_path,
                consolidated_path=consolidated_path,
                exit_code=0,
            )

        def fake_insert_failure(_batch, _consolidated_path, _db, *, on_progress=None, resume_context=None):
            assert resume_context is None
            assert on_progress is not None
            on_progress(
                lead_pipeline_service._build_insert_leads_progress_event(
                    processed_rows=0,
                    total_rows=3,
                    committed_rows=0,
                )
            )
            on_progress(
                lead_pipeline_service._build_insert_leads_progress_event(
                    processed_rows=2,
                    total_rows=3,
                    committed_rows=2,
                )
            )
            raise RuntimeError("insert exploded after checkpoint")

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", fake_run_pipeline)
        monkeypatch.setattr(lead_pipeline_service, "_inserir_leads_gold", fake_insert_failure)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.FAIL
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["failure_context"]["resume_context"] == {
                "step": "insert_leads",
                "committed_rows": 2,
                "total_rows": 3,
            }

    def test_rerun_after_failed_insert_resumes_from_last_committed_row(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, evento_id=evento.id)
        _promote_to_silver(engine, batch_id, evento.id)

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            preexisting_rows = [
                ("Alice", "52998224725", "alice@ex.com"),
                ("Bruno", "11144477735", "bruno@ex.com"),
            ]
            for nome, cpf, email in preexisting_rows:
                lead = Lead(
                    batch_id=batch_id,
                    nome=nome,
                    email=email,
                    cpf=cpf,
                    evento_nome=evento.nome,
                    sessao="Sao Paulo-SP",
                )
                s.add(lead)
                s.commit()
                s.refresh(lead)
                s.add(
                    LeadEvento(
                        lead_id=lead.id,
                        evento_id=evento.id,
                        source_kind=LeadEventoSourceKind.LEAD_BATCH,
                        source_ref_id=batch_id,
                        tipo_lead=TipoLead.ENTRADA_EVENTO,
                        responsavel_tipo=TipoResponsavel.PROPONENTE,
                        responsavel_nome=evento.nome,
                    )
                )
                s.commit()

            batch.pipeline_status = PipelineStatus.FAIL
            batch.pipeline_report = {
                "gate": {"status": "FAIL", "decision": "hold", "fail_reasons": [], "warnings": []},
                "failure_context": {
                    "step": "insert_leads",
                    "resume_context": {
                        "step": "insert_leads",
                        "committed_rows": 2,
                        "total_rows": 3,
                    },
                },
            }
            s.add(batch)
            s.commit()

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        tmp_root = Path("backend/tmp-pytest") / f"insert-resume-success-{uuid4().hex}"
        report_dir = tmp_root / "output" / str(batch_id)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.json"
        consolidated_path = report_dir / FINAL_FILENAME
        summary_path = report_dir / "summary.md"
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
        consolidated_path.write_text(
            (
                "nome,cpf,email,local,data_evento\n"
                "Alice,52998224725,alice@ex.com,Sao Paulo-SP,2026-06-08\n"
                "Bruno,11144477735,bruno@ex.com,Sao Paulo-SP,2026-06-08\n"
                "Carla,39053344705,carla@ex.com,Sao Paulo-SP,2026-06-08\n"
            ),
            encoding="utf-8",
        )
        summary_path.write_text("# summary\n", encoding="utf-8")

        def fake_run_pipeline(_config):
            return PipelineResult(
                lote_id=str(batch_id),
                status="PASS",
                decision="promote",
                output_dir=report_dir,
                report_path=report_path,
                summary_path=summary_path,
                consolidated_path=consolidated_path,
                exit_code=0,
            )

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", fake_run_pipeline)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS
            assert batch.stage == BatchStage.GOLD
            leads = s.exec(select(Lead).where(Lead.batch_id == batch_id).order_by(Lead.email)).all()
            assert [lead.email for lead in leads] == [
                "alice@ex.com",
                "bruno@ex.com",
                "carla@ex.com",
            ]


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

    def test_run_pipeline_keeps_numeric_cpf_and_phone_before_report_stringification(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        raw_row = {column: "" for column in ALL_COLUMNS}
        raw_row.update(
            {
                "nome": "Alice",
                "cpf": 52998224725.0,
                "email": "alice@ex.com",
                "telefone": 11999990000.0,
                "evento": "Park Challenge 2025",
                "tipo_evento": "ESPORTE",
                "local": "Sao Paulo-SP",
                "data_evento": "2026-06-08",
                "data_nascimento": "1990-01-15",
                CITY_OUT_COL: False,
                SHEET_COL_SOURCE: "Planilha 1",
                ROW_COL_SOURCE: 2,
                REJECT_REASON_COL: "",
            }
        )
        adapted = AdaptedInput(
            dataframe=pd.DataFrame([raw_row]),
            source_profiles=["numeric-test"],
            fail_reasons=[],
            warnings=[],
        )

        def fake_adapt_source_file(_input_file: Path) -> AdaptedInput:
            return adapted

        monkeypatch.setattr("lead_pipeline.pipeline.adapt_source_file", fake_adapt_source_file)

        input_file = tmp_path / "numeric.xlsx"
        input_file.write_bytes(b"not-used")
        result = run_pipeline(
            PipelineConfig(
                lote_id="numeric-cpf",
                input_files=[input_file],
                output_root=tmp_path / "output",
            )
        )

        consolidated = pd.read_csv(result.consolidated_path, dtype=str, keep_default_na=False)
        report = json.loads(result.report_path.read_text(encoding="utf-8"))

        assert result.decision == "promote"
        assert len(consolidated.index) == 1
        row = consolidated.to_dict(orient="records")[0]
        assert row["nome"] == "Alice"
        assert row["cpf"] == "52998224725"
        assert row["telefone"] == "11999990000"
        assert row["email"] == "alice@ex.com"
        assert row["data_nascimento"] == "1990-01-15"
        assert row["evento"] == "Park Challenge 2025"
        assert row["local"] == "São Paulo-SP"
        assert row["cidade"] == "São Paulo"
        assert row["estado"] == "SP"
        assert report["quality_metrics"]["cpf_invalid_discarded"] == 0
        assert report["totals"]["valid_rows"] == 1
        assert report["invalid_records"] == []


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

    def test_anchored_event_locality_keeps_event_local_and_lead_city_state_separate(self) -> None:
        normalized, reasons, _, locality = _normalize_row(
            _base_gold_row(local="Rio de Janeiro-RJ", cidade="Sao Paulo", estado="SP"),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
            event_locality_owned=True,
        )

        assert reasons == []
        assert locality.issue_code is None
        assert normalized["local"] == "Rio de Janeiro-RJ"
        assert normalized["cidade"] == "São Paulo"
        assert normalized["estado"] == "SP"


    def test_anchored_event_locality_preserves_event_model_value_when_reference_misses(self) -> None:
        normalized, reasons, _, locality = _normalize_row(
            _base_gold_row(local="Brasilia-DF", cidade="", estado=""),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
            event_locality_owned=True,
        )

        assert reasons == []
        assert locality.issue_code is None
        assert normalized["local"] == "Brasilia-DF"
        assert normalized["cidade"] == ""
        assert normalized["estado"] == ""


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


class TestNormalizeRowEventDateDQ:
    def test_invalid_event_date_still_discards_row_in_pipeline_generico(self) -> None:
        _normalized, reasons, _issue, _locality = _normalize_row(
            _base_gold_row(data_evento="valor-invalido"),
            city_out_of_mapping=False,
            ref_date_utc=date_type(2026, 1, 1),
        )

        assert "DATA_EVENTO_INVALIDA" in reasons


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

    def test_promote_to_gold_parses_cliente_alias_into_is_cliente_bb(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={
                "cliente": "false",
                "is_cliente_bb": "",
            },
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.is_cliente_bb is False

    def test_invalid_event_date_in_sheet_is_ignored_when_batch_is_anchored_on_evento_id(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento.data_inicio_prevista = date_type(2026, 6, 8)
            s.add(evento)
            s.commit()
            s.refresh(evento)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={"data_evento": "planilha-invalida"},
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS
            assert batch.stage == BatchStage.GOLD
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("data_evento_invalid", 0) == 0
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["invalid_records"] == []
            assert "DATA_EVENTO_INVALIDA" not in batch.pipeline_report["gate"]["warnings"]

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.evento_nome == evento.nome

    def test_anchored_batch_persists_lead_city_state_and_uses_event_local_for_sessao_fallback(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento.cidade = "Rio de Janeiro"
            evento.estado = "RJ"
            s.add(evento)
            s.commit()
            s.refresh(evento)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={
                "local": "Londres-UK",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "sessao": "",
            },
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["invalid_records"] == []

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.cidade == "São Paulo"
            assert lead.estado == "SP"
            assert lead.sessao == "Rio de Janeiro-RJ"

    def test_event_without_canonical_date_fails_batch_with_single_contextual_problem(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento.data_inicio_prevista = None
            evento.data_inicio_realizada = None
            s.add(evento)
            s.commit()
            s.refresh(evento)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={"data_evento": "planilha-invalida"},
        )

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        def _unexpected_run_pipeline(*_args, **_kwargs):
            raise AssertionError("run_pipeline nao deve ser chamado quando o Evento nao tem data canonica")

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", _unexpected_run_pipeline)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.FAIL
            assert batch.stage == BatchStage.SILVER
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_discarded_rows == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("data_evento_invalid", 0) == 0
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["gate"]["status"] == "FAIL"
            assert batch.pipeline_report["gate"]["decision"] == "hold"
            assert batch.pipeline_report["gate"]["fail_reasons"] == ["EVENTO_SEM_DATA_CANONICA"]
            assert batch.pipeline_report["gate"]["warnings"] == []
            assert batch.pipeline_report["invalid_records"] == []

    def test_event_model_locality_not_in_reference_still_promotes_with_event_local(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento.cidade = "Brasilia"
            evento.estado = "DF"
            s.add(evento)
            s.commit()
            s.refresh(evento)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={"local": "planilha-espuria", "sessao": ""},
        )

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS
            assert batch.stage == BatchStage.GOLD
            assert batch.gold_dq_invalid_records_total == 0
            assert batch.gold_dq_discarded_rows == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("localidade_invalida", 0) == 0
            assert batch.gold_dq_issue_counts.get("cidade_fora_mapeamento", 0) == 0
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["gate"]["status"] == "PASS"
            assert batch.pipeline_report["gate"]["decision"] == "promote"
            assert "EVENTO_SEM_LOCALIDADE_CANONICA" not in batch.pipeline_report["gate"]["fail_reasons"]
            assert batch.pipeline_report["gate"]["warnings"] == []
            assert batch.pipeline_report["invalid_records"] == []

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.sessao == "Brasilia-DF"

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

    def test_activation_batch_without_event_agencia_persists_fail_with_context(
        self, engine, monkeypatch
    ):
        with Session(engine) as s:
            user = _seed_user(s)
            evento = _seed_evento(s, agencia_id=None)
            ativacao = Ativacao(nome="Stand import", evento_id=evento.id)
            s.add(ativacao)
            s.commit()
            s.refresh(ativacao)
            evento_id = evento.id

            batch = LeadBatch(
                enviado_por=user.id or 0,
                plataforma_origem="email",
                data_envio=datetime(2026, 3, 5, 10, 0, 0, tzinfo=timezone.utc),
                nome_arquivo_original="leads.csv",
                arquivo_bronze=CSV_CONTENT,
                stage=BatchStage.SILVER,
                evento_id=evento.id,
                origem_lote="ativacao",
                ativacao_id=ativacao.id,
                pipeline_status=PipelineStatus.PENDING,
            )
            s.add(batch)
            s.commit()
            s.refresh(batch)
            batch_id = batch.id
            silver = LeadSilver(
                batch_id=batch_id,
                row_index=0,
                evento_id=evento.id,
                dados_brutos=_base_gold_row(),
            )
            s.add(silver)
            s.commit()

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.FAIL
            assert batch.stage == BatchStage.SILVER
            assert batch.pipeline_progress is None
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["gate"]["status"] == "FAIL"
            assert batch.pipeline_report["gate"]["decision"] == "hold"
            assert (
                batch.pipeline_report["failure_context"]["message"]
                == "Falha interna em 'Inserindo leads Gold no banco': "
                f"ValueError: Evento {evento_id} precisa de agencia_id para canonicalizar LeadEvento de ativacao."
            )
            assert batch.pipeline_report["failure_context"]["step"] == "insert_leads"
            assert "precisa de agencia_id" in batch.pipeline_report["gate"]["fail_reasons"][0]

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
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["gate"]["status"] == "FAIL"
            assert batch.pipeline_report["gate"]["decision"] == "hold"
            assert "RuntimeError: pipeline exploded" in batch.pipeline_report["gate"]["fail_reasons"][0]
            assert batch.pipeline_progress is None
            assert batch.gold_dq_discarded_rows == 0
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("cpf_invalid_discarded") == 0
            assert batch.gold_dq_invalid_records_total == 0

        resp = client.get(f"/leads/batches/{batch_id}", headers=auth)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_status"] == "fail"
        assert body["pipeline_report"] is not None
        assert body["pipeline_report"]["gate"]["status"] == "FAIL"
        assert "RuntimeError: pipeline exploded" in body["pipeline_report"]["gate"]["fail_reasons"][0]
        assert body["pipeline_progress"] is None
        assert body["gold_dq_discarded_rows"] == 0
        assert body["gold_dq_issue_counts"]["cpf_invalid_discarded"] == 0
        assert body["gold_dq_invalid_records_total"] == 0

    def test_insert_failure_preserves_pipeline_quality_report_and_adds_failure_context(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        tmp_root = Path("backend/tmp-pytest") / f"insert-fail-{uuid4().hex}"
        report_dir = tmp_root / "output" / str(batch_id)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.json"
        consolidated_path = report_dir / "leads_multieventos_2025.csv"
        summary_path = report_dir / "summary.md"
        report_payload = {
            "lote_id": str(batch_id),
            "run_timestamp": "2026-04-15T18:00:00Z",
            "totals": {"raw_rows": 4, "valid_rows": 3, "discarded_rows": 1},
            "quality_metrics": {
                "cpf_invalid_discarded": 1,
                "telefone_invalid": 0,
                "data_evento_invalid": 0,
                "data_nascimento_invalid": 0,
                "data_nascimento_missing": 0,
                "duplicidades_cpf_evento": 0,
                "cidade_fora_mapeamento": 0,
                "localidade_invalida": 0,
                "localidade_nao_resolvida": 0,
                "localidade_fora_brasil": 0,
                "localidade_cidade_uf_inconsistente": 0,
            },
            "gate": {
                "status": "PASS_WITH_WARNINGS",
                "decision": "promote",
                "fail_reasons": [],
                "warnings": ["CPF_INVALIDO_DESCARTADO"],
            },
            "invalid_records": [],
            "data_nascimento_controle": [],
            "localidade_controle": [],
            "cidade_fora_mapeamento_controle": [],
        }
        report_path.write_text(json.dumps(report_payload), encoding="utf-8")
        consolidated_path.write_text("nome,cpf,email\nAlice,52998224725,alice@ex.com\n", encoding="utf-8")
        summary_path.write_text("# resumo\n", encoding="utf-8")

        def _fake_run_pipeline(*_args, **_kwargs):
            return PipelineResult(
                lote_id=str(batch_id),
                status="PASS_WITH_WARNINGS",
                decision="promote",
                output_dir=report_dir,
                report_path=report_path,
                summary_path=summary_path,
                consolidated_path=consolidated_path,
                exit_code=0,
            )

        def _raise_insert_failure(*_args, **_kwargs):
            raise RuntimeError("insert exploded")

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", _fake_run_pipeline)
        monkeypatch.setattr(lead_pipeline_service, "_inserir_leads_gold", _raise_insert_failure)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.FAIL
            assert batch.stage == BatchStage.SILVER
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["totals"] == report_payload["totals"]
            assert batch.pipeline_report["gate"]["status"] == "FAIL"
            assert batch.pipeline_report["gate"]["decision"] == "hold"
            assert batch.pipeline_report["gate"]["warnings"] == ["CPF_INVALIDO_DESCARTADO"]
            assert "RuntimeError: insert exploded" in batch.pipeline_report["gate"]["fail_reasons"][0]
            assert batch.pipeline_report["failure_context"]["step"] == "insert_leads"
            assert batch.gold_dq_discarded_rows == 1
            assert batch.gold_dq_issue_counts is not None
            assert batch.gold_dq_issue_counts.get("cpf_invalid_discarded") == 1
            assert batch.gold_dq_invalid_records_total == 0

    def test_missing_consolidated_csv_marks_batch_as_failed(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(engine, batch_id, evento.id)

        import app.db.database as database_module
        import app.services.lead_pipeline_service as lead_pipeline_service

        monkeypatch.setattr(database_module, "engine", engine)

        tmp_root = Path("backend/tmp-pytest") / f"insert-missing-{uuid4().hex}"
        report_dir = tmp_root / "output" / str(batch_id)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.json"
        consolidated_path = report_dir / "missing-consolidated.csv"
        summary_path = report_dir / "summary.md"
        report_payload = {
            "lote_id": str(batch_id),
            "run_timestamp": "2026-04-15T18:00:00Z",
            "totals": {"raw_rows": 4, "valid_rows": 3, "discarded_rows": 1},
            "quality_metrics": {
                "cpf_invalid_discarded": 1,
                "telefone_invalid": 0,
                "data_evento_invalid": 0,
                "data_nascimento_invalid": 0,
                "data_nascimento_missing": 0,
                "duplicidades_cpf_evento": 0,
                "cidade_fora_mapeamento": 0,
                "localidade_invalida": 0,
                "localidade_nao_resolvida": 0,
                "localidade_fora_brasil": 0,
                "localidade_cidade_uf_inconsistente": 0,
            },
            "gate": {
                "status": "PASS",
                "decision": "promote",
                "fail_reasons": [],
                "warnings": [],
            },
            "invalid_records": [],
            "data_nascimento_controle": [],
            "localidade_controle": [],
            "cidade_fora_mapeamento_controle": [],
        }
        report_path.write_text(json.dumps(report_payload), encoding="utf-8")
        summary_path.write_text("# resumo\n", encoding="utf-8")

        def _fake_run_pipeline(*_args, **_kwargs):
            return PipelineResult(
                lote_id=str(batch_id),
                status="PASS",
                decision="promote",
                output_dir=report_dir,
                report_path=report_path,
                summary_path=summary_path,
                consolidated_path=consolidated_path,
                exit_code=0,
            )

        monkeypatch.setattr(lead_pipeline_service, "run_pipeline", _fake_run_pipeline)

        asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.FAIL
            assert batch.stage == BatchStage.SILVER
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["gate"]["status"] == "FAIL"
            assert batch.pipeline_report["gate"]["decision"] == "hold"
            assert "FileNotFoundError" in batch.pipeline_report["gate"]["fail_reasons"][0]
            assert batch.pipeline_report["failure_context"]["step"] == "insert_leads"

    def test_missing_birth_date_keeps_lead_and_records_dq(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth)
        _promote_to_silver(
            engine,
            batch_id,
            evento.id,
            dados_brutos_extra={
                "data_nascimento": "   ",
                "source_file": "leads.xlsx",
                "source_sheet": "Participantes",
                "source_row": 1514,
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
            assert batch.gold_dq_issue_counts.get("data_nascimento_missing") == 1
            assert batch.gold_dq_issue_counts.get("data_nascimento_invalid") == 0
            assert batch.pipeline_report is not None
            assert batch.pipeline_report["invalid_records"] == []
            assert batch.pipeline_report["gate"]["warnings"] == ["DATA_NASCIMENTO_AUSENTE"]
            controle = batch.pipeline_report["data_nascimento_controle"]
            assert len(controle) == 1
            assert controle[0]["source_file"] == "leads.xlsx"
            assert controle[0]["source_sheet"] == "Participantes"
            assert controle[0]["source_row"] == 1514
            assert controle[0]["issue"] == "missing"

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.data_nascimento is None

    def test_missing_birth_date_dq_reports_physical_line_after_blank_csv_row(
        self, client, engine, monkeypatch
    ):
        """Linha em branco após o cabeçalho: source_row no relatório Gold = linha física no CSV."""
        from app.models.lead_batch import LeadSilver

        csv_blank = (
            b"nome,cpf,email,telefone,data_nascimento\n"
            b"\n"
            b"Alice,52998224725,alice@ex.com,11999990000,   \n"
        )
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        batch_id = _upload_batch(client, auth, file_content=csv_blank)
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
                    "data_nascimento": "data_nascimento",
                },
            },
        )
        assert resp.status_code == 200, resp.text

        with Session(engine) as s:
            silver = s.exec(select(LeadSilver).where(LeadSilver.batch_id == batch_id)).first()
            assert silver is not None
            assert silver.dados_brutos.get("source_row") == 3
            assert silver.dados_brutos.get("source_row_original") == 3

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        asyncio.run(executar_pipeline_gold(batch_id))

        with Session(engine) as s:
            batch = s.get(LeadBatch, batch_id)
            assert batch is not None
            assert batch.pipeline_status == PipelineStatus.PASS_WITH_WARNINGS
            assert batch.pipeline_report is not None
            controle = batch.pipeline_report["data_nascimento_controle"]
            assert len(controle) == 1
            assert controle[0]["source_file"] == "leads.csv"
            assert controle[0]["source_sheet"] == ""
            assert controle[0]["source_row"] == 3
            assert controle[0]["issue"] == "missing"

    def test_anchored_batch_keeps_lead_locality_dq_without_blaming_event_local(self, client, engine, monkeypatch):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)
            evento.cidade = "Rio de Janeiro"
            evento.estado = "RJ"
            s.add(evento)
            s.commit()
            s.refresh(evento)

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
            assert controle[0]["source_file"] == "leads.csv"
            assert controle[0]["source_sheet"] == ""
            assert controle[0]["source_row"] == 2
            assert controle[0]["issue"] == "cidade_uf_mismatch"
            assert controle[0]["raw_cidade"] == "Sao Paulo"
            assert controle[0]["raw_estado"] == "RJ"
            assert controle[0]["raw_local"] == ""

            lead = s.exec(select(Lead).where(Lead.batch_id == batch_id)).first()
            assert lead is not None
            assert lead.cidade is None
            assert lead.estado is None
            assert lead.sessao == "Rio de Janeiro-RJ"

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
            assert controle[0]["source_file"] == "leads.csv"
            assert controle[0]["source_sheet"] == ""
            assert controle[0]["source_row"] == 2
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

    def test_anchored_batch_reimport_matches_existing_lead_by_evento_id_after_event_rename(
        self, client, engine, monkeypatch
    ):
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        first_batch_id = _upload_batch(client, auth, evento_id=evento.id)
        _promote_to_silver(engine, first_batch_id, evento.id)
        asyncio.run(executar_pipeline_gold(first_batch_id))

        with Session(engine) as s:
            existing = s.exec(select(Lead).where(Lead.email == "alice@ex.com")).first()
            assert existing is not None
            existing_id = existing.id
            persisted_evento = s.get(Evento, evento.id)
            assert persisted_evento is not None
            persisted_evento.nome = "Park Challenge 2025 Renomeado"
            s.add(persisted_evento)
            s.commit()

        second_batch_id = _upload_batch(client, auth, evento_id=evento.id)
        _promote_to_silver(engine, second_batch_id, evento.id)
        asyncio.run(executar_pipeline_gold(second_batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.email == "alice@ex.com")).all()
            assert len(leads) == 1
            assert leads[0].id == existing_id

            lead_eventos = s.exec(
                select(LeadEvento)
                .where(LeadEvento.lead_id == existing_id)
                .where(LeadEvento.evento_id == evento.id)
            ).all()
            assert len(lead_eventos) == 1

    def test_anchored_batch_reimport_preserves_existing_filled_fields(
        self, client, engine, monkeypatch
    ) -> None:
        with Session(engine) as s:
            auth = _auth_header(client, s)
            evento = _seed_evento(s)

        import app.db.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        from app.services.lead_pipeline_service import executar_pipeline_gold

        first_batch_id = _upload_batch(client, auth, evento_id=evento.id)
        _promote_to_silver(
            engine,
            first_batch_id,
            evento.id,
            dados_brutos_extra={"nome": "Alice Original"},
        )
        asyncio.run(executar_pipeline_gold(first_batch_id))

        with Session(engine) as s:
            existing = s.exec(select(Lead).where(Lead.email == "alice@ex.com")).first()
            assert existing is not None
            existing_id = existing.id
            assert existing.nome == "Alice Original"

        second_batch_id = _upload_batch(client, auth, evento_id=evento.id)
        _promote_to_silver(
            engine,
            second_batch_id,
            evento.id,
            dados_brutos_extra={"nome": "Alice Corrigida"},
        )
        asyncio.run(executar_pipeline_gold(second_batch_id))

        with Session(engine) as s:
            leads = s.exec(select(Lead).where(Lead.email == "alice@ex.com")).all()
            assert len(leads) == 1
            assert leads[0].id == existing_id
            assert leads[0].nome == "Alice Original"

            lead_eventos = s.exec(
                select(LeadEvento)
                .where(LeadEvento.lead_id == existing_id)
                .where(LeadEvento.evento_id == evento.id)
            ).all()
            assert len(lead_eventos) == 1

    def test_find_existing_lead_anchored_batch_ignores_homonymous_lead_from_other_event(
        self, engine
    ) -> None:
        with Session(engine) as s:
            evento = _seed_evento(s)
            outro_evento = _seed_evento(s)
            outro_evento.nome = evento.nome
            s.add(outro_evento)
            s.commit()
            s.refresh(outro_evento)

            lead = Lead(
                email="homonimo-classico@example.com",
                cpf="52998224725",
                nome="Lead Homonimo",
                evento_nome=evento.nome,
                sessao="Sao Paulo-SP",
            )
            s.add(lead)
            s.commit()
            s.refresh(lead)
            s.add(
                LeadEvento(
                    lead_id=lead.id,
                    evento_id=outro_evento.id,
                    source_kind=LeadEventoSourceKind.LEAD_BATCH,
                )
            )
            s.commit()

            from app.services.lead_pipeline_service import _find_existing_lead

            payload = {
                "email": "homonimo-classico@example.com",
                "cpf": "52998224725",
                "evento_nome": evento.nome,
                "sessao": "Sao Paulo-SP",
            }

            assert _find_existing_lead(s, payload, anchored_evento_id=evento.id) is None

            matched = _find_existing_lead(s, payload, anchored_evento_id=outro_evento.id)
            assert matched is not None
            assert matched.id == lead.id


def test_executar_pipeline_gold_enrichment_only_updates_existing_leads_by_cpf(
    client, engine, monkeypatch
):
    with Session(engine) as s:
        auth = _auth_header(client, s)

    batch_id = _upload_batch(client, auth, enrichment_only=True)

    with Session(engine) as s:
        batch = s.get(LeadBatch, batch_id)
        assert batch is not None
        batch.stage = BatchStage.SILVER
        batch.evento_id = None
        s.add(batch)

        matched_lead = Lead(
            cpf="52998224725",
            email="existing-match@example.com",
            nome=None,
            telefone=None,
            data_nascimento=date_type(1991, 1, 1),
            is_cliente_bb=False,
        )
        ambiguous_lead_a = Lead(
            cpf="39053344705",
            email="ambiguous-a@example.com",
            nome="Ambiguous A",
        )
        ambiguous_lead_b = Lead(
            cpf="39053344705",
            email="ambiguous-b@example.com",
            nome="Ambiguous B",
        )
        s.add(matched_lead)
        s.add(ambiguous_lead_a)
        s.add(ambiguous_lead_b)
        s.commit()

        rows = [
            {
                "row_index": 0,
                "dados_brutos": {
                    "cpf": "529.982.247-25",
                    "nome": "Alice Enrichment",
                    "email": "incoming@example.com",
                    "telefone": "11999990000",
                    "data_nascimento": "1980-02-03 00:00:00",
                    "is_cliente_bb": "true",
                },
            },
            {
                "row_index": 1,
                "dados_brutos": {
                    "cpf": "",
                    "nome": "Sem CPF",
                },
            },
            {
                "row_index": 2,
                "dados_brutos": {
                    "cpf": "12345678909",
                    "nome": "CPF Invalido",
                },
            },
            {
                "row_index": 3,
                "dados_brutos": {
                    "cpf": "11144477735",
                    "nome": "Nao Encontrado",
                },
            },
            {
                "row_index": 4,
                "dados_brutos": {
                    "cpf": "39053344705",
                    "nome": "Ambiguo",
                },
            },
        ]
        for row in rows:
            s.add(
                LeadSilver(
                    batch_id=batch_id,
                    row_index=row["row_index"],
                    evento_id=None,
                    dados_brutos=row["dados_brutos"],
                )
            )
        s.commit()

    import app.db.database as database_module
    import app.services.lead_pipeline_service as lead_pipeline_service

    monkeypatch.setattr(database_module, "engine", engine)

    def _unexpected_run_pipeline(*_args, **_kwargs):
        raise AssertionError("run_pipeline nao deve ser chamado em enrichment_only")

    monkeypatch.setattr(lead_pipeline_service, "run_pipeline", _unexpected_run_pipeline)

    asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

    with Session(engine) as s:
        batch = s.get(LeadBatch, batch_id)
        assert batch is not None
        assert batch.stage == BatchStage.GOLD
        assert batch.pipeline_status == PipelineStatus.PASS_WITH_WARNINGS
        assert batch.gold_dq_discarded_rows == 4
        assert batch.gold_dq_invalid_records_total == 4
        assert batch.gold_dq_issue_counts is not None
        assert batch.gold_dq_issue_counts.get("cpf_missing_rows") == 1
        assert batch.gold_dq_issue_counts.get("cpf_invalid_rows") == 1
        assert batch.gold_dq_issue_counts.get("lead_not_found_rows") == 1
        assert batch.gold_dq_issue_counts.get("ambiguous_match_rows") == 1
        assert batch.pipeline_report is not None
        assert batch.pipeline_report["gate"]["status"] == "PASS_WITH_WARNINGS"
        assert batch.pipeline_report["gate"]["decision"] == "promote"
        assert batch.pipeline_report["enrichment"] == {
            "mode": "enrichment_only",
            "lookup_key": "cpf",
            "merge_policy": "fill_missing_with_truth_source_overrides",
            "truth_source_fields": ["data_nascimento", "is_cliente_bb", "is_cliente_estilo"],
            "matched_rows": 1,
            "updated_rows": 1,
            "not_found_rows": 1,
            "ambiguous_rows": 1,
            "cpf_missing_rows": 1,
            "cpf_invalid_rows": 1,
            "rejection_samples": batch.pipeline_report["enrichment"]["rejection_samples"],
        }
        assert {item["reason"] for item in batch.pipeline_report["invalid_records"]} == {
            "cpf_missing",
            "cpf_invalid",
            "lead_not_found",
            "ambiguous_match",
        }

        leads = s.exec(select(Lead).order_by(Lead.id)).all()
        assert len(leads) == 3

        matched = s.exec(select(Lead).where(Lead.cpf == "52998224725")).one()
        assert matched.nome == "Alice Enrichment"
        assert matched.telefone == "11999990000"
        assert matched.email == "existing-match@example.com"
        assert matched.data_nascimento == date_type(1980, 2, 3)
        assert matched.is_cliente_bb is True

        assert s.exec(select(LeadEvento)).all() == []


def test_executar_pipeline_gold_enrichment_only_accepts_cliente_boolean_alias(
    client, engine, monkeypatch
):
    with Session(engine) as s:
        auth = _auth_header(client, s)

    batch_id = _upload_batch(client, auth, enrichment_only=True)

    with Session(engine) as s:
        batch = s.get(LeadBatch, batch_id)
        assert batch is not None
        batch.stage = BatchStage.SILVER
        batch.evento_id = None
        s.add(batch)

        matched_lead = Lead(
            cpf="52998224725",
            email="existing-cliente@example.com",
            nome="Lead Cliente",
            is_cliente_bb=None,
        )
        s.add(matched_lead)
        s.commit()

        s.add(
            LeadSilver(
                batch_id=batch_id,
                row_index=0,
                evento_id=None,
                dados_brutos={
                    "cpf": "529.982.247-25",
                    "cliente": "true",
                },
            )
        )
        s.commit()

    import app.db.database as database_module
    import app.services.lead_pipeline_service as lead_pipeline_service

    monkeypatch.setattr(database_module, "engine", engine)
    asyncio.run(lead_pipeline_service.executar_pipeline_gold(batch_id))

    with Session(engine) as s:
        matched = s.exec(select(Lead).where(Lead.cpf == "52998224725")).one()
        assert matched.is_cliente_bb is True
