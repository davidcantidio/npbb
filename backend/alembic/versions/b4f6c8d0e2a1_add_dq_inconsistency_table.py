"""Add dq_inconsistency table for cross-source conflict findings.

Revision ID: b4f6c8d0e2a1
Revises: a6d9e2f1b3c4
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b4f6c8d0e2a1"
down_revision = "a6d9e2f1b3c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dq_inconsistency",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("check_id", sa.String(length=220), nullable=False),
        sa.Column("dataset_id", sa.String(length=120), nullable=False),
        sa.Column("metric_key", sa.String(length=220), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("values_json", sa.Text(), nullable=False),
        sa.Column("sources_json", sa.Text(), nullable=False),
        sa.Column("lineage_refs_json", sa.Text(), nullable=True),
        sa.Column("evidence_json", sa.Text(), nullable=True),
        sa.Column("suggested_action", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('inconsistente')",
            name="ck_dq_inconsistency_status_domain",
        ),
        sa.CheckConstraint(
            "severity in ('info','warning','error')",
            name="ck_dq_inconsistency_severity_domain",
        ),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
    )
    op.create_index(
        "ix_dq_inconsistency_ingestion_id",
        "dq_inconsistency",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index("ix_dq_inconsistency_check_id", "dq_inconsistency", ["check_id"], unique=False)
    op.create_index("ix_dq_inconsistency_dataset_id", "dq_inconsistency", ["dataset_id"], unique=False)
    op.create_index("ix_dq_inconsistency_metric_key", "dq_inconsistency", ["metric_key"], unique=False)
    op.create_index("ix_dq_inconsistency_status", "dq_inconsistency", ["status"], unique=False)
    op.create_index("ix_dq_inconsistency_severity", "dq_inconsistency", ["severity"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_dq_inconsistency_severity", table_name="dq_inconsistency")
    op.drop_index("ix_dq_inconsistency_status", table_name="dq_inconsistency")
    op.drop_index("ix_dq_inconsistency_metric_key", table_name="dq_inconsistency")
    op.drop_index("ix_dq_inconsistency_dataset_id", table_name="dq_inconsistency")
    op.drop_index("ix_dq_inconsistency_check_id", table_name="dq_inconsistency")
    op.drop_index("ix_dq_inconsistency_ingestion_id", table_name="dq_inconsistency")
    op.drop_table("dq_inconsistency")

