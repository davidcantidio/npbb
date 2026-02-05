"""Add status_aprovacao to usuario.

Revision ID: 5f2b8c9a1d4e
Revises: 061885ae3a38
Create Date: 2026-02-04
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5f2b8c9a1d4e"
down_revision = "061885ae3a38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuario", sa.Column("status_aprovacao", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("usuario", "status_aprovacao")
