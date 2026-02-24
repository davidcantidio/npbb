"""Tests for XLSX utils/extractors using repository fixture files."""

from __future__ import annotations

from pathlib import Path
import sys

from openpyxl import load_workbook
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from etl.extract import xlsx_leads, xlsx_optin
from etl.extract.xlsx_utils import build_columns_with_metadata, find_header_row


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source  # noqa: E402
from app.models.stg_leads import StgLead, StgLeadAction  # noqa: E402
from app.models.stg_optin import StgOptinTransaction  # noqa: E402


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "xlsx"
OPTIN_FIXTURE = FIXTURES_DIR / "optin_min.xlsx"
LEADS_FIXTURE = FIXTURES_DIR / "leads_min.xlsx"


def _make_engine():
    """Create isolated in-memory SQLite engine for extractor tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry, lineage and staging tables required by loaders."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            StgOptinTransaction.__table__,
            StgLead.__table__,
            StgLeadAction.__table__,
        ],
    )


def test_xlsx_utils_detect_header_and_build_columns_with_lineage() -> None:
    """Header utilities should normalize merged headers and return lineage metadata."""
    wb = load_workbook(OPTIN_FIXTURE, data_only=True)
    ws = wb["OptIn"]

    header_row = find_header_row(ws, required_terms=["CPF", "Opt In"], max_scan_rows=20)
    assert header_row == 4

    result = build_columns_with_metadata(
        ws,
        header_row=header_row,
        header_depth=2,
        aliases={
            "cliente_nome": "nome",
            "cliente_cpf": "cpf",
            "cliente_email": "email",
            "venda_data_compra": "dt_hr_compra",
            "venda_opt_in": "opt_in",
            "venda_opt_in_id": "opt_in_id",
            "venda_evento": "evento",
            "venda_sessao": "sessao",
            "venda_qtd_ingresso": "qtd_ingresso",
        },
    )

    assert result.columns == [
        "nome",
        "cpf",
        "email",
        "dt_hr_compra",
        "opt_in",
        "opt_in_id",
        "evento",
        "sessao",
        "qtd_ingresso",
    ]
    assert result.lineage.sheet_name == "OptIn"
    assert result.lineage.header_row == 4
    assert result.lineage.header_range == "A4:I5"
    assert result.lineage.used_range == "A4:I6"


def test_extract_optin_from_fixture_includes_lineage_metadata() -> None:
    """Opt-in extractor should parse one fixture row with canonical fields."""
    rows = list(
        xlsx_optin.extract_optin_xlsx(
            OPTIN_FIXTURE,
            aliases={
                "venda_evento": "evento",
                "venda_sessao": "sessao",
            },
        )
    )
    assert len(rows) == 1

    row = rows[0]
    assert row["evento"] == "Tamo Junto"
    assert row["sessao"] == "Show 12/12"
    assert row["opt_in"] == "Sim"
    assert row["qtd_ingresso"] == 2
    assert row["cpf_hash"]
    assert row["email_hash"]
    assert row["__sheet_name"] == "OptIn"
    assert row["__header_row"] == 4
    assert row["__header_range"] == "A4:I5"
    assert row["__source_range"] == "A6:I6"


def test_extract_leads_from_fixture_includes_actions_and_lineage() -> None:
    """Leads extractor should parse actions and emit lineage metadata keys."""
    rows = list(xlsx_leads.extract_leads_xlsx(LEADS_FIXTURE))
    assert len(rows) == 2

    first = rows[0]
    assert first["evento"] == "Festival"
    assert first["estado"] == "SP"
    assert first["acoes_list"] == ["Ativacao QR", "Pesquisa", "Cupom"]
    assert first["person_key_hash"]
    assert first["__sheet_name"] == "Leads"
    assert first["__header_row"] == 4
    assert first["__header_range"] == "A4:N5"
    assert first["__source_range"] == "A6:N6"


def test_optin_loader_fails_when_required_lineage_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Required policy should fail opt-in load when lineage ID is absent."""
    engine = _make_engine()
    _create_tables(engine)
    monkeypatch.setattr(xlsx_optin, "engine", engine)

    class _DummyLineageRef:
        id = 0

    monkeypatch.setattr(xlsx_optin, "create_lineage_ref", lambda *args, **kwargs: _DummyLineageRef())

    with pytest.raises(ValueError, match="exige linhagem"):
        xlsx_optin.load_optin_xlsx_to_staging(
            source_id="SRC_OPTIN_REQUIRED_LINEAGE",
            xlsx_path=OPTIN_FIXTURE,
            lineage_policy="required",
            severity_on_missing="failed",
        )

    with Session(engine) as session:
        runs = session.exec(select(IngestionRun).order_by(IngestionRun.id.desc())).all()
        assert runs
        assert runs[0].status == IngestionStatus.FAILED


def test_leads_loader_fails_when_required_lineage_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Required policy should fail leads load when lineage ID is absent."""
    engine = _make_engine()
    _create_tables(engine)
    monkeypatch.setattr(xlsx_leads, "engine", engine)

    class _DummyLineageRef:
        id = 0

    monkeypatch.setattr(xlsx_leads, "create_lineage_ref", lambda *args, **kwargs: _DummyLineageRef())

    with pytest.raises(ValueError, match="exige linhagem"):
        xlsx_leads.load_leads_xlsx_to_staging(
            source_id="SRC_LEADS_REQUIRED_LINEAGE",
            xlsx_path=LEADS_FIXTURE,
            lineage_policy="required",
            severity_on_missing="failed",
        )

    with Session(engine) as session:
        runs = session.exec(select(IngestionRun).order_by(IngestionRun.id.desc())).all()
        assert runs
        assert runs[0].status == IngestionStatus.FAILED
