"""Add lead_evento table to Alembic history (ISSUE-F1-01-002).

Revision ID: 20260317_add_lead_evento
Revises: a7b8c9d0e1f2
Create Date: 2026-03-17

The table already exists (created via metadata.create_all or prior migration).
This migration is for versioning and traceability only.

O ficheiro usa prefixo alfabético (a20260317_...) para o module_id gerado pelo
Alembic não começar por dígito (evita falhas em alguns ambientes Linux).
"""

revision = "20260317_add_lead_evento"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
