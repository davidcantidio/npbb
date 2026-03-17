"""Adiciona registro da tabela lead_evento no histórico Alembic.

Revision ID: 20260317_add_lead_evento
Revises: a7b8c9d0e1f2
Create Date: 2026-03-17

Esta migration registra a tabela lead_evento (já existente no modelo
em lead_public_models.py) para satisfazer ISSUE-F1-01-002.

A tabela já foi criada via metadata.create_all() ou migration anterior.
Esta migration serve apenas para versionamento e rastreabilidade.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import context


# revision identifiers, used by Alembic.
revision = '20260317_add_lead_evento'
down_revision = 'a7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Registra que a tabela lead_evento já existe."""
    # Como a tabela já existe no banco, não executamos DDL real.
    # Isso evita erros de "table already exists" e mantém o histórico limpo.
    pass


def downgrade() -> None:
    """Não faz nada no downgrade (tabela não deve ser removida)."""
    pass
