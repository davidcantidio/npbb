"""Add stg_access_control_sessions staging table.

Revision ID: 3d8f2a4b7c1e
Revises: 2b6f8d1c4e9a
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d8f2a4b7c1e"
down_revision = "2b6f8d1c4e9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stg_access_control_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("pdf_page", sa.Integer(), nullable=False),
        sa.Column("session_name", sa.String(length=200), nullable=False),
        sa.Column("ingressos_validos", sa.Integer(), nullable=True),
        sa.Column("invalidos", sa.Integer(), nullable=True),
        sa.Column("bloqueados", sa.Integer(), nullable=True),
        sa.Column("presentes", sa.Integer(), nullable=True),
        sa.Column("ausentes", sa.Integer(), nullable=True),
        sa.Column("comparecimento_pct", sa.Numeric(precision=7, scale=4), nullable=True),
        sa.Column("table_header", sa.String(length=500), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_access_control_sessions")),
        sa.UniqueConstraint(
            "source_id",
            "ingestion_id",
            "pdf_page",
            "session_name",
            name="uq_stg_access_control_source_ingestion_page_session",
        ),
    )
    op.create_index(
        op.f("ix_stg_access_control_sessions_source_id"),
        "stg_access_control_sessions",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_access_control_sessions_ingestion_id"),
        "stg_access_control_sessions",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_access_control_sessions_lineage_ref_id"),
        "stg_access_control_sessions",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_access_control_sessions_pdf_page"),
        "stg_access_control_sessions",
        ["pdf_page"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_access_control_sessions_session_name"),
        "stg_access_control_sessions",
        ["session_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stg_access_control_sessions_session_name"), table_name="stg_access_control_sessions")
    op.drop_index(op.f("ix_stg_access_control_sessions_pdf_page"), table_name="stg_access_control_sessions")
    op.drop_index(op.f("ix_stg_access_control_sessions_lineage_ref_id"), table_name="stg_access_control_sessions")
    op.drop_index(op.f("ix_stg_access_control_sessions_ingestion_id"), table_name="stg_access_control_sessions")
    op.drop_index(op.f("ix_stg_access_control_sessions_source_id"), table_name="stg_access_control_sessions")
    op.drop_table("stg_access_control_sessions")
