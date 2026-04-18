"""ensure mandatory BB activation per event

Revision ID: fa1b2c3d4e5f
Revises: e7f8a9b0c1d2
Create Date: 2026-04-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "fa1b2c3d4e5f"
down_revision = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


def repair_bb_activations(bind: sa.engine.Connection) -> None:
    insp = sa.inspect(bind)
    if not insp.has_table("evento") or not insp.has_table("ativacao"):
        return

    bind.execute(
        sa.text(
            """
            WITH ranked AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY evento_id
                        ORDER BY id
                    ) AS rn
                FROM ativacao
                WHERE UPPER(TRIM(COALESCE(nome, ''))) = 'BB'
            )
            UPDATE ativacao
            SET nome = 'BB (legado ' || CAST(id AS TEXT) || ')'
            WHERE id IN (
                SELECT id FROM ranked WHERE rn > 1
            )
            """
        )
    )

    bind.execute(
        sa.text(
            """
            WITH ranked AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY evento_id
                        ORDER BY id
                    ) AS rn
                FROM ativacao
                WHERE UPPER(TRIM(COALESCE(nome, ''))) = 'BB'
            )
            UPDATE ativacao
            SET nome = 'BB'
            WHERE id IN (
                SELECT id FROM ranked WHERE rn = 1
            )
            """
        )
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO ativacao (
                nome,
                descricao,
                evento_id,
                gamificacao_id,
                landing_url,
                qr_code_url,
                url_promotor,
                valor,
                mensagem_qrcode,
                redireciona_pesquisa,
                checkin_unico,
                termo_uso,
                gera_cupom,
                created_at,
                updated_at
            )
            SELECT
                'BB',
                NULL,
                evento.id,
                NULL,
                NULL,
                NULL,
                NULL,
                0.00,
                NULL,
                FALSE,
                FALSE,
                FALSE,
                FALSE,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            FROM evento
            WHERE NOT EXISTS (
                SELECT 1
                FROM ativacao
                WHERE ativacao.evento_id = evento.id
                  AND UPPER(TRIM(COALESCE(ativacao.nome, ''))) = 'BB'
            )
            """
        )
    )


def upgrade() -> None:
    repair_bb_activations(op.get_bind())


def downgrade() -> None:
    # Data migration irreversivel: nao desfaz inserts/normalizacoes/renomeacoes.
    pass
