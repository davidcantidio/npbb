"""Optimize indexes for scalable leads listing.

Revision ID: b3c4d5e6f7a8
Revises: 8b6f4c2d9a1e
Create Date: 2026-04-20
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "b3c4d5e6f7a8"
down_revision = "8b6f4c2d9a1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_lead_nome", "lead", ["nome"], unique=False)
    op.create_index("ix_lead_email", "lead", ["email"], unique=False)
    op.create_index("ix_lead_cpf", "lead", ["cpf"], unique=False)
    op.create_index("ix_evento_nome", "evento", ["nome"], unique=False)
    op.create_index("ix_evento_data_inicio_prevista", "evento", ["data_inicio_prevista"], unique=False)
    op.create_index(
        "ix_lead_conversao_lead_id_id",
        "lead_conversao",
        ["lead_id", "id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_evento_lead_id_updated_created_id",
        "lead_evento",
        ["lead_id", "updated_at", "created_at", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_evento_lead_id_updated_created_id", table_name="lead_evento")
    op.drop_index("ix_lead_conversao_lead_id_id", table_name="lead_conversao")
    op.drop_index("ix_evento_data_inicio_prevista", table_name="evento")
    op.drop_index("ix_evento_nome", table_name="evento")
    op.drop_index("ix_lead_cpf", table_name="lead")
    op.drop_index("ix_lead_email", table_name="lead")
    op.drop_index("ix_lead_nome", table_name="lead")
