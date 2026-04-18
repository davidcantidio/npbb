"""Lead ticketing dedupe: functional unique index (NULL-safe).

Revision ID: a1c9e8f7d6b5
Revises: fb2c3d4e5f6a
Create Date: 2026-04-18

Replaces uq_lead_ticketing_dedupe (email, cpf, evento_nome, sessao) which in
PostgreSQL does not treat NULL like the application dedupe key. The new partial
unique index applies only when CPF is non-empty after TRIM.

Before upgrading production, deduplicate rows that would violate the new index;
see auditoria/handoff-task3.md.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "a1c9e8f7d6b5"
down_revision = "fb2c3d4e5f6a"
branch_labels = None
depends_on = None

_NEW_INDEX = "uq_lead_ticketing_dedupe_norm"
_OLD_UQ = "uq_lead_ticketing_dedupe"


def upgrade() -> None:
    bind = op.get_bind()
    op.drop_constraint(_OLD_UQ, "lead", type_="unique", if_exists=True)
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                f"""
                CREATE UNIQUE INDEX {_NEW_INDEX}
                ON lead (
                    (COALESCE(TRIM(email), '')),
                    cpf,
                    (COALESCE(TRIM(evento_nome), '')),
                    (COALESCE(TRIM(sessao), ''))
                )
                WHERE NULLIF(TRIM(cpf), '') IS NOT NULL
                """
            )
        )
    else:
        # SQLite (tests / local alembic): expression index + partial predicate
        op.execute(
            sa.text(
                f"""
                CREATE UNIQUE INDEX {_NEW_INDEX}
                ON lead (
                    COALESCE(TRIM(email), ''),
                    cpf,
                    COALESCE(TRIM(evento_nome), ''),
                    COALESCE(TRIM(sessao), '')
                )
                WHERE NULLIF(TRIM(cpf), '') IS NOT NULL
                """
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text(f"DROP INDEX IF EXISTS {_NEW_INDEX}"))
    else:
        op.execute(sa.text(f"DROP INDEX IF EXISTS {_NEW_INDEX}"))
    op.create_unique_constraint(
        _OLD_UQ,
        "lead",
        ["email", "cpf", "evento_nome", "sessao"],
    )
