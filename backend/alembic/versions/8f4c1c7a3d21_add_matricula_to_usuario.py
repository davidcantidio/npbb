"""Add matricula to usuario.

Revision ID: 8f4c1c7a3d21
Revises: 6250e180a2f0
Create Date: 2025-12-15
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f4c1c7a3d21"
down_revision = "6250e180a2f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuario", sa.Column("matricula", sa.String(length=20), nullable=True))
    op.create_unique_constraint("uq_usuario_matricula", "usuario", ["matricula"])


def downgrade() -> None:
    op.drop_constraint("uq_usuario_matricula", "usuario", type_="unique")
    op.drop_column("usuario", "matricula")
