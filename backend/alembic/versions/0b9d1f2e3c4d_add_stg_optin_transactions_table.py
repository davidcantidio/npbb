"""Add stg_optin_transactions staging table.

Revision ID: 0b9d1f2e3c4d
Revises: f8a1c2d3e4b5
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0b9d1f2e3c4d"
down_revision = "f8a1c2d3e4b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stg_optin_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("sheet_name", sa.String(length=120), nullable=False),
        sa.Column("header_row", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("source_range", sa.String(length=64), nullable=False),
        sa.Column("evento", sa.String(length=200), nullable=True),
        sa.Column("sessao", sa.String(length=200), nullable=True),
        sa.Column("dt_hr_compra", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opt_in", sa.String(length=200), nullable=True),
        sa.Column("opt_in_id", sa.String(length=120), nullable=True),
        sa.Column("opt_in_status", sa.String(length=120), nullable=True),
        sa.Column("canal_venda", sa.String(length=160), nullable=True),
        sa.Column("metodo_entrega", sa.String(length=160), nullable=True),
        sa.Column("ingresso", sa.String(length=200), nullable=True),
        sa.Column("qtd_ingresso", sa.Integer(), nullable=True),
        sa.Column("cpf_hash", sa.String(length=64), nullable=True),
        sa.Column("email_hash", sa.String(length=64), nullable=True),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_optin_transactions")),
        sa.UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_stg_optin_source_sheet_row",
        ),
    )
    op.create_index(
        op.f("ix_stg_optin_transactions_source_id"),
        "stg_optin_transactions",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_optin_transactions_ingestion_id"),
        "stg_optin_transactions",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_optin_transactions_lineage_ref_id"),
        "stg_optin_transactions",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_optin_transactions_sheet_name"),
        "stg_optin_transactions",
        ["sheet_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_optin_transactions_cpf_hash"),
        "stg_optin_transactions",
        ["cpf_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_optin_transactions_email_hash"),
        "stg_optin_transactions",
        ["email_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stg_optin_transactions_email_hash"), table_name="stg_optin_transactions")
    op.drop_index(op.f("ix_stg_optin_transactions_cpf_hash"), table_name="stg_optin_transactions")
    op.drop_index(op.f("ix_stg_optin_transactions_sheet_name"), table_name="stg_optin_transactions")
    op.drop_index(op.f("ix_stg_optin_transactions_lineage_ref_id"), table_name="stg_optin_transactions")
    op.drop_index(op.f("ix_stg_optin_transactions_ingestion_id"), table_name="stg_optin_transactions")
    op.drop_index(op.f("ix_stg_optin_transactions_source_id"), table_name="stg_optin_transactions")
    op.drop_table("stg_optin_transactions")

