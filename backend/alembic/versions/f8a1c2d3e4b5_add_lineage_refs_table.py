"""Add lineage_refs table for source-location evidence traceability.

Revision ID: f8a1c2d3e4b5
Revises: e4c7b8a9d0f1
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f8a1c2d3e4b5"
down_revision = "e4c7b8a9d0f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lineage_refs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("location_type", sa.String(length=16), nullable=False),
        sa.Column("location_value", sa.String(length=200), nullable=False),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "location_type in ('page','slide','sheet','range')",
            name="ck_lineage_refs_location_type_domain",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
    )
    op.create_index("ix_lineage_refs_source_id", "lineage_refs", ["source_id"], unique=False)
    op.create_index("ix_lineage_refs_ingestion_id", "lineage_refs", ["ingestion_id"], unique=False)
    op.create_index(
        "ix_lineage_refs_location_type",
        "lineage_refs",
        ["location_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lineage_refs_location_type", table_name="lineage_refs")
    op.drop_index("ix_lineage_refs_ingestion_id", table_name="lineage_refs")
    op.drop_index("ix_lineage_refs_source_id", table_name="lineage_refs")
    op.drop_table("lineage_refs")

