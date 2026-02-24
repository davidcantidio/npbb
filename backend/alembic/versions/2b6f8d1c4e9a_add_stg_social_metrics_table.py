"""Add stg_social_metrics staging table.

Revision ID: 2b6f8d1c4e9a
Revises: 1c4e5a7b9d2f
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b6f8d1c4e9a"
down_revision = "1c4e5a7b9d2f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stg_social_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("slide_number", sa.Integer(), nullable=False),
        sa.Column("slide_title", sa.String(length=400), nullable=True),
        sa.Column("location_value", sa.String(length=32), nullable=False),
        sa.Column("platform", sa.String(length=120), nullable=False),
        sa.Column("metric_name", sa.String(length=160), nullable=False),
        sa.Column("metric_value", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("metric_value_raw", sa.String(length=80), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("evidence_label", sa.String(length=200), nullable=False),
        sa.Column("evidence_text", sa.Text(), nullable=False),
        sa.Column("extraction_rule", sa.String(length=500), nullable=False),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_social_metrics")),
        sa.UniqueConstraint(
            "source_id",
            "ingestion_id",
            "platform",
            "metric_name",
            "slide_number",
            name="uq_stg_social_metrics_source_ingestion_metric_slide",
        ),
    )
    op.create_index(
        op.f("ix_stg_social_metrics_source_id"),
        "stg_social_metrics",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_social_metrics_ingestion_id"),
        "stg_social_metrics",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_social_metrics_lineage_ref_id"),
        "stg_social_metrics",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_social_metrics_slide_number"),
        "stg_social_metrics",
        ["slide_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_social_metrics_platform"),
        "stg_social_metrics",
        ["platform"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_social_metrics_metric_name"),
        "stg_social_metrics",
        ["metric_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stg_social_metrics_metric_name"), table_name="stg_social_metrics")
    op.drop_index(op.f("ix_stg_social_metrics_platform"), table_name="stg_social_metrics")
    op.drop_index(op.f("ix_stg_social_metrics_slide_number"), table_name="stg_social_metrics")
    op.drop_index(op.f("ix_stg_social_metrics_lineage_ref_id"), table_name="stg_social_metrics")
    op.drop_index(op.f("ix_stg_social_metrics_ingestion_id"), table_name="stg_social_metrics")
    op.drop_index(op.f("ix_stg_social_metrics_source_id"), table_name="stg_social_metrics")
    op.drop_table("stg_social_metrics")
