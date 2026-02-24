"""Add event/session references to staging tables.

Revision ID: 6b1d4e9f2a3c
Revises: 5c8e1a2f7b4d
Create Date: 2026-02-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b1d4e9f2a3c"
down_revision = "5c8e1a2f7b4d"
branch_labels = None
depends_on = None


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    """Return whether one column exists in target table."""
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    """Return whether one index exists in target table."""
    return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


def _foreign_key_exists(inspector: sa.Inspector, table_name: str, fk_name: str) -> bool:
    """Return whether one foreign key exists in target table."""
    return fk_name in {fk["name"] for fk in inspector.get_foreign_keys(table_name)}


def _add_session_columns(table_name: str, session_fk_name: str) -> None:
    """Add event/session resolution columns to one staging table if missing."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _column_exists(inspector, table_name, "event_id"):
        op.add_column(table_name, sa.Column("event_id", sa.Integer(), nullable=True))
    if not _column_exists(inspector, table_name, "session_id"):
        op.add_column(table_name, sa.Column("session_id", sa.Integer(), nullable=True))
    if not _column_exists(inspector, table_name, "session_resolution_finding"):
        op.add_column(table_name, sa.Column("session_resolution_finding", sa.Text(), nullable=True))

    inspector = sa.inspect(bind)
    if not _index_exists(inspector, table_name, f"ix_{table_name}_event_id"):
        op.create_index(f"ix_{table_name}_event_id", table_name, ["event_id"], unique=False)
    if not _index_exists(inspector, table_name, f"ix_{table_name}_session_id"):
        op.create_index(f"ix_{table_name}_session_id", table_name, ["session_id"], unique=False)
    if not _foreign_key_exists(inspector, table_name, session_fk_name):
        op.create_foreign_key(
            session_fk_name,
            table_name,
            "event_sessions",
            ["session_id"],
            ["id"],
        )


def upgrade() -> None:
    _add_session_columns("stg_optin_transactions", "fk_stg_optin_transactions_session_id_event_sessions")
    _add_session_columns("stg_access_control_sessions", "fk_stg_access_control_sessions_session_id_event_sessions")
    _add_session_columns("stg_social_metrics", "fk_stg_social_metrics_session_id_event_sessions")


def _drop_session_columns(table_name: str, session_fk_name: str) -> None:
    """Drop event/session resolution columns from one staging table if present."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _foreign_key_exists(inspector, table_name, session_fk_name):
        op.drop_constraint(session_fk_name, table_name, type_="foreignkey")

    inspector = sa.inspect(bind)
    for index_name in (f"ix_{table_name}_session_id", f"ix_{table_name}_event_id"):
        if _index_exists(inspector, table_name, index_name):
            op.drop_index(index_name, table_name=table_name)

    inspector = sa.inspect(bind)
    if _column_exists(inspector, table_name, "session_resolution_finding"):
        op.drop_column(table_name, "session_resolution_finding")
    if _column_exists(inspector, table_name, "session_id"):
        op.drop_column(table_name, "session_id")
    if _column_exists(inspector, table_name, "event_id"):
        op.drop_column(table_name, "event_id")


def downgrade() -> None:
    _drop_session_columns("stg_social_metrics", "fk_stg_social_metrics_session_id_event_sessions")
    _drop_session_columns("stg_access_control_sessions", "fk_stg_access_control_sessions_session_id_event_sessions")
    _drop_session_columns("stg_optin_transactions", "fk_stg_optin_transactions_session_id_event_sessions")
