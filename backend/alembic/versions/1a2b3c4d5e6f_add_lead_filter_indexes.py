"""Add indexes for lead dashboard filters.

Revision ID: 1a2b3c4d5e6f
Revises: 9b1c2d3e4f5a
Create Date: 2026-02-04
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "1a2b3c4d5e6f"
down_revision = "9b1c2d3e4f5a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_lead_data_criacao", "lead", ["data_criacao"])
    op.create_index("ix_evento_estado", "evento", ["estado"])
    op.create_index("ix_evento_cidade", "evento", ["cidade"])
    op.create_index("ix_ativacao_lead_lead_id", "ativacao_lead", ["lead_id"])


def downgrade() -> None:
    op.drop_index("ix_ativacao_lead_lead_id", table_name="ativacao_lead")
    op.drop_index("ix_evento_cidade", table_name="evento")
    op.drop_index("ix_evento_estado", table_name="evento")
    op.drop_index("ix_lead_data_criacao", table_name="lead")
