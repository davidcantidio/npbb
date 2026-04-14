"""bridge missing local revision 8d4e6f1a2b3c

Revision ID: 8d4e6f1a2b3c
Revises: 4c7a9d2e1f3b
Create Date: 2026-04-14
"""

from __future__ import annotations


revision = "8d4e6f1a2b3c"
down_revision = "4c7a9d2e1f3b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Bridge orphaned local Alembic state to the committed chain."""


def downgrade() -> None:
    """No-op downgrade for bridge revision."""
