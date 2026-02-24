"""Create sources and ingestions tables for ETL registry.

Revision ID: e4c7b8a9d0f1
Revises: d2f4c6a8b0e1
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4c7b8a9d0f1"
down_revision = "d2f4c6a8b0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("uri", sa.String(length=800), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("file_sha256", sa.String(length=64), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_mtime_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", name="uq_sources_source_id"),
    )
    op.create_index("ix_sources_source_id", "sources", ["source_id"], unique=False)
    op.create_index("ix_sources_kind", "sources", ["kind"], unique=False)

    op.create_table(
        "ingestions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_pk", sa.Integer(), nullable=False),
        sa.Column("extractor_name", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_read", sa.Integer(), nullable=True),
        sa.Column("records_loaded", sa.Integer(), nullable=True),
        sa.Column("file_sha256", sa.String(length=64), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("log_text", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('SUCCESS','FAILED','PARTIAL')",
            name="ck_ingestions_status_domain",
        ),
        sa.ForeignKeyConstraint(["source_pk"], ["sources.id"]),
    )
    op.create_index("ix_ingestions_source_pk", "ingestions", ["source_pk"], unique=False)
    op.create_index("ix_ingestions_status", "ingestions", ["status"], unique=False)
    op.create_index("ix_ingestions_started_at", "ingestions", ["started_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ingestions_started_at", table_name="ingestions")
    op.drop_index("ix_ingestions_status", table_name="ingestions")
    op.drop_index("ix_ingestions_source_pk", table_name="ingestions")
    op.drop_table("ingestions")

    op.drop_index("ix_sources_kind", table_name="sources")
    op.drop_index("ix_sources_source_id", table_name="sources")
    op.drop_table("sources")
