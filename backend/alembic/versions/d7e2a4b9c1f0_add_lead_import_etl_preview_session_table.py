"""Add lead_import_etl_preview_session table for ETL preview/commit flow.

Revision ID: d7e2a4b9c1f0
Revises: c6a2d9f1b4e7
Create Date: 2026-03-03
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d7e2a4b9c1f0"
down_revision = "c6a2d9f1b4e7"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return bool(_inspector().has_table(table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(index["name"] == index_name for index in _inspector().get_indexes(table_name))


def upgrade() -> None:
    if not _table_exists("lead_import_etl_preview_session"):
        op.create_table(
            "lead_import_etl_preview_session",
            sa.Column("session_token", sa.String(length=120), nullable=False),
            sa.Column("idempotency_key", sa.String(length=160), nullable=False),
            sa.Column("evento_id", sa.Integer(), nullable=False),
            sa.Column("evento_nome", sa.String(length=150), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("strict", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="previewed"),
            sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("valid_rows", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("invalid_rows", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("has_validation_errors", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("approved_rows_json", sa.Text(), nullable=False),
            sa.Column("rejected_rows_json", sa.Text(), nullable=False),
            sa.Column("dq_report_json", sa.Text(), nullable=False),
            sa.Column("commit_result_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["evento_id"], ["evento.id"], name="fk_lead_import_etl_preview_session_evento_id_evento"),
            sa.PrimaryKeyConstraint("session_token", name="pk_lead_import_etl_preview_session"),
            sa.UniqueConstraint("idempotency_key", name="uq_lead_import_etl_preview_session_idempotency_key"),
        )

    if _table_exists("lead_import_etl_preview_session"):
        if not _index_exists("lead_import_etl_preview_session", "ix_lead_import_etl_preview_session_evento_id"):
            op.create_index(
                "ix_lead_import_etl_preview_session_evento_id",
                "lead_import_etl_preview_session",
                ["evento_id"],
                unique=False,
            )
        if not _index_exists("lead_import_etl_preview_session", "ix_lead_import_etl_preview_session_status"):
            op.create_index(
                "ix_lead_import_etl_preview_session_status",
                "lead_import_etl_preview_session",
                ["status"],
                unique=False,
            )
        if not _index_exists("lead_import_etl_preview_session", "ix_lead_import_etl_preview_session_created_at"):
            op.create_index(
                "ix_lead_import_etl_preview_session_created_at",
                "lead_import_etl_preview_session",
                ["created_at"],
                unique=False,
            )
        if not _index_exists("lead_import_etl_preview_session", "ix_lead_import_etl_preview_session_idempotency_key"):
            op.create_index(
                "ix_lead_import_etl_preview_session_idempotency_key",
                "lead_import_etl_preview_session",
                ["idempotency_key"],
                unique=True,
            )


def downgrade() -> None:
    # Politica nao-destrutiva deste rollout: sem DROP/DOWNGRADE destrutivo automatico.
    pass

