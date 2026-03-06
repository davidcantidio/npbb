"""add_rg_and_complemento_to_lead

Adds two fields that were absent from the Lead model:
- rg: identity document number (nullable VARCHAR 30)
- complemento: address complement (nullable VARCHAR 120)

Revision ID: a1b2c3d4e5f6
Revises: 7f3c2d1b4a6e
Create Date: 2026-03-06
"""

revision = "a1b2c3d4e5f6"
down_revision = "7f3c2d1b4a6e"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.add_column("lead", sa.Column("rg", sa.String(length=30), nullable=True))
    op.add_column("lead", sa.Column("complemento", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("lead", "complemento")
    op.drop_column("lead", "rg")
