"""Add landing page phase 1 fields to evento and ativacao.

Revision ID: 6d5f4c3b2a10
Revises: f3a1b2c4d5e6
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa


revision = "6d5f4c3b2a10"
down_revision = "f3a1b2c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("evento", sa.Column("template_override", sa.String(length=50), nullable=True))
    op.add_column("evento", sa.Column("hero_image_url", sa.Text(), nullable=True))
    op.add_column("evento", sa.Column("cta_personalizado", sa.String(length=200), nullable=True))
    op.add_column("evento", sa.Column("descricao_curta", sa.String(length=500), nullable=True))

    op.add_column("ativacao", sa.Column("landing_url", sa.String(length=500), nullable=True))
    op.add_column("ativacao", sa.Column("qr_code_url", sa.Text(), nullable=True))
    op.add_column("ativacao", sa.Column("url_promotor", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("ativacao", "url_promotor")
    op.drop_column("ativacao", "qr_code_url")
    op.drop_column("ativacao", "landing_url")

    op.drop_column("evento", "descricao_curta")
    op.drop_column("evento", "cta_personalizado")
    op.drop_column("evento", "hero_image_url")
    op.drop_column("evento", "template_override")
