"""Make ativacao.descricao optional and align length to 240 (MVP).

Revision ID: 061885ae3a38
Revises: b7c2d5f9a8e1
Create Date: 2026-01-05
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "061885ae3a38"
down_revision = "b7c2d5f9a8e1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("ativacao") as batch_op:
        batch_op.alter_column(
            "descricao",
            existing_type=sa.String(length=200),
            type_=sa.String(length=240),
            nullable=True,
        )


def downgrade():
    # Preenche nulos antes de aplicar NOT NULL.
    op.execute("UPDATE ativacao SET descricao = '' WHERE descricao IS NULL")
    # Trunca textos para caberem no limite anterior.
    op.execute("UPDATE ativacao SET descricao = SUBSTR(descricao, 1, 200) WHERE LENGTH(descricao) > 200")

    with op.batch_alter_table("ativacao") as batch_op:
        batch_op.alter_column(
            "descricao",
            existing_type=sa.String(length=240),
            type_=sa.String(length=200),
            nullable=False,
        )

