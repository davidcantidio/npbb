"""Add lead_batches, leads_silver, lead_column_aliases tables.

Revision ID: e9f1a2b3c4d5
Revises: d7e2a4b9c1f0
Create Date: 2026-03-04
"""

from alembic import op
import sqlalchemy as sa


revision = "e9f1a2b3c4d5"
down_revision = "d7e2a4b9c1f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lead_batches",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("enviado_por", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("plataforma_origem", sa.String(length=80), nullable=False),
        sa.Column("data_envio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_upload", sa.DateTime(timezone=True), nullable=False),
        sa.Column("nome_arquivo_original", sa.String(length=255), nullable=False),
        sa.Column("arquivo_bronze", sa.LargeBinary(), nullable=False),
        sa.Column("stage", sa.String(length=10), nullable=False, server_default="bronze"),
        sa.Column("evento_id", sa.Integer(), sa.ForeignKey("evento.id"), nullable=True),
        sa.Column("pipeline_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("pipeline_report", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_lead_batches_enviado_por", "lead_batches", ["enviado_por"])
    op.create_index("ix_lead_batches_evento_id", "lead_batches", ["evento_id"])
    op.create_index("ix_lead_batches_stage", "lead_batches", ["stage"])
    op.create_index("ix_lead_batches_pipeline_status", "lead_batches", ["pipeline_status"])

    op.create_table(
        "lead_column_aliases",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nome_coluna_original", sa.String(length=255), nullable=False),
        sa.Column("campo_canonico", sa.String(length=100), nullable=False),
        sa.Column("plataforma_origem", sa.String(length=80), nullable=False),
        sa.Column("criado_por", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "nome_coluna_original",
            "plataforma_origem",
            name="uq_lead_column_aliases_coluna_plataforma",
        ),
    )
    op.create_index(
        "ix_lead_column_aliases_plataforma_origem",
        "lead_column_aliases",
        ["plataforma_origem"],
    )
    op.create_index("ix_lead_column_aliases_criado_por", "lead_column_aliases", ["criado_por"])

    op.create_table(
        "leads_silver",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("lead_batches.id"), nullable=False),
        sa.Column("row_index", sa.Integer(), nullable=False),
        sa.Column("dados_brutos", sa.JSON(), nullable=False),
        sa.Column("evento_id", sa.Integer(), sa.ForeignKey("evento.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("batch_id", "row_index", name="uq_leads_silver_batch_row"),
    )
    op.create_index("ix_leads_silver_batch_id", "leads_silver", ["batch_id"])
    op.create_index("ix_leads_silver_row_index", "leads_silver", ["row_index"])
    op.create_index("ix_leads_silver_evento_id", "leads_silver", ["evento_id"])


def downgrade() -> None:
    op.drop_index("ix_leads_silver_evento_id", table_name="leads_silver")
    op.drop_index("ix_leads_silver_row_index", table_name="leads_silver")
    op.drop_index("ix_leads_silver_batch_id", table_name="leads_silver")
    op.drop_table("leads_silver")
    op.drop_index("ix_lead_column_aliases_criado_por", table_name="lead_column_aliases")
    op.drop_index("ix_lead_column_aliases_plataforma_origem", table_name="lead_column_aliases")
    op.drop_table("lead_column_aliases")
    op.drop_index("ix_lead_batches_pipeline_status", table_name="lead_batches")
    op.drop_index("ix_lead_batches_stage", table_name="lead_batches")
    op.drop_index("ix_lead_batches_evento_id", table_name="lead_batches")
    op.drop_index("ix_lead_batches_enviado_por", table_name="lead_batches")
    op.drop_table("lead_batches")
