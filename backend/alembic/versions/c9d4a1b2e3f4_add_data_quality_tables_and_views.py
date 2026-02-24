"""Add data quality tables and operational views.

Revision ID: c9d4a1b2e3f4
Revises: 7e3c2b1a9f0d
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


revision = "c9d4a1b2e3f4"
down_revision = "7e3c2b1a9f0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_evidence",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("extractor", sa.String(length=120), nullable=False),
        sa.Column("evidence_status", sa.String(length=40), nullable=False),
        sa.Column("layout_signature", sa.String(length=64), nullable=True),
        sa.Column("stats_json", sa.Text(), nullable=True),
        sa.Column("evidence_path", sa.String(length=800), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.UniqueConstraint("ingestion_id", "extractor", name="uq_ingestion_evidence_ingestion_extractor"),
    )
    op.create_index("ix_ingestion_evidence_ingestion_id", "ingestion_evidence", ["ingestion_id"], unique=False)
    op.create_index("ix_ingestion_evidence_source_id", "ingestion_evidence", ["source_id"], unique=False)
    op.create_index("ix_ingestion_evidence_layout_signature", "ingestion_evidence", ["layout_signature"], unique=False)

    op.create_table(
        "data_quality_result",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("scope", sa.String(length=20), nullable=False),
        sa.Column("severity", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("check_key", sa.String(length=220), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
    )
    op.create_index("ix_data_quality_result_ingestion_id", "data_quality_result", ["ingestion_id"], unique=False)
    op.create_index("ix_data_quality_result_source_id", "data_quality_result", ["source_id"], unique=False)
    op.create_index("ix_data_quality_result_session_id", "data_quality_result", ["session_id"], unique=False)
    op.create_index("ix_data_quality_result_scope", "data_quality_result", ["scope"], unique=False)
    op.create_index("ix_data_quality_result_severity", "data_quality_result", ["severity"], unique=False)
    op.create_index("ix_data_quality_result_status", "data_quality_result", ["status"], unique=False)
    op.create_index("ix_data_quality_result_check_key", "data_quality_result", ["check_key"], unique=False)

    # Operational views (best-effort; can be recomputed without data loss).
    op.execute("DROP VIEW IF EXISTS mart_dq_ingestion_summary")
    op.execute("DROP VIEW IF EXISTS mart_dq_ingestion_with_summary")
    op.execute("DROP VIEW IF EXISTS mart_dq_session_summary")

    op.execute(
        """
CREATE VIEW mart_dq_ingestion_summary AS
SELECT
  ingestion_id,
  source_id,
  SUM(CASE WHEN severity = 'ERROR' AND status = 'FAIL' THEN 1 ELSE 0 END) AS error_fail_count,
  SUM(CASE WHEN severity = 'WARN' AND status = 'FAIL' THEN 1 ELSE 0 END) AS warn_fail_count,
  SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS pass_count,
  COUNT(*) AS total_count,
  MAX(created_at) AS last_checked_at
FROM data_quality_result
GROUP BY ingestion_id, source_id
"""
    )

    op.execute(
        """
CREATE VIEW mart_dq_ingestion_with_summary AS
SELECT
  i.id AS ingestion_id,
  i.source_id AS source_id,
  i.pipeline AS pipeline,
  i.status AS ingestion_status,
  i.started_at AS started_at,
  i.finished_at AS finished_at,
  COALESCE(s.error_fail_count, 0) AS error_fail_count,
  COALESCE(s.warn_fail_count, 0) AS warn_fail_count,
  COALESCE(s.pass_count, 0) AS pass_count,
  COALESCE(s.total_count, 0) AS total_count,
  s.last_checked_at AS last_checked_at
FROM ingestion i
LEFT JOIN mart_dq_ingestion_summary s ON s.ingestion_id = i.id
"""
    )

    op.execute(
        """
CREATE VIEW mart_dq_session_summary AS
SELECT
  session_id,
  SUM(CASE WHEN severity = 'ERROR' AND status = 'FAIL' THEN 1 ELSE 0 END) AS error_fail_count,
  SUM(CASE WHEN severity = 'WARN' AND status = 'FAIL' THEN 1 ELSE 0 END) AS warn_fail_count,
  COUNT(*) AS total_count,
  MAX(created_at) AS last_checked_at
FROM data_quality_result
WHERE session_id IS NOT NULL
GROUP BY session_id
"""
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS mart_dq_session_summary")
    op.execute("DROP VIEW IF EXISTS mart_dq_ingestion_with_summary")
    op.execute("DROP VIEW IF EXISTS mart_dq_ingestion_summary")

    op.drop_index("ix_data_quality_result_check_key", table_name="data_quality_result")
    op.drop_index("ix_data_quality_result_status", table_name="data_quality_result")
    op.drop_index("ix_data_quality_result_severity", table_name="data_quality_result")
    op.drop_index("ix_data_quality_result_scope", table_name="data_quality_result")
    op.drop_index("ix_data_quality_result_session_id", table_name="data_quality_result")
    op.drop_index("ix_data_quality_result_source_id", table_name="data_quality_result")
    op.drop_index("ix_data_quality_result_ingestion_id", table_name="data_quality_result")
    op.drop_table("data_quality_result")

    op.drop_index("ix_ingestion_evidence_layout_signature", table_name="ingestion_evidence")
    op.drop_index("ix_ingestion_evidence_source_id", table_name="ingestion_evidence")
    op.drop_index("ix_ingestion_evidence_ingestion_id", table_name="ingestion_evidence")
    op.drop_table("ingestion_evidence")

