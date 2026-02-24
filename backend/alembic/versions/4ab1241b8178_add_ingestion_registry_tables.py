"""Add ingestion registry tables (source + ingestion).

Revision ID: 4ab1241b8178
Revises: 7c6d5e4f3a2b
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4ab1241b8178"
down_revision = "7c6d5e4f3a2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source",
        sa.Column("source_id", sa.String(length=160), primary_key=True, nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("uri", sa.String(length=800), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("file_sha256", sa.String(length=64), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_mtime_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_kind", "source", ["kind"], unique=False)

    op.create_table(
        "ingestion",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("pipeline", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("file_sha256", sa.String(length=64), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("log_text", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
    )
    op.create_index("ix_ingestion_source_id", "ingestion", ["source_id"], unique=False)
    op.create_index("ix_ingestion_status", "ingestion", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ingestion_status", table_name="ingestion")
    op.drop_index("ix_ingestion_source_id", table_name="ingestion")
    op.drop_table("ingestion")

    op.drop_index("ix_source_kind", table_name="source")
    op.drop_table("source")
