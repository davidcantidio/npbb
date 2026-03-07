from pathlib import Path
import re
from datetime import date, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.models import Lead
from core.leads_etl.models import LEAD_ROW_EXCLUDED_FIELDS, LEAD_ROW_FIELDS, coerce_lead_field
from core.leads_etl.models._field_catalog import LEGACY_COERCION_FIELDS


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_lead_dedupe_por_evento_e_sessao():
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        lead1 = Lead(
            nome="Joao",
            sobrenome="Silva",
            cpf="12345678900",
            email="joao@example.com",
            data_nascimento=date(1990, 1, 1),
            evento_nome="Evento A",
            sessao="Sessao 1",
        )
        session.add(lead1)
        session.commit()

        lead2 = Lead(
            nome="Maria",
            sobrenome="Souza",
            cpf="12345678900",
            email="joao@example.com",
            data_nascimento=date(1991, 2, 2),
            evento_nome="Evento B",
            sessao="Sessao 1",
        )
        session.add(lead2)
        session.commit()

        lead3 = Lead(
            nome="Joao",
            sobrenome="Silva",
            cpf="12345678900",
            email="joao@example.com",
            data_nascimento=date(1990, 1, 1),
            evento_nome="Evento A",
            sessao="Sessao 1",
        )
        session.add(lead3)
        with pytest.raises(IntegrityError):
            session.commit()


def test_lead_campos_cliente_bb_e_estilo_sao_opcionais() -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        lead_default = Lead(nome="Lead Sem Cruzamento")
        lead_enriquecido = Lead(
            nome="Lead Enriquecido",
            is_cliente_bb=True,
            is_cliente_estilo=False,
        )

        session.add_all([lead_default, lead_enriquecido])
        session.commit()
        session.refresh(lead_default)
        session.refresh(lead_enriquecido)

        assert lead_default.is_cliente_bb is None
        assert lead_default.is_cliente_estilo is None
        assert lead_enriquecido.is_cliente_bb is True
        assert lead_enriquecido.is_cliente_estilo is False


def test_lead_row_catalog_cobre_campos_importaveis_do_modelo_lead() -> None:
    lead_fields = set(Lead.model_fields)
    canonical_fields = set(LEAD_ROW_FIELDS)
    excluded_fields = set(LEAD_ROW_EXCLUDED_FIELDS)

    assert lead_fields == canonical_fields | excluded_fields
    assert excluded_fields == {"id", "data_criacao", "data_compra_data", "data_compra_hora", "batch_id"}
    assert all(reason.strip() for reason in LEAD_ROW_EXCLUDED_FIELDS.values())


def test_lead_row_catalog_cobre_campos_expostos_na_ui_de_importacao() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    ui_path = repo_root / "frontend/src/pages/leads/ImportacaoPage.tsx"
    text = ui_path.read_text(encoding="utf-8-sig")
    ui_fields = {
        value
        for value in re.findall(r'value: "([^"]+)"', text)
        if value
    }

    assert ui_fields <= set(LEAD_ROW_FIELDS)


def test_coercao_canonica_cobre_campos_legados_de_importacao() -> None:
    assert set(LEGACY_COERCION_FIELDS) <= set(LEAD_ROW_FIELDS)

    samples = {
        "email": (" Pessoa@Example.COM ", "pessoa@example.com"),
        "cpf": ("123.456.789-00", "12345678900"),
        "telefone": ("+55 (11) 91234-5678", "5511912345678"),
        "cep": ("70.000-123", "70000123"),
        "data_nascimento": ("31/12/1999", date(1999, 12, 31)),
        "data_compra": ("2025-01-02 10:30", datetime(2025, 1, 2, 10, 30)),
        "ingresso_qtd": ("02", 2),
        "opt_in_flag": ("sim", True),
        "estado": (" sp ", "SP"),
        "nome": ("  Alice  ", "Alice"),
    }

    for field, (sample, expected) in samples.items():
        assert coerce_lead_field(field, sample) == expected


def test_helper_legado_foi_removido() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    helper_path = repo_root / "backend/app/utils/lead_import_normalize.py"
    assert not helper_path.exists()


def test_router_leads_consume_coercao_direta_do_core() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    router_path = repo_root / "backend/app/routers/leads.py"
    text = router_path.read_text(encoding="utf-8")

    assert "from core.leads_etl.models import coerce_lead_field" in text
    assert "lead_import_normalize" not in text
