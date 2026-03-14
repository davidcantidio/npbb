"""Alter evento.qr_code_url to Text for data URL storage.

Revision ID: a7b8c9d0e1f2
Revises: c5a8d2e1f4b6
Create Date: 2026-03-14 00:00:00.000000

O QR code real em data URL excede 500 caracteres. A coluna precisa ser Text.
"""

from alembic import op
import sqlalchemy as sa


revision = "a7b8c9d0e1f2"
down_revision = "c5a8d2e1f4b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "evento",
        "qr_code_url",
        existing_type=sa.String(500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "evento",
        "qr_code_url",
        existing_type=sa.Text(),
        type_=sa.String(500),
        existing_nullable=True,
    )
