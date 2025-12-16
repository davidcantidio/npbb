"""Add password reset tokens.

Revision ID: c1b4e0a9d2f7
Revises: 8f4c1c7a3d21
Create Date: 2025-12-16
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1b4e0a9d2f7"
down_revision = "8f4c1c7a3d21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset_token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uq_password_reset_token_hash",
        "password_reset_token",
        ["token_hash"],
    )
    op.create_index(
        "ix_password_reset_token_usuario_id",
        "password_reset_token",
        ["usuario_id"],
        unique=False,
    )
    op.create_index(
        "ix_password_reset_token_token_hash",
        "password_reset_token",
        ["token_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_token_token_hash", table_name="password_reset_token")
    op.drop_index("ix_password_reset_token_usuario_id", table_name="password_reset_token")
    op.drop_constraint(
        "uq_password_reset_token_hash",
        "password_reset_token",
        type_="unique",
    )
    op.drop_table("password_reset_token")

