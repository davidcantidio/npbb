"""Add stg_dimac_metrics and stg_mtc_metrics staging tables.

Revision ID: 4d9a1b7c2e5f
Revises: 3d8f2a4b7c1e
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d9a1b7c2e5f"
down_revision = "3d8f2a4b7c1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stg_dimac_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("metric_key", sa.String(length=200), nullable=False),
        sa.Column("metric_label", sa.String(length=200), nullable=True),
        sa.Column("metric_value", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("metric_value_raw", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=8), nullable=False),
        sa.Column("gap_reason", sa.Text(), nullable=True),
        sa.Column("pdf_page", sa.Integer(), nullable=True),
        sa.Column("location_value", sa.String(length=40), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("extraction_rule", sa.String(length=500), nullable=False),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('ok','gap')",
            name="ck_stg_dimac_metrics_status_domain",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_dimac_metrics")),
        sa.UniqueConstraint(
            "source_id",
            "ingestion_id",
            "metric_key",
            name="uq_stg_dimac_source_ingestion_metric",
        ),
    )
    op.create_index(
        op.f("ix_stg_dimac_metrics_source_id"),
        "stg_dimac_metrics",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_dimac_metrics_ingestion_id"),
        "stg_dimac_metrics",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_dimac_metrics_lineage_ref_id"),
        "stg_dimac_metrics",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_dimac_metrics_metric_key"),
        "stg_dimac_metrics",
        ["metric_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_dimac_metrics_status"),
        "stg_dimac_metrics",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_dimac_metrics_pdf_page"),
        "stg_dimac_metrics",
        ["pdf_page"],
        unique=False,
    )

    op.create_table(
        "stg_mtc_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("metric_key", sa.String(length=200), nullable=False),
        sa.Column("metric_label", sa.String(length=200), nullable=True),
        sa.Column("metric_value", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("metric_value_raw", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=8), nullable=False),
        sa.Column("gap_reason", sa.Text(), nullable=True),
        sa.Column("pdf_page", sa.Integer(), nullable=True),
        sa.Column("location_value", sa.String(length=40), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("extraction_rule", sa.String(length=500), nullable=False),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('ok','gap')",
            name="ck_stg_mtc_metrics_status_domain",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_mtc_metrics")),
        sa.UniqueConstraint(
            "source_id",
            "ingestion_id",
            "metric_key",
            name="uq_stg_mtc_source_ingestion_metric",
        ),
    )
    op.create_index(
        op.f("ix_stg_mtc_metrics_source_id"),
        "stg_mtc_metrics",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_mtc_metrics_ingestion_id"),
        "stg_mtc_metrics",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_mtc_metrics_lineage_ref_id"),
        "stg_mtc_metrics",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_mtc_metrics_metric_key"),
        "stg_mtc_metrics",
        ["metric_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_mtc_metrics_status"),
        "stg_mtc_metrics",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_mtc_metrics_pdf_page"),
        "stg_mtc_metrics",
        ["pdf_page"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stg_mtc_metrics_pdf_page"), table_name="stg_mtc_metrics")
    op.drop_index(op.f("ix_stg_mtc_metrics_status"), table_name="stg_mtc_metrics")
    op.drop_index(op.f("ix_stg_mtc_metrics_metric_key"), table_name="stg_mtc_metrics")
    op.drop_index(op.f("ix_stg_mtc_metrics_lineage_ref_id"), table_name="stg_mtc_metrics")
    op.drop_index(op.f("ix_stg_mtc_metrics_ingestion_id"), table_name="stg_mtc_metrics")
    op.drop_index(op.f("ix_stg_mtc_metrics_source_id"), table_name="stg_mtc_metrics")
    op.drop_table("stg_mtc_metrics")

    op.drop_index(op.f("ix_stg_dimac_metrics_pdf_page"), table_name="stg_dimac_metrics")
    op.drop_index(op.f("ix_stg_dimac_metrics_status"), table_name="stg_dimac_metrics")
    op.drop_index(op.f("ix_stg_dimac_metrics_metric_key"), table_name="stg_dimac_metrics")
    op.drop_index(op.f("ix_stg_dimac_metrics_lineage_ref_id"), table_name="stg_dimac_metrics")
    op.drop_index(op.f("ix_stg_dimac_metrics_ingestion_id"), table_name="stg_dimac_metrics")
    op.drop_index(op.f("ix_stg_dimac_metrics_source_id"), table_name="stg_dimac_metrics")
    op.drop_table("stg_dimac_metrics")
