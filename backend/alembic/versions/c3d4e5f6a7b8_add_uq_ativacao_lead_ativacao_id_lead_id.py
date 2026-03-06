"""add_uq_ativacao_lead_ativacao_id_lead_id

Deduplicates existing rows in ativacao_lead and adds a unique constraint on
(ativacao_id, lead_id) to avoid duplicated links under concurrent submits.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-06
"""

from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep one canonical row per (ativacao_id, lead_id):
    # 1) completed=True first
    # 2) most recent completed_at
    # 3) lowest id (stable tie-breaker)
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY ativacao_id, lead_id
                    ORDER BY
                        CASE WHEN COALESCE(gamificacao_completed, false) THEN 1 ELSE 0 END DESC,
                        CASE WHEN gamificacao_completed_at IS NULL THEN 1 ELSE 0 END ASC,
                        gamificacao_completed_at DESC,
                        id ASC
                ) AS rn
            FROM ativacao_lead
        )
        DELETE FROM ativacao_lead
        WHERE id IN (
            SELECT id FROM ranked WHERE rn > 1
        )
        """
    )

    op.create_unique_constraint(
        "uq_ativacao_lead_ativacao_id_lead_id",
        "ativacao_lead",
        ["ativacao_id", "lead_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_ativacao_lead_ativacao_id_lead_id",
        "ativacao_lead",
        type_="unique",
    )
