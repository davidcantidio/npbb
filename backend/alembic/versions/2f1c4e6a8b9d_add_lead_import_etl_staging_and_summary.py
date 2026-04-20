"""Add lead import ETL staging table and session summary columns.

Revision ID: 2f1c4e6a8b9d
Revises: 0f2e3d4c5b6a
Create Date: 2026-04-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "2f1c4e6a8b9d"
down_revision = "0f2e3d4c5b6a"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return bool(_inspector().has_table(table_name))


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return column_name in {column["name"] for column in _inspector().get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(index["name"] == index_name for index in _inspector().get_indexes(table_name))


def upgrade() -> None:
    if _table_exists("lead_import_etl_preview_session"):
        preview_columns: list[tuple[str, sa.Column]] = [
            ("requested_by", sa.Column("requested_by", sa.Integer(), nullable=True)),
            ("source_file_size_bytes", sa.Column("source_file_size_bytes", sa.Integer(), nullable=True)),
            ("ingestion_strategy", sa.Column("ingestion_strategy", sa.String(length=32), nullable=True)),
            ("staged_rows", sa.Column("staged_rows", sa.Integer(), nullable=False, server_default="0")),
            ("duplicate_rows", sa.Column("duplicate_rows", sa.Integer(), nullable=False, server_default="0")),
            ("created_rows", sa.Column("created_rows", sa.Integer(), nullable=False, server_default="0")),
            ("updated_rows", sa.Column("updated_rows", sa.Integer(), nullable=False, server_default="0")),
            ("skipped_rows", sa.Column("skipped_rows", sa.Integer(), nullable=False, server_default="0")),
            ("error_rows", sa.Column("error_rows", sa.Integer(), nullable=False, server_default="0")),
        ]
        for column_name, column in preview_columns:
            if not _column_exists("lead_import_etl_preview_session", column_name):
                op.add_column("lead_import_etl_preview_session", column)
        if not _index_exists("lead_import_etl_preview_session", "ix_lead_import_etl_preview_session_requested_by"):
            op.create_index(
                "ix_lead_import_etl_preview_session_requested_by",
                "lead_import_etl_preview_session",
                ["requested_by"],
                unique=False,
            )

    if not _table_exists("lead_import_etl_job"):
        op.create_table(
            "lead_import_etl_job",
            sa.Column("job_id", sa.String(length=120), nullable=False),
            sa.Column("requested_by", sa.Integer(), nullable=False),
            sa.Column("evento_id", sa.Integer(), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("strict", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
            sa.Column("progress_json", sa.JSON(), nullable=True),
            sa.Column("options_json", sa.JSON(), nullable=True),
            sa.Column("result_json", sa.JSON(), nullable=True),
            sa.Column("error_json", sa.JSON(), nullable=True),
            sa.Column("file_blob", sa.LargeBinary(), nullable=True),
            sa.Column("preview_session_token", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["requested_by"], ["usuario.id"], name="fk_lead_import_etl_job_requested_by"),
            sa.ForeignKeyConstraint(["evento_id"], ["evento.id"], name="fk_lead_import_etl_job_evento_id"),
            sa.PrimaryKeyConstraint("job_id", name="pk_lead_import_etl_job"),
        )

    job_indexes: list[tuple[str, list[str], bool]] = [
        ("ix_lead_import_etl_job_requested_by", ["requested_by"], False),
        ("ix_lead_import_etl_job_evento_id", ["evento_id"], False),
        ("ix_lead_import_etl_job_status", ["status"], False),
        ("ix_lead_import_etl_job_preview_session_token", ["preview_session_token"], False),
        ("ix_lead_import_etl_job_created_at", ["created_at"], False),
    ]
    for index_name, columns, unique in job_indexes:
        if not _index_exists("lead_import_etl_job", index_name):
            op.create_index(index_name, "lead_import_etl_job", columns, unique=unique)

    if not _table_exists("lead_import_etl_staging"):
        op.create_table(
            "lead_import_etl_staging",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column("session_token", sa.String(length=120), nullable=False),
            sa.Column("job_id", sa.String(length=120), nullable=True),
            sa.Column("requested_by", sa.Integer(), nullable=True),
            sa.Column("evento_id", sa.Integer(), nullable=False),
            sa.Column("source_file", sa.String(length=255), nullable=False),
            sa.Column("source_sheet", sa.String(length=120), nullable=True),
            sa.Column("source_row_number", sa.Integer(), nullable=False),
            sa.Column("row_hash", sa.String(length=64), nullable=False),
            sa.Column("dedupe_key", sa.String(length=255), nullable=True),
            sa.Column("raw_payload_json", sa.JSON(), nullable=False),
            sa.Column("normalized_payload_json", sa.JSON(), nullable=True),
            sa.Column("validation_status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("validation_errors_json", sa.JSON(), nullable=True),
            sa.Column("merge_status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("merge_error", sa.Text(), nullable=True),
            sa.Column("merged_lead_id", sa.Integer(), nullable=True),
            sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["session_token"], ["lead_import_etl_preview_session.session_token"], name="fk_lead_import_etl_staging_session_token"),
            sa.ForeignKeyConstraint(["job_id"], ["lead_import_etl_job.job_id"], name="fk_lead_import_etl_staging_job_id"),
            sa.ForeignKeyConstraint(["requested_by"], ["usuario.id"], name="fk_lead_import_etl_staging_requested_by"),
            sa.ForeignKeyConstraint(["evento_id"], ["evento.id"], name="fk_lead_import_etl_staging_evento_id"),
            sa.ForeignKeyConstraint(["merged_lead_id"], ["lead.id"], name="fk_lead_import_etl_staging_merged_lead_id"),
            sa.UniqueConstraint("session_token", "source_row_number", name="uq_lead_import_etl_staging_session_row"),
        )

    staging_indexes: list[tuple[str, list[str], bool]] = [
        ("ix_lead_import_etl_staging_session_token", ["session_token"], False),
        ("ix_lead_import_etl_staging_job_id", ["job_id"], False),
        ("ix_lead_import_etl_staging_requested_by", ["requested_by"], False),
        ("ix_lead_import_etl_staging_evento_id", ["evento_id"], False),
        ("ix_lead_import_etl_staging_source_row_number", ["source_row_number"], False),
        ("ix_lead_import_etl_staging_row_hash", ["row_hash"], False),
        ("ix_lead_import_etl_staging_merged_lead_id", ["merged_lead_id"], False),
        ("ix_lead_import_etl_staging_created_at", ["created_at"], False),
        (
            "ix_lead_import_etl_staging_session_validation_status",
            ["session_token", "validation_status"],
            False,
        ),
        (
            "ix_lead_import_etl_staging_session_merge_status",
            ["session_token", "merge_status"],
            False,
        ),
        (
            "ix_lead_import_etl_staging_session_dedupe_key",
            ["session_token", "dedupe_key"],
            False,
        ),
    ]
    for index_name, columns, unique in staging_indexes:
        if not _index_exists("lead_import_etl_staging", index_name):
            op.create_index(index_name, "lead_import_etl_staging", columns, unique=unique)


def downgrade() -> None:
    # Rollout nao destrutivo: sem drop automatico.
    pass
