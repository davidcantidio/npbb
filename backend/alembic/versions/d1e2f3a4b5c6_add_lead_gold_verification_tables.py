"""add lead gold verification tables

Revision ID: d1e2f3a4b5c6
Revises: c4d5e6f7a8b9
Create Date: 2026-04-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d1e2f3a4b5c6"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead_batches",
        sa.Column("reprocess_kind", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "lead_batches",
        sa.Column("reprocess_run_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "lead_batches",
        sa.Column("reprocess_source_batch_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_lead_batches_reprocess_kind", "lead_batches", ["reprocess_kind"], unique=False)
    op.create_index("ix_lead_batches_reprocess_run_id", "lead_batches", ["reprocess_run_id"], unique=False)
    op.create_index(
        "ix_lead_batches_reprocess_source_batch_id",
        "lead_batches",
        ["reprocess_source_batch_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_lead_batches_reprocess_source_batch_id_lead_batches",
        "lead_batches",
        "lead_batches",
        ["reprocess_source_batch_id"],
        ["id"],
    )

    op.create_table(
        "lead_gold_verification_run",
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("rules_version", sa.String(length=80), nullable=False),
        sa.Column("scope_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["requested_by"], ["usuario.id"], name="fk_lead_gold_verification_run_requested_by"),
        sa.PrimaryKeyConstraint("run_id"),
        sa.UniqueConstraint("idempotency_key", name="uq_lead_gold_verification_run_idempotency_key"),
    )
    op.create_index(
        "ix_lead_gold_verification_run_status",
        "lead_gold_verification_run",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_run_requested_by",
        "lead_gold_verification_run",
        ["requested_by"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_run_started_at",
        "lead_gold_verification_run",
        ["started_at"],
        unique=False,
    )

    op.create_table(
        "lead_gold_verification_result",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("verification_batch_id", sa.Integer(), nullable=False),
        sa.Column("source_batch_id", sa.Integer(), nullable=True),
        sa.Column("source_lead_id", sa.Integer(), nullable=False),
        sa.Column("resolved_evento_id", sa.Integer(), nullable=True),
        sa.Column("resolved_evento_nome", sa.String(length=150), nullable=True),
        sa.Column("outcome", sa.String(length=24), nullable=False),
        sa.Column("motivo_rejeicao", sa.String(length=255), nullable=True),
        sa.Column("reason_codes_json", sa.JSON(), nullable=True),
        sa.Column("row_data_json", sa.JSON(), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("source_sheet", sa.String(length=120), nullable=True),
        sa.Column("source_row", sa.Integer(), nullable=True),
        sa.Column("source_row_ref", sa.String(length=120), nullable=True),
        sa.Column("dedupe_rank", sa.Integer(), nullable=True),
        sa.Column("duplicate_of_lead_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["duplicate_of_lead_id"], ["lead.id"], name="fk_lead_gold_verification_result_duplicate_of_lead_id"),
        sa.ForeignKeyConstraint(["resolved_evento_id"], ["evento.id"], name="fk_lead_gold_verification_result_resolved_evento_id"),
        sa.ForeignKeyConstraint(["run_id"], ["lead_gold_verification_run.run_id"], name="fk_lead_gold_verification_result_run_id"),
        sa.ForeignKeyConstraint(["source_batch_id"], ["lead_batches.id"], name="fk_lead_gold_verification_result_source_batch_id"),
        sa.ForeignKeyConstraint(["source_lead_id"], ["lead.id"], name="fk_lead_gold_verification_result_source_lead_id"),
        sa.ForeignKeyConstraint(["verification_batch_id"], ["lead_batches.id"], name="fk_lead_gold_verification_result_verification_batch_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "source_lead_id", name="uq_lead_gold_verification_result_run_lead"),
    )
    op.create_index(
        "ix_lead_gold_verification_result_run_id",
        "lead_gold_verification_result",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_verification_batch_id",
        "lead_gold_verification_result",
        ["verification_batch_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_source_batch_id",
        "lead_gold_verification_result",
        ["source_batch_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_source_lead_id",
        "lead_gold_verification_result",
        ["source_lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_resolved_evento_id",
        "lead_gold_verification_result",
        ["resolved_evento_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_duplicate_of_lead_id",
        "lead_gold_verification_result",
        ["duplicate_of_lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_outcome",
        "lead_gold_verification_result",
        ["outcome"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_batch_outcome",
        "lead_gold_verification_result",
        ["verification_batch_id", "outcome"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_source_lead_created_at",
        "lead_gold_verification_result",
        ["source_lead_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_lead_gold_verification_result_run_source_batch",
        "lead_gold_verification_result",
        ["run_id", "source_batch_id"],
        unique=False,
    )

    op.execute(
        """
        create view lead_gold_validation_latest_v as
        select
            ranked.id,
            ranked.run_id,
            ranked.verification_batch_id,
            ranked.source_batch_id,
            ranked.source_lead_id,
            ranked.resolved_evento_id,
            ranked.resolved_evento_nome,
            ranked.outcome,
            ranked.motivo_rejeicao,
            ranked.reason_codes_json,
            ranked.row_data_json,
            ranked.source_file,
            ranked.source_sheet,
            ranked.source_row,
            ranked.source_row_ref,
            ranked.dedupe_rank,
            ranked.duplicate_of_lead_id,
            ranked.created_at
        from (
            select
                r.*,
                row_number() over (
                    partition by r.source_lead_id
                    order by r.created_at desc, r.id desc
                ) as rn
            from lead_gold_verification_result r
        ) ranked
        where ranked.rn = 1
        """
    )
    op.execute(
        """
        create view lead_gold_validated_current_v as
        select *
        from lead_gold_validation_latest_v
        where outcome = 'valid'
        """
    )


def downgrade() -> None:
    op.execute("drop view if exists lead_gold_validated_current_v")
    op.execute("drop view if exists lead_gold_validation_latest_v")

    op.drop_index("ix_lead_gold_verification_result_run_source_batch", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_source_lead_created_at", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_batch_outcome", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_outcome", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_duplicate_of_lead_id", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_resolved_evento_id", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_source_lead_id", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_source_batch_id", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_verification_batch_id", table_name="lead_gold_verification_result")
    op.drop_index("ix_lead_gold_verification_result_run_id", table_name="lead_gold_verification_result")
    op.drop_table("lead_gold_verification_result")

    op.drop_index("ix_lead_gold_verification_run_started_at", table_name="lead_gold_verification_run")
    op.drop_index("ix_lead_gold_verification_run_requested_by", table_name="lead_gold_verification_run")
    op.drop_index("ix_lead_gold_verification_run_status", table_name="lead_gold_verification_run")
    op.drop_table("lead_gold_verification_run")

    op.drop_constraint(
        "fk_lead_batches_reprocess_source_batch_id_lead_batches",
        "lead_batches",
        type_="foreignkey",
    )
    op.drop_index("ix_lead_batches_reprocess_source_batch_id", table_name="lead_batches")
    op.drop_index("ix_lead_batches_reprocess_run_id", table_name="lead_batches")
    op.drop_index("ix_lead_batches_reprocess_kind", table_name="lead_batches")
    op.drop_column("lead_batches", "reprocess_source_batch_id")
    op.drop_column("lead_batches", "reprocess_run_id")
    op.drop_column("lead_batches", "reprocess_kind")
