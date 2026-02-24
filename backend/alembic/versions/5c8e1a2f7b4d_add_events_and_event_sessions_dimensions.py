"""Add canonical dimensions: events and event_sessions.

Revision ID: 5c8e1a2f7b4d
Revises: 4d9a1b7c2e5f
Create Date: 2026-02-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c8e1a2f7b4d"
down_revision = "4d9a1b7c2e5f"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    """Return whether table exists in current database schema."""
    return table_name in set(inspector.get_table_names())


def _ensure_index(
    inspector: sa.Inspector,
    table_name: str,
    index_name: str,
    columns: list[str],
) -> None:
    """Create index only when it does not exist yet."""
    existing = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name not in existing:
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "events"):
        op.create_table(
            "events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("event_key", sa.String(length=120), nullable=False),
            sa.Column("event_name", sa.String(length=200), nullable=False),
            sa.Column("event_start_date", sa.Date(), nullable=True),
            sa.Column("event_end_date", sa.Date(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
            sa.UniqueConstraint("event_key", name="uq_events_event_key"),
        )
        op.create_index(op.f("ix_events_event_key"), "events", ["event_key"], unique=False)
        op.create_index(op.f("ix_events_event_name"), "events", ["event_name"], unique=False)

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "event_sessions"):
        op.create_table(
            "event_sessions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("event_id", sa.Integer(), nullable=True),
            sa.Column("session_key", sa.String(length=120), nullable=False),
            sa.Column("session_name", sa.String(length=200), nullable=False),
            sa.Column("session_type", sa.String(length=30), nullable=False),
            sa.Column("session_date", sa.Date(), nullable=False),
            sa.Column("session_start_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("session_end_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_event_sessions")),
            sa.UniqueConstraint("session_key", name="uq_event_sessions_session_key"),
        )

    inspector = sa.inspect(bind)
    _ensure_index(inspector, "event_sessions", "ix_event_sessions_event_id", ["event_id"])
    _ensure_index(inspector, "event_sessions", "ix_event_sessions_session_date", ["session_date"])
    _ensure_index(inspector, "event_sessions", "ix_event_sessions_session_type", ["session_type"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "event_sessions"):
        foreign_keys = inspector.get_foreign_keys("event_sessions")
        has_fk_to_events = any(fk.get("referred_table") == "events" for fk in foreign_keys)
        if has_fk_to_events:
            for index_name in (
                "ix_event_sessions_session_type",
                "ix_event_sessions_session_date",
                "ix_event_sessions_event_id",
            ):
                existing_indexes = {index["name"] for index in inspector.get_indexes("event_sessions")}
                if index_name in existing_indexes:
                    op.drop_index(index_name, table_name="event_sessions")
            op.drop_table("event_sessions")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "events"):
        existing_indexes = {index["name"] for index in inspector.get_indexes("events")}
        for index_name in (op.f("ix_events_event_name"), op.f("ix_events_event_key")):
            if index_name in existing_indexes:
                op.drop_index(index_name, table_name="events")
        op.drop_table("events")
