"""Add metric lineage table for audit and traceability.

Revision ID: 0668e4b00eb0
Revises: 4ab1241b8178
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0668e4b00eb0"
down_revision = "4ab1241b8178"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metric_lineage",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("metric_key", sa.String(length=200), nullable=False),
        sa.Column("docx_section", sa.String(length=240), nullable=True),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("location_raw", sa.String(length=200), nullable=False),
        sa.Column("location_norm", sa.String(length=200), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
    )
    op.create_index(
        "ix_metric_lineage_metric_key",
        "metric_lineage",
        ["metric_key"],
        unique=False,
    )
    op.create_index(
        "ix_metric_lineage_source_id",
        "metric_lineage",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "ix_metric_lineage_ingestion_id",
        "metric_lineage",
        ["ingestion_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_metric_lineage_ingestion_id", table_name="metric_lineage")
    op.drop_index("ix_metric_lineage_source_id", table_name="metric_lineage")
    op.drop_index("ix_metric_lineage_metric_key", table_name="metric_lineage")
    op.drop_table("metric_lineage")
