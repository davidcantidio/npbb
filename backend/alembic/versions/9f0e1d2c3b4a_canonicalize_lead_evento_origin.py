"""canonicalize lead_evento origin for proponente vs ativacao

Revision ID: 9f0e1d2c3b4a
Revises: 4c7a9d2e1f3b
Create Date: 2026-04-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "9f0e1d2c3b4a"
down_revision = "8d4e6f1a2b3c"
branch_labels = None
depends_on = None

_CANONICAL_SOURCE_KIND_VALUES = (
    "ativacao",
    "event_id_direct",
    "lead_batch",
    "evento_nome_backfill",
    "manual_reconciled",
)
_LEGACY_TO_CANONICAL_SOURCE_KIND = {
    "ACTIVATION": "ativacao",
    "EVENT_DIRECT": "event_id_direct",
    "LEAD_BATCH": "lead_batch",
    "EVENT_NAME_BACKFILL": "evento_nome_backfill",
    "MANUAL_RECONCILED": "manual_reconciled",
}

_TIPO_LEAD_VALUES = ("bilheteria", "entrada_evento", "ativacao")
_TIPO_RESPONSAVEL_VALUES = ("proponente", "agencia")


def _has_named_object(existing_names: set[str | None], expected_name: str) -> bool:
    return any(
        name is not None and (name == expected_name or str(name).endswith(expected_name))
        for name in existing_names
    )


def _tipo_lead_type(bind: sa.engine.Connection) -> sa.types.TypeEngine:
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(*_TIPO_LEAD_VALUES, name="tipolead", create_type=False)
    return sa.Enum(*_TIPO_LEAD_VALUES, name="tipolead")


def _tipo_responsavel_type(bind: sa.engine.Connection) -> sa.types.TypeEngine:
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(*_TIPO_RESPONSAVEL_VALUES, name="tiporesponsavel", create_type=False)
    return sa.Enum(*_TIPO_RESPONSAVEL_VALUES, name="tiporesponsavel")


def _create_origin_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tipolead AS ENUM "
            "('bilheteria', 'entrada_evento', 'ativacao'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tiporesponsavel AS ENUM "
            "('proponente', 'agencia'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )


def _normalize_source_kind_enum_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    enum_labels = bind.execute(
        sa.text(
            """
            SELECT enumlabel
            FROM pg_enum e
            JOIN pg_type t ON t.oid = e.enumtypid
            WHERE t.typname = 'leadeventosourcekind'
            ORDER BY e.enumsortorder
            """
        )
    ).scalars().all()
    if not enum_labels or tuple(enum_labels) == _CANONICAL_SOURCE_KIND_VALUES:
        return

    known_values = set(_CANONICAL_SOURCE_KIND_VALUES) | set(_LEGACY_TO_CANONICAL_SOURCE_KIND)
    unexpected_values = sorted(set(enum_labels) - known_values)
    if unexpected_values:
        raise RuntimeError(
            "Valores inesperados em leadeventosourcekind: "
            + ", ".join(unexpected_values)
        )

    op.execute("ALTER TYPE leadeventosourcekind RENAME TO leadeventosourcekind_legacy")
    op.execute(
        """
        CREATE TYPE leadeventosourcekind AS ENUM (
            'ativacao',
            'event_id_direct',
            'lead_batch',
            'evento_nome_backfill',
            'manual_reconciled'
        )
        """
    )
    op.execute(
        """
        ALTER TABLE lead_evento
        ALTER COLUMN source_kind TYPE leadeventosourcekind
        USING (
            CASE CAST(source_kind AS TEXT)
                WHEN 'ACTIVATION' THEN 'ativacao'
                WHEN 'EVENT_DIRECT' THEN 'event_id_direct'
                WHEN 'LEAD_BATCH' THEN 'lead_batch'
                WHEN 'EVENT_NAME_BACKFILL' THEN 'evento_nome_backfill'
                WHEN 'MANUAL_RECONCILED' THEN 'manual_reconciled'
                WHEN 'ativacao' THEN 'ativacao'
                WHEN 'event_id_direct' THEN 'event_id_direct'
                WHEN 'lead_batch' THEN 'lead_batch'
                WHEN 'evento_nome_backfill' THEN 'evento_nome_backfill'
                WHEN 'manual_reconciled' THEN 'manual_reconciled'
            END
        )::leadeventosourcekind
        """
    )
    op.execute("DROP TYPE leadeventosourcekind_legacy")


def _ensure_origin_columns() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    lead_columns = {col["name"] for col in insp.get_columns("lead_evento")}
    lead_foreign_keys = {fk.get("name") for fk in insp.get_foreign_keys("lead_evento")}

    with op.batch_alter_table("lead_evento") as batch_op:
        if "tipo_lead" not in lead_columns:
            batch_op.add_column(sa.Column("tipo_lead", _tipo_lead_type(bind), nullable=True))
        if "responsavel_tipo" not in lead_columns:
            batch_op.add_column(
                sa.Column("responsavel_tipo", _tipo_responsavel_type(bind), nullable=True)
            )
        if "responsavel_nome" not in lead_columns:
            batch_op.add_column(sa.Column("responsavel_nome", sa.String(length=150), nullable=True))
        if "responsavel_agencia_id" not in lead_columns:
            batch_op.add_column(sa.Column("responsavel_agencia_id", sa.Integer(), nullable=True))
        if not _has_named_object(
            lead_foreign_keys,
            "fk_lead_evento_responsavel_agencia_id_agencia",
        ):
            batch_op.create_foreign_key(
                "fk_lead_evento_responsavel_agencia_id_agencia",
                "agencia",
                ["responsavel_agencia_id"],
                ["id"],
            )

    ativacao_columns = {col["name"] for col in insp.get_columns("ativacao_lead")}
    ativacao_checks = {check.get("name") for check in insp.get_check_constraints("ativacao_lead")}
    with op.batch_alter_table("ativacao_lead") as batch_op:
        if "nome_ativacao" not in ativacao_columns:
            batch_op.add_column(sa.Column("nome_ativacao", sa.String(length=150), nullable=True))
        if not _has_named_object(
            ativacao_checks,
            "ck_ativacao_lead_nome_ativacao_not_blank",
        ):
            batch_op.create_check_constraint(
                "ck_ativacao_lead_nome_ativacao_not_blank",
                "nome_ativacao IS NULL OR length(trim(nome_ativacao)) > 0",
            )


def _ensure_origin_indexes_and_checks() -> None:
    insp = sa.inspect(op.get_bind())
    lead_indexes = {index.get("name") for index in insp.get_indexes("lead_evento")}
    lead_checks = {check.get("name") for check in insp.get_check_constraints("lead_evento")}

    with op.batch_alter_table("lead_evento") as batch_op:
        if not _has_named_object(lead_indexes, "ix_lead_evento_lead_evento_tipo_lead"):
            batch_op.create_index(
                "ix_lead_evento_lead_evento_tipo_lead",
                ["tipo_lead"],
                unique=False,
            )
        if not _has_named_object(
            lead_indexes,
            "ix_lead_evento_lead_evento_responsavel_tipo",
        ):
            batch_op.create_index(
                "ix_lead_evento_lead_evento_responsavel_tipo",
                ["responsavel_tipo"],
                unique=False,
            )
        if not _has_named_object(
            lead_indexes,
            "ix_lead_evento_lead_evento_responsavel_agencia_id",
        ):
            batch_op.create_index(
                "ix_lead_evento_lead_evento_responsavel_agencia_id",
                ["responsavel_agencia_id"],
                unique=False,
            )
        if not _has_named_object(
            lead_checks,
            "ck_lead_evento_tipo_lead_ativacao_agencia",
        ):
            batch_op.create_check_constraint(
                "ck_lead_evento_tipo_lead_ativacao_agencia",
                "tipo_lead IS NULL OR tipo_lead != 'ativacao' OR "
                "(responsavel_tipo IS NOT NULL AND responsavel_tipo = 'agencia')",
            )
        if not _has_named_object(
            lead_checks,
            "ck_lead_evento_tipo_lead_proponente",
        ):
            batch_op.create_check_constraint(
                "ck_lead_evento_tipo_lead_proponente",
                "tipo_lead IS NULL OR tipo_lead NOT IN ('entrada_evento', 'bilheteria') OR "
                "(responsavel_tipo IS NOT NULL AND responsavel_tipo = 'proponente')",
            )
        if not _has_named_object(
            lead_checks,
            "ck_lead_evento_source_kind_ativacao_requires_tipo_lead",
        ):
            batch_op.create_check_constraint(
                "ck_lead_evento_source_kind_ativacao_requires_tipo_lead",
                "source_kind != 'ativacao' OR tipo_lead = 'ativacao'",
            )
        if not _has_named_object(
            lead_checks,
            "ck_lead_evento_responsavel_nome_required",
        ):
            batch_op.create_check_constraint(
                "ck_lead_evento_responsavel_nome_required",
                "responsavel_tipo IS NULL OR "
                "(responsavel_nome IS NOT NULL AND length(trim(responsavel_nome)) > 0)",
            )
        if not _has_named_object(
            lead_checks,
            "ck_lead_evento_responsavel_agencia_consistency",
        ):
            batch_op.create_check_constraint(
                "ck_lead_evento_responsavel_agencia_consistency",
                "responsavel_tipo IS NULL OR "
                "(responsavel_tipo = 'agencia' AND responsavel_agencia_id IS NOT NULL) OR "
                "(responsavel_tipo = 'proponente' AND responsavel_agencia_id IS NULL)",
            )


def _backfill_lead_evento_origin() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        """
        WITH activation_candidates AS (
            SELECT
                le.id AS lead_evento_id,
                al.id AS ativacao_lead_id,
                ROW_NUMBER() OVER (
                    PARTITION BY le.id
                    ORDER BY
                        CASE
                            WHEN le.source_ref_id = al.id THEN 0
                            WHEN le.source_ref_id = a.id THEN 1
                            ELSE 2
                        END,
                        al.id
                ) AS rn,
                COUNT(*) OVER (PARTITION BY le.id) AS candidate_count,
                SUM(
                    CASE
                        WHEN le.source_ref_id = al.id OR le.source_ref_id = a.id THEN 1
                        ELSE 0
                    END
                ) OVER (PARTITION BY le.id) AS source_match_count
            FROM lead_evento AS le
            JOIN ativacao_lead AS al ON al.lead_id = le.lead_id
            JOIN ativacao AS a ON a.id = al.ativacao_id
            WHERE CAST(le.source_kind AS TEXT) = 'ativacao'
              AND a.evento_id = le.evento_id
        ),
        resolved_activation AS (
            SELECT lead_evento_id, ativacao_lead_id
            FROM activation_candidates
            WHERE rn = 1
              AND (
                  source_match_count = 1
                  OR (source_match_count = 0 AND candidate_count = 1)
              )
        )
        UPDATE lead_evento AS le
        SET
            source_ref_id = resolved_activation.ativacao_lead_id,
            tipo_lead = 'ativacao',
            responsavel_tipo = 'agencia',
            responsavel_nome = ag.nome,
            responsavel_agencia_id = ev.agencia_id
        FROM resolved_activation
        JOIN evento AS ev ON ev.id = (
            SELECT evento_id FROM lead_evento WHERE id = resolved_activation.lead_evento_id
        )
        LEFT JOIN agencia AS ag ON ag.id = ev.agencia_id
        WHERE le.id = resolved_activation.lead_evento_id
        """
    )

    op.execute(
        """
        UPDATE lead_evento AS le
        SET
            tipo_lead = 'entrada_evento',
            responsavel_tipo = 'proponente',
            responsavel_nome = COALESCE(d.nome, ev.nome),
            responsavel_agencia_id = NULL
        FROM evento AS ev
        LEFT JOIN diretoria AS d ON d.id = ev.diretoria_id
        WHERE le.evento_id = ev.id
          AND CAST(le.source_kind AS TEXT) IN (
              'event_id_direct',
              'lead_batch',
              'evento_nome_backfill',
              'manual_reconciled'
          )
          AND (
              le.tipo_lead IS NULL
              OR CAST(le.tipo_lead AS TEXT) = 'entrada_evento'
          )
        """
    )

    op.execute(
        """
        UPDATE lead_evento AS le
        SET
            responsavel_tipo = 'proponente',
            responsavel_nome = COALESCE(d.nome, ev.nome),
            responsavel_agencia_id = NULL
        FROM evento AS ev
        LEFT JOIN diretoria AS d ON d.id = ev.diretoria_id
        WHERE le.evento_id = ev.id
          AND CAST(le.tipo_lead AS TEXT) = 'bilheteria'
        """
    )


def _create_postgres_triggers() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        """
        CREATE OR REPLACE FUNCTION validate_lead_evento_activation_link()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            matched_ativacao_lead_id integer;
        BEGIN
            IF CAST(NEW.source_kind AS TEXT) <> 'ativacao' THEN
                RETURN NEW;
            END IF;

            IF NEW.source_ref_id IS NULL THEN
                RAISE EXCEPTION
                    'lead_evento de ativacao exige source_ref_id com ativacao_lead.id';
            END IF;

            SELECT al.id
            INTO matched_ativacao_lead_id
            FROM ativacao_lead AS al
            JOIN ativacao AS a ON a.id = al.ativacao_id
            WHERE al.id = NEW.source_ref_id
              AND al.lead_id = NEW.lead_id
              AND a.evento_id = NEW.evento_id;

            IF matched_ativacao_lead_id IS NULL THEN
                RAISE EXCEPTION
                    'lead_evento de ativacao exige ativacao_lead compatível com lead_id=%, evento_id=% e source_ref_id=%',
                    NEW.lead_id,
                    NEW.evento_id,
                    NEW.source_ref_id;
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_lead_evento_validate_activation_link ON lead_evento;
        CREATE TRIGGER trg_lead_evento_validate_activation_link
        BEFORE INSERT OR UPDATE OF source_kind, source_ref_id, lead_id, evento_id
        ON lead_evento
        FOR EACH ROW
        EXECUTE FUNCTION validate_lead_evento_activation_link();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_ativacao_lead_delete_if_linked()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM lead_evento AS le
                WHERE CAST(le.source_kind AS TEXT) = 'ativacao'
                  AND le.source_ref_id = OLD.id
            ) THEN
                RAISE EXCEPTION
                    'Nao e permitido remover ativacao_lead % enquanto existir lead_evento de ativacao apontando para ele',
                    OLD.id;
            END IF;
            RETURN OLD;
        END;
        $$;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_ativacao_lead_prevent_delete_if_linked ON ativacao_lead;
        CREATE TRIGGER trg_ativacao_lead_prevent_delete_if_linked
        BEFORE DELETE ON ativacao_lead
        FOR EACH ROW
        EXECUTE FUNCTION prevent_ativacao_lead_delete_if_linked();
        """
    )


def _validate_canonical_state() -> None:
    bind = op.get_bind()

    invalid_activation_rows = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM lead_evento AS le
            LEFT JOIN ativacao_lead AS al ON al.id = le.source_ref_id
            LEFT JOIN ativacao AS a ON a.id = al.ativacao_id
            WHERE CAST(le.source_kind AS TEXT) = 'ativacao'
              AND (
                  le.source_ref_id IS NULL
                  OR CAST(le.tipo_lead AS TEXT) <> 'ativacao'
                  OR CAST(le.responsavel_tipo AS TEXT) <> 'agencia'
                  OR le.responsavel_agencia_id IS NULL
                  OR le.responsavel_nome IS NULL
                  OR length(trim(le.responsavel_nome)) = 0
                  OR al.id IS NULL
                  OR al.lead_id <> le.lead_id
                  OR a.id IS NULL
                  OR a.evento_id <> le.evento_id
              )
            """
        )
    ).scalar_one()

    invalid_proponente_rows = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM lead_evento AS le
            WHERE CAST(le.tipo_lead AS TEXT) IN ('entrada_evento', 'bilheteria')
              AND (
                  CAST(le.responsavel_tipo AS TEXT) <> 'proponente'
                  OR le.responsavel_agencia_id IS NOT NULL
                  OR le.responsavel_nome IS NULL
                  OR length(trim(le.responsavel_nome)) = 0
              )
            """
        )
    ).scalar_one()

    if invalid_activation_rows or invalid_proponente_rows:
        raise RuntimeError(
            "Canonicalizacao de lead_evento falhou: "
            f"invalid_activation_rows={invalid_activation_rows}, "
            f"invalid_proponente_rows={invalid_proponente_rows}"
        )


def _drop_postgres_triggers() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DROP TRIGGER IF EXISTS trg_lead_evento_validate_activation_link ON lead_evento")
    op.execute("DROP FUNCTION IF EXISTS validate_lead_evento_activation_link()")
    op.execute("DROP TRIGGER IF EXISTS trg_ativacao_lead_prevent_delete_if_linked ON ativacao_lead")
    op.execute("DROP FUNCTION IF EXISTS prevent_ativacao_lead_delete_if_linked()")


def upgrade() -> None:
    _create_origin_enums_if_postgres()
    _normalize_source_kind_enum_if_postgres()
    _ensure_origin_columns()
    _backfill_lead_evento_origin()
    _ensure_origin_indexes_and_checks()
    _create_postgres_triggers()
    _validate_canonical_state()


def downgrade() -> None:
    _drop_postgres_triggers()

    insp = sa.inspect(op.get_bind())
    lead_checks = {check.get("name") for check in insp.get_check_constraints("lead_evento")}
    ativacao_checks = {check.get("name") for check in insp.get_check_constraints("ativacao_lead")}

    with op.batch_alter_table("lead_evento") as batch_op:
        if _has_named_object(
            lead_checks,
            "ck_lead_evento_source_kind_ativacao_requires_tipo_lead",
        ):
            batch_op.drop_constraint(
                "ck_lead_evento_source_kind_ativacao_requires_tipo_lead",
                type_="check",
            )
        if _has_named_object(
            lead_checks,
            "ck_lead_evento_tipo_lead_proponente",
        ):
            batch_op.drop_constraint("ck_lead_evento_tipo_lead_proponente", type_="check")

    with op.batch_alter_table("ativacao_lead") as batch_op:
        if _has_named_object(
            ativacao_checks,
            "ck_ativacao_lead_nome_ativacao_not_blank",
        ):
            batch_op.drop_constraint("ck_ativacao_lead_nome_ativacao_not_blank", type_="check")
