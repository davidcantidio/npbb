"""Make gamificacao required fields and align lengths.

Revision ID: a3f9c1e27b4d
Revises: 39a29b379b54
Create Date: 2025-12-23
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3f9c1e27b4d"
down_revision = "39a29b379b54"
branch_labels = None
depends_on = None


def upgrade():
    # Trunca textos para caberem no novo limite (MVP: 240).
    op.execute(
        "UPDATE gamificacao SET descricao = SUBSTR(descricao, 1, 240) "
        "WHERE descricao IS NOT NULL AND LENGTH(descricao) > 240"
    )
    op.execute(
        "UPDATE gamificacao SET texto_feedback = SUBSTR(texto_feedback, 1, 240) "
        "WHERE texto_feedback IS NOT NULL AND LENGTH(texto_feedback) > 240"
    )

    # Preenche nulos antes de aplicar NOT NULL.
    op.execute("UPDATE gamificacao SET premio = '' WHERE premio IS NULL")
    op.execute("UPDATE gamificacao SET titulo_feedback = '' WHERE titulo_feedback IS NULL")
    op.execute("UPDATE gamificacao SET texto_feedback = '' WHERE texto_feedback IS NULL")

    with op.batch_alter_table("gamificacao") as batch_op:
        batch_op.alter_column(
            "descricao",
            existing_type=sa.String(length=500),
            type_=sa.String(length=240),
            nullable=False,
        )
        batch_op.alter_column(
            "texto_feedback",
            existing_type=sa.String(length=500),
            type_=sa.String(length=240),
            nullable=False,
        )
        batch_op.alter_column(
            "premio",
            existing_type=sa.String(length=200),
            nullable=False,
        )
        batch_op.alter_column(
            "titulo_feedback",
            existing_type=sa.String(length=200),
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table("gamificacao") as batch_op:
        batch_op.alter_column(
            "descricao",
            existing_type=sa.String(length=240),
            type_=sa.String(length=500),
            nullable=False,
        )
        batch_op.alter_column(
            "texto_feedback",
            existing_type=sa.String(length=240),
            type_=sa.String(length=500),
            nullable=True,
        )
        batch_op.alter_column(
            "premio",
            existing_type=sa.String(length=200),
            nullable=True,
        )
        batch_op.alter_column(
            "titulo_feedback",
            existing_type=sa.String(length=200),
            nullable=True,
        )

