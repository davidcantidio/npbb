"""Add dq_check_result table for persisted ETL framework findings.

Revision ID: a6d9e2f1b3c4
Revises: 9e7a4c2d1b6f
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a6d9e2f1b3c4"
down_revision = "9e7a4c2d1b6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dq_check_result",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=True),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("check_id", sa.String(length=220), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "severity in ('info','warning','error')",
            name="ck_dq_check_result_severity_domain",
        ),
        sa.CheckConstraint(
            "status in ('pass','fail','skip')",
            name="ck_dq_check_result_status_domain",
        ),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
    )
    op.create_index(
        "ix_dq_check_result_ingestion_id",
        "dq_check_result",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index("ix_dq_check_result_source_id", "dq_check_result", ["source_id"], unique=False)
    op.create_index(
        "ix_dq_check_result_lineage_ref_id",
        "dq_check_result",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index("ix_dq_check_result_check_id", "dq_check_result", ["check_id"], unique=False)
    op.create_index("ix_dq_check_result_severity", "dq_check_result", ["severity"], unique=False)
    op.create_index("ix_dq_check_result_status", "dq_check_result", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_dq_check_result_status", table_name="dq_check_result")
    op.drop_index("ix_dq_check_result_severity", table_name="dq_check_result")
    op.drop_index("ix_dq_check_result_check_id", table_name="dq_check_result")
    op.drop_index("ix_dq_check_result_lineage_ref_id", table_name="dq_check_result")
    op.drop_index("ix_dq_check_result_source_id", table_name="dq_check_result")
    op.drop_index("ix_dq_check_result_ingestion_id", table_name="dq_check_result")
    op.drop_table("dq_check_result")
