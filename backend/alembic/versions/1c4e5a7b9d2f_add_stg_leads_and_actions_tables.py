"""Add staging tables for leads and parsed actions.

Revision ID: 1c4e5a7b9d2f
Revises: 0b9d1f2e3c4d
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c4e5a7b9d2f"
down_revision = "0b9d1f2e3c4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stg_leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("sheet_name", sa.String(length=120), nullable=False),
        sa.Column("header_row", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("source_range", sa.String(length=64), nullable=False),
        sa.Column("evento", sa.String(length=200), nullable=True),
        sa.Column("data_criacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sexo", sa.String(length=40), nullable=True),
        sa.Column("estado", sa.String(length=40), nullable=True),
        sa.Column("cidade", sa.String(length=120), nullable=True),
        sa.Column("interesses", sa.Text(), nullable=True),
        sa.Column("area_atuacao", sa.Text(), nullable=True),
        sa.Column("cpf_hash", sa.String(length=64), nullable=True),
        sa.Column("email_hash", sa.String(length=64), nullable=True),
        sa.Column("person_key_hash", sa.String(length=64), nullable=True),
        sa.Column("cpf_promotor_hash", sa.String(length=64), nullable=True),
        sa.Column("nome_promotor", sa.String(length=200), nullable=True),
        sa.Column("acoes_raw", sa.Text(), nullable=True),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_leads")),
        sa.UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_stg_leads_source_sheet_row",
        ),
    )
    op.create_index(op.f("ix_stg_leads_source_id"), "stg_leads", ["source_id"], unique=False)
    op.create_index(op.f("ix_stg_leads_ingestion_id"), "stg_leads", ["ingestion_id"], unique=False)
    op.create_index(op.f("ix_stg_leads_lineage_ref_id"), "stg_leads", ["lineage_ref_id"], unique=False)
    op.create_index(op.f("ix_stg_leads_sheet_name"), "stg_leads", ["sheet_name"], unique=False)
    op.create_index(op.f("ix_stg_leads_cpf_hash"), "stg_leads", ["cpf_hash"], unique=False)
    op.create_index(op.f("ix_stg_leads_email_hash"), "stg_leads", ["email_hash"], unique=False)
    op.create_index(op.f("ix_stg_leads_person_key_hash"), "stg_leads", ["person_key_hash"], unique=False)
    op.create_index(
        op.f("ix_stg_leads_cpf_promotor_hash"),
        "stg_leads",
        ["cpf_promotor_hash"],
        unique=False,
    )

    op.create_table(
        "stg_lead_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("action_order", sa.Integer(), nullable=False),
        sa.Column("action_raw", sa.String(length=200), nullable=False),
        sa.Column("action_norm", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["stg_leads.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stg_lead_actions")),
        sa.UniqueConstraint(
            "lead_id",
            "action_norm",
            name="uq_stg_lead_actions_lead_action_norm",
        ),
    )
    op.create_index(op.f("ix_stg_lead_actions_lead_id"), "stg_lead_actions", ["lead_id"], unique=False)
    op.create_index(
        op.f("ix_stg_lead_actions_source_id"),
        "stg_lead_actions",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_lead_actions_ingestion_id"),
        "stg_lead_actions",
        ["ingestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_lead_actions_lineage_ref_id"),
        "stg_lead_actions",
        ["lineage_ref_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stg_lead_actions_action_norm"),
        "stg_lead_actions",
        ["action_norm"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stg_lead_actions_action_norm"), table_name="stg_lead_actions")
    op.drop_index(op.f("ix_stg_lead_actions_lineage_ref_id"), table_name="stg_lead_actions")
    op.drop_index(op.f("ix_stg_lead_actions_ingestion_id"), table_name="stg_lead_actions")
    op.drop_index(op.f("ix_stg_lead_actions_source_id"), table_name="stg_lead_actions")
    op.drop_index(op.f("ix_stg_lead_actions_lead_id"), table_name="stg_lead_actions")
    op.drop_table("stg_lead_actions")

    op.drop_index(op.f("ix_stg_leads_cpf_promotor_hash"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_person_key_hash"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_email_hash"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_cpf_hash"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_sheet_name"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_lineage_ref_id"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_ingestion_id"), table_name="stg_leads")
    op.drop_index(op.f("ix_stg_leads_source_id"), table_name="stg_leads")
    op.drop_table("stg_leads")

