"""Unit tests for ETL data-quality framework primitives."""

from __future__ import annotations

from pathlib import Path
import sys

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from etl.validate.checks_duplicates import DuplicateCheck, DuplicateCheckSpec
from etl.validate.checks_not_null import NotNullCheck
from etl.validate.checks_schema import DatasetCheckConfig, SchemaCheck
from etl.validate.framework import (
    Check,
    CheckContext,
    CheckResult,
    CheckRunner,
    CheckStatus,
    Severity,
    parse_fail_on,
    render_report_json,
    render_report_markdown,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.dq_results import DQCheckResult  # noqa: E402
from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402


class _PassCheck(Check):
    check_id = "test.pass"
    description = "Always pass"

    def run(self, context: CheckContext) -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="ok",
            ingestion_id=context.ingestion_id,
        )


class _WarningFailCheck(Check):
    check_id = "test.warning_fail"
    description = "Always warning fail"

    def run(self, context: CheckContext) -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message="warn fail",
            ingestion_id=context.ingestion_id,
            evidence={"hint": "action"},
        )


class _CrashCheck(Check):
    check_id = "test.crash"
    description = "Raises exception"

    def run(self, context: CheckContext) -> CheckResult:
        raise RuntimeError("boom")


class _PersistentWarningCheck(Check):
    """Return a deterministic warning-fail result with lineage payload."""

    check_id = "test.persist_warning"
    description = "Always warning fail with lineage metadata"

    def __init__(self, *, lineage_ref_id: int, source_id: str) -> None:
        """Initialize deterministic payload for persistence assertions.

        Args:
            lineage_ref_id: Lineage reference id to be persisted.
            source_id: Source identifier attached to lineage payload.
        """

        self._lineage_ref_id = lineage_ref_id
        self._source_id = source_id

    def run(self, context: CheckContext) -> CheckResult:
        """Return one warning failure with explicit evidence and lineage."""

        return CheckResult(
            check_id=self.check_id,
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message="persist this finding",
            ingestion_id=context.ingestion_id,
            evidence={"dataset": "optin"},
            lineage={
                "source_id": self._source_id,
                "lineage_ref_id": self._lineage_ref_id,
            },
        )


def _make_engine():
    """Create isolated in-memory SQLite engine for persistence tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_tables(engine) -> None:  # noqa: ANN001
    """Create minimum registry/lineage/DQ result tables for framework tests."""

    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            DQCheckResult.__table__,
        ],
    )


def _seed_registry_lineage(session: Session) -> tuple[int, str, int]:
    """Insert source, ingestion and lineage reference for persistence flow.

    Args:
        session: Active SQLModel session.

    Returns:
        Tuple with `ingestion_id`, `source_id`, and `lineage_ref_id`.
    """

    source = Source(source_id="SRC_DQ_PERSIST", kind=SourceKind.XLSX, uri="file:///tmp/optin.xlsx")
    session.add(source)
    session.commit()
    session.refresh(source)

    run = IngestionRun(
        source_pk=int(source.id),
        status=IngestionStatus.SUCCESS,
        extractor_name="extract_xlsx_optin",
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    lineage = LineageRef(
        source_id=source.source_id,
        ingestion_id=int(run.id),
        location_type=LineageLocationType.SHEET,
        location_value="sheet:01.1 - Opt-In",
        evidence_text="Tabela principal",
    )
    session.add(lineage)
    session.commit()
    session.refresh(lineage)

    return int(run.id), source.source_id, int(lineage.id)


def _create_dq_target_table(engine) -> sa.Table:  # noqa: ANN001
    """Create one synthetic dataset table for framework integration checks.

    Args:
        engine: SQLAlchemy engine used by tests.

    Returns:
        Reflected SQLAlchemy table object.
    """

    metadata = sa.MetaData()
    table = sa.Table(
        "stg_dq_runner_target",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("cpf_hash", sa.String(64), nullable=True),
        sa.Column("evento", sa.String(200), nullable=True),
        sa.Column("sessao", sa.String(200), nullable=True),
        sa.Column("metric_value", sa.Integer(), nullable=True),
    )
    metadata.create_all(engine)
    return table


def _seed_dq_target_rows(
    engine,  # noqa: ANN001
    *,
    ingestion_id: int,
    source_id: str,
    lineage_ref_id: int,
) -> None:
    """Insert deterministic rows with duplicate key and critical NULL sample.

    Args:
        engine: SQLAlchemy engine used by tests.
        ingestion_id: Ingestion id to scope the check run.
        source_id: Source id used for lineage hints.
        lineage_ref_id: Lineage id used for lineage hints.
    """

    table = sa.Table("stg_dq_runner_target", sa.MetaData(), autoload_with=engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": ingestion_id,
                    "source_id": source_id,
                    "lineage_ref_id": lineage_ref_id,
                    "cpf_hash": "CPF_DUP",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 13/12",
                    "metric_value": 10,
                },
                {
                    "id": 2,
                    "ingestion_id": ingestion_id,
                    "source_id": source_id,
                    "lineage_ref_id": lineage_ref_id,
                    "cpf_hash": "CPF_DUP",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 13/12",
                    "metric_value": None,
                },
                {
                    "id": 3,
                    "ingestion_id": ingestion_id,
                    "source_id": source_id,
                    "lineage_ref_id": lineage_ref_id,
                    "cpf_hash": "CPF_OK",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 14/12",
                    "metric_value": 7,
                },
            ],
        )


def _build_basic_dq_checks_config() -> DatasetCheckConfig:
    """Build one dataset config used by schema/not-null/duplicate checks.

    Returns:
        Dataset check config with required, null-critical and duplicate keys.
    """

    return DatasetCheckConfig(
        dataset_id="runner_target",
        table="stg_dq_runner_target",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=(
            "ingestion_id",
            "source_id",
            "lineage_ref_id",
            "cpf_hash",
            "evento",
            "sessao",
            "metric_value",
        ),
        critical_not_null_columns=("ingestion_id", "source_id", "lineage_ref_id", "metric_value"),
        duplicate_key_sets=(("cpf_hash", "evento", "sessao"),),
    )


def test_check_runner_exit_code_respects_fail_on_threshold() -> None:
    """Runner should fail only when failing result reaches configured threshold."""

    context = CheckContext(ingestion_id=99)
    checks = (_PassCheck(), _WarningFailCheck())

    report_error = CheckRunner(checks, fail_on=Severity.ERROR).run(context)
    report_warning = CheckRunner(checks, fail_on=Severity.WARNING).run(context)

    assert report_error.exit_code == 0
    assert report_warning.exit_code == 1
    assert report_warning.summary["total"] == 2
    assert report_warning.summary["pass"] == 1
    assert report_warning.summary["fail"] == 1
    assert report_warning.summary["warning"] == 1


def test_runner_captures_unexpected_exceptions_as_error_finding() -> None:
    """Unhandled check exceptions should become actionable error results."""

    context = CheckContext(ingestion_id=55)
    report = CheckRunner((_CrashCheck(),), fail_on=Severity.ERROR).run(context)

    assert report.exit_code == 1
    assert len(report.results) == 1
    result = report.results[0]
    assert result.check_id == "test.crash"
    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["exception_type"] == "RuntimeError"


def test_framework_renderers_and_fail_on_parser_generate_expected_output() -> None:
    """JSON/Markdown renderers and fail-on parser should be deterministic."""

    report = CheckRunner((_PassCheck(),), fail_on=parse_fail_on("none")).run(CheckContext(ingestion_id=7))
    json_output = render_report_json(report)
    md_output = render_report_markdown(report)

    assert report.exit_code == 0
    assert '"check_id": "test.pass"' in json_output
    assert "| test.pass | pass | info |" in md_output
    assert parse_fail_on("info") == Severity.INFO
    assert parse_fail_on("none") is None


def test_check_runner_persists_results_without_duplicate_rows_for_same_ingestion() -> None:
    """Runner should persist results and replace prior rows for same ingestion."""

    engine = _make_engine()
    _create_tables(engine)

    with Session(engine) as session:
        ingestion_id, source_id, lineage_ref_id = _seed_registry_lineage(session)
        context = CheckContext(ingestion_id=ingestion_id, resources={"session": session})
        check = _PersistentWarningCheck(lineage_ref_id=lineage_ref_id, source_id=source_id)
        runner = CheckRunner(
            (check,),
            fail_on=Severity.ERROR,
            persist_results=True,
            replace_existing_results=True,
        )

        first_report = runner.run(context)
        second_report = runner.run(context)

        rows = session.exec(
            select(DQCheckResult).where(DQCheckResult.ingestion_id == ingestion_id)
        ).all()
        assert first_report.exit_code == 0
        assert second_report.exit_code == 0
        assert context.metadata["dq_persisted_count"] == 1
        assert len(rows) == 1
        persisted = rows[0]
        assert persisted.source_id == source_id
        assert persisted.lineage_ref_id == lineage_ref_id
        assert persisted.check_id == "test.persist_warning"
        assert persisted.status.value == CheckStatus.FAIL.value
        assert persisted.severity.value == Severity.WARNING.value


def test_check_runner_reports_error_when_persistence_is_enabled_without_session_resource() -> None:
    """Runner should emit actionable error result when persistence lacks session."""

    report = CheckRunner(
        (_PassCheck(),),
        persist_results=True,
        fail_on=Severity.ERROR,
    ).run(CheckContext(ingestion_id=10))

    by_id = {result.check_id: result for result in report.results}
    assert report.exit_code == 1
    assert "dq.persist_results" in by_id
    assert by_id["dq.persist_results"].status == CheckStatus.FAIL
    assert by_id["dq.persist_results"].severity == Severity.ERROR


def test_runner_executes_basic_checks_and_aggregates_by_severity() -> None:
    """Runner should execute schema/not-null/duplicate checks and aggregate summary."""

    engine = _make_engine()
    _create_tables(engine)

    with Session(engine) as session:
        ingestion_id, source_id, lineage_ref_id = _seed_registry_lineage(session)

    _create_dq_target_table(engine)
    _seed_dq_target_rows(
        engine,
        ingestion_id=ingestion_id,
        source_id=source_id,
        lineage_ref_id=lineage_ref_id,
    )

    config = _build_basic_dq_checks_config()
    checks = (
        SchemaCheck(config),
        NotNullCheck(config),
        DuplicateCheck(
            DuplicateCheckSpec(
                dataset_config=config,
                key_columns=("cpf_hash", "evento", "sessao"),
            ),
            sample_limit=3,
        ),
    )

    with Session(engine) as session:
        context = CheckContext(ingestion_id=ingestion_id, resources={"session": session})
        report = CheckRunner(checks, fail_on=Severity.ERROR).run(context)

    by_id = {result.check_id: result for result in report.results}
    assert report.exit_code == 1
    assert report.summary["total"] == 3
    assert report.summary["pass"] == 1
    assert report.summary["fail"] == 2
    assert report.summary["error"] == 2
    assert by_id["dq.schema.runner_target"].status == CheckStatus.PASS
    assert by_id["dq.not_null.runner_target"].status == CheckStatus.FAIL
    assert by_id["dq.duplicates.runner_target.cpf_hash_evento_sessao"].status == CheckStatus.FAIL
    for result in report.results:
        assert isinstance(result.message, str)
        assert result.message.strip()


def test_runner_persists_basic_check_results_when_enabled() -> None:
    """Runner should persist schema/not-null/duplicate outcomes into dq_check_result."""

    engine = _make_engine()
    _create_tables(engine)

    with Session(engine) as session:
        ingestion_id, source_id, lineage_ref_id = _seed_registry_lineage(session)

    _create_dq_target_table(engine)
    _seed_dq_target_rows(
        engine,
        ingestion_id=ingestion_id,
        source_id=source_id,
        lineage_ref_id=lineage_ref_id,
    )

    config = _build_basic_dq_checks_config()
    checks = (
        SchemaCheck(config),
        NotNullCheck(config),
        DuplicateCheck(
            DuplicateCheckSpec(
                dataset_config=config,
                key_columns=("cpf_hash", "evento", "sessao"),
            ),
            sample_limit=2,
        ),
    )

    with Session(engine) as session:
        context = CheckContext(ingestion_id=ingestion_id, resources={"session": session})
        report = CheckRunner(
            checks,
            fail_on=Severity.ERROR,
            persist_results=True,
            replace_existing_results=True,
            default_source_id=source_id,
        ).run(context)
        persisted_rows = session.exec(
            select(DQCheckResult).where(DQCheckResult.ingestion_id == ingestion_id)
        ).all()

    assert report.summary["total"] == 3
    assert context.metadata["dq_persisted_count"] == 3
    assert len(persisted_rows) == 3
    persisted_ids = {row.check_id for row in persisted_rows}
    assert "dq.schema.runner_target" in persisted_ids
    assert "dq.not_null.runner_target" in persisted_ids
    assert "dq.duplicates.runner_target.cpf_hash_evento_sessao" in persisted_ids
