"""Add landing phase 3 analytics and audit tables.

Revision ID: 7f3c2d1b4a6e
Revises: 6d5f4c3b2a10
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa


revision = "7f3c2d1b4a6e"
down_revision = "6d5f4c3b2a10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evento_landing_customization_audit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(length=80), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("changed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["usuario.id"]),
        sa.ForeignKeyConstraint(["event_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_evento_landing_customization_audit_event_id",
        "evento_landing_customization_audit",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        "ix_evento_landing_customization_audit_changed_by_user_id",
        "evento_landing_customization_audit",
        ["changed_by_user_id"],
        unique=False,
    )

    op.create_table(
        "landing_analytics_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("ativacao_id", sa.Integer(), nullable=True),
        sa.Column("categoria", sa.String(length=80), nullable=False),
        sa.Column("tema", sa.String(length=80), nullable=False),
        sa.Column("event_name", sa.String(length=60), nullable=False),
        sa.Column("cta_variant_id", sa.String(length=60), nullable=True),
        sa.Column("landing_session_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ativacao_id"], ["ativacao.id"]),
        sa.ForeignKeyConstraint(["event_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_landing_analytics_event_event_id", "landing_analytics_event", ["event_id"], unique=False)
    op.create_index(
        "ix_landing_analytics_event_ativacao_id",
        "landing_analytics_event",
        ["ativacao_id"],
        unique=False,
    )
    op.create_index(
        "ix_landing_analytics_event_categoria",
        "landing_analytics_event",
        ["categoria"],
        unique=False,
    )
    op.create_index(
        "ix_landing_analytics_event_event_name",
        "landing_analytics_event",
        ["event_name"],
        unique=False,
    )
    op.create_index(
        "ix_landing_analytics_event_cta_variant_id",
        "landing_analytics_event",
        ["cta_variant_id"],
        unique=False,
    )
    op.create_index(
        "ix_landing_analytics_event_landing_session_id",
        "landing_analytics_event",
        ["landing_session_id"],
        unique=False,
    )
    op.create_index(
        "ix_landing_analytics_event_created_at",
        "landing_analytics_event",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_landing_analytics_event_created_at", table_name="landing_analytics_event")
    op.drop_index("ix_landing_analytics_event_landing_session_id", table_name="landing_analytics_event")
    op.drop_index("ix_landing_analytics_event_cta_variant_id", table_name="landing_analytics_event")
    op.drop_index("ix_landing_analytics_event_event_name", table_name="landing_analytics_event")
    op.drop_index("ix_landing_analytics_event_categoria", table_name="landing_analytics_event")
    op.drop_index("ix_landing_analytics_event_ativacao_id", table_name="landing_analytics_event")
    op.drop_index("ix_landing_analytics_event_event_id", table_name="landing_analytics_event")
    op.drop_table("landing_analytics_event")

    op.drop_index(
        "ix_evento_landing_customization_audit_changed_by_user_id",
        table_name="evento_landing_customization_audit",
    )
    op.drop_index(
        "ix_evento_landing_customization_audit_event_id",
        table_name="evento_landing_customization_audit",
    )
    op.drop_table("evento_landing_customization_audit")
