"""Add canonical fact schema for audience ruler separation.

Revision ID: 9e7a4c2d1b6f
Revises: 6b1d4e9f2a3c
Create Date: 2026-02-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9e7a4c2d1b6f"
down_revision = "6b1d4e9f2a3c"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    """Return whether one table exists in current schema."""

    return table_name in set(inspector.get_table_names())


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    """Return whether one column exists in target table."""

    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    """Return whether one index exists in target table."""

    return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


def _fk_name_exists(inspector: sa.Inspector, table_name: str, fk_name: str) -> bool:
    """Return whether one foreign key name exists in target table."""

    return fk_name in {fk.get("name") for fk in inspector.get_foreign_keys(table_name)}


def _fk_target_exists(
    inspector: sa.Inspector,
    table_name: str,
    referred_table: str,
    constrained_columns: list[str],
    referred_columns: list[str],
) -> bool:
    """Return whether FK target already exists regardless of FK name."""

    for fk in inspector.get_foreign_keys(table_name):
        if fk.get("referred_table") != referred_table:
            continue
        if list(fk.get("constrained_columns") or []) != constrained_columns:
            continue
        if list(fk.get("referred_columns") or []) != referred_columns:
            continue
        return True
    return False


def _ensure_column(
    table_name: str,
    column_name: str,
    column_type: sa.types.TypeEngine,
    *,
    nullable: bool = True,
) -> None:
    """Add one column to target table when absent."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not _column_exists(inspector, table_name, column_name):
        op.add_column(table_name, sa.Column(column_name, column_type, nullable=nullable))


def _ensure_index(table_name: str, index_name: str, columns: list[str]) -> None:
    """Create index in target table when absent."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not _index_exists(inspector, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def _ensure_foreign_key(
    table_name: str,
    fk_name: str,
    referred_table: str,
    constrained_columns: list[str],
    referred_columns: list[str],
) -> None:
    """Create foreign key when target is absent."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _fk_name_exists(inspector, table_name, fk_name):
        return
    if _fk_target_exists(
        inspector,
        table_name,
        referred_table,
        constrained_columns,
        referred_columns,
    ):
        return
    op.create_foreign_key(
        fk_name,
        table_name,
        referred_table,
        constrained_columns,
        referred_columns,
    )


def _create_attendance_table() -> None:
    """Create canonical attendance fact table when absent."""

    op.create_table(
        "attendance_access_control",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("ingressos_validos", sa.Integer(), nullable=True),
        sa.Column("presentes", sa.Integer(), nullable=True),
        sa.Column("ausentes", sa.Integer(), nullable=True),
        sa.Column("invalidos", sa.Integer(), nullable=True),
        sa.Column("bloqueados", sa.Integer(), nullable=True),
        sa.Column("comparecimento_pct", sa.Numeric(7, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
    )


def _create_ticket_sales_table() -> None:
    """Create canonical ticket-sales fact table when absent."""

    op.create_table(
        "ticket_sales",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("sold_total", sa.Integer(), nullable=True),
        sa.Column("refunded_total", sa.Integer(), nullable=True),
        sa.Column("net_sold_total", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
    )


def _create_optin_transactions_table() -> None:
    """Create canonical opt-in fact table when absent."""

    op.create_table(
        "optin_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("purchase_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("optin_flag", sa.Boolean(), nullable=True),
        sa.Column("optin_status", sa.String(length=80), nullable=True),
        sa.Column("qty", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestions.id"]),
        sa.ForeignKeyConstraint(["lineage_ref_id"], ["lineage_refs.id"]),
    )


def _ensure_attendance_schema() -> None:
    """Ensure attendance fact table has minimum canonical columns and links."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "attendance_access_control"

    if not _table_exists(inspector, table_name):
        _create_attendance_table()
    else:
        _ensure_column(table_name, "session_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "source_id", sa.String(length=160), nullable=True)
        _ensure_column(table_name, "ingestion_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "lineage_ref_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "ingressos_validos", sa.Integer(), nullable=True)
        _ensure_column(table_name, "presentes", sa.Integer(), nullable=True)
        _ensure_column(table_name, "ausentes", sa.Integer(), nullable=True)
        _ensure_column(table_name, "invalidos", sa.Integer(), nullable=True)
        _ensure_column(table_name, "bloqueados", sa.Integer(), nullable=True)

    _ensure_index(table_name, "ix_attendance_access_control_session_id", ["session_id"])
    _ensure_index(table_name, "ix_attendance_access_control_ingestion_id", ["ingestion_id"])
    _ensure_index(table_name, "ix_attendance_access_control_lineage_ref_id", ["lineage_ref_id"])

    _ensure_foreign_key(
        table_name,
        "fk_attendance_access_control_session_id_event_sessions",
        "event_sessions",
        ["session_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_attendance_access_control_ingestion_id_ingestions",
        "ingestions",
        ["ingestion_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_attendance_access_control_lineage_ref_id_lineage_refs",
        "lineage_refs",
        ["lineage_ref_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_attendance_access_control_source_id_sources",
        "sources",
        ["source_id"],
        ["source_id"],
    )


def _ensure_ticket_sales_schema() -> None:
    """Ensure ticket-sales fact table has minimum canonical columns and links."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "ticket_sales"

    if not _table_exists(inspector, table_name):
        _create_ticket_sales_table()
    else:
        _ensure_column(table_name, "session_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "source_id", sa.String(length=160), nullable=True)
        _ensure_column(table_name, "ingestion_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "lineage_ref_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "sold_total", sa.Integer(), nullable=True)
        _ensure_column(table_name, "refunded_total", sa.Integer(), nullable=True)
        _ensure_column(table_name, "net_sold_total", sa.Integer(), nullable=True)

    _ensure_index(table_name, "ix_ticket_sales_session_id", ["session_id"])
    _ensure_index(table_name, "ix_ticket_sales_ingestion_id", ["ingestion_id"])
    _ensure_index(table_name, "ix_ticket_sales_lineage_ref_id", ["lineage_ref_id"])

    _ensure_foreign_key(
        table_name,
        "fk_ticket_sales_session_id_event_sessions",
        "event_sessions",
        ["session_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_ticket_sales_ingestion_id_ingestions",
        "ingestions",
        ["ingestion_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_ticket_sales_lineage_ref_id_lineage_refs",
        "lineage_refs",
        ["lineage_ref_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_ticket_sales_source_id_sources",
        "sources",
        ["source_id"],
        ["source_id"],
    )


def _ensure_optin_schema() -> None:
    """Ensure opt-in fact table has minimum canonical columns and links."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "optin_transactions"

    if not _table_exists(inspector, table_name):
        _create_optin_transactions_table()
    else:
        _ensure_column(table_name, "session_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "source_id", sa.String(length=160), nullable=True)
        _ensure_column(table_name, "ingestion_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "lineage_ref_id", sa.Integer(), nullable=True)
        _ensure_column(table_name, "purchase_at", sa.DateTime(timezone=True), nullable=True)
        _ensure_column(table_name, "optin_flag", sa.Boolean(), nullable=True)
        _ensure_column(table_name, "optin_status", sa.String(length=80), nullable=True)
        _ensure_column(table_name, "qty", sa.Integer(), nullable=True)

    _ensure_index(table_name, "ix_optin_transactions_session_id", ["session_id"])
    _ensure_index(table_name, "ix_optin_transactions_ingestion_id", ["ingestion_id"])
    _ensure_index(table_name, "ix_optin_transactions_lineage_ref_id", ["lineage_ref_id"])

    _ensure_foreign_key(
        table_name,
        "fk_optin_transactions_session_id_event_sessions",
        "event_sessions",
        ["session_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_optin_transactions_ingestion_id_ingestions",
        "ingestions",
        ["ingestion_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_optin_transactions_lineage_ref_id_lineage_refs",
        "lineage_refs",
        ["lineage_ref_id"],
        ["id"],
    )
    _ensure_foreign_key(
        table_name,
        "fk_optin_transactions_source_id_sources",
        "sources",
        ["source_id"],
        ["source_id"],
    )


def upgrade() -> None:
    _ensure_attendance_schema()
    _ensure_ticket_sales_schema()
    _ensure_optin_schema()


def _drop_fk_if_exists(table_name: str, fk_name: str) -> None:
    """Drop one foreign key when present."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _fk_name_exists(inspector, table_name, fk_name):
        op.drop_constraint(fk_name, table_name, type_="foreignkey")


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    """Drop one index when present."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _index_exists(inspector, table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def _drop_column_if_exists(table_name: str, column_name: str) -> None:
    """Drop one column when present."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _column_exists(inspector, table_name, column_name):
        op.drop_column(table_name, column_name)


def downgrade() -> None:
    _drop_fk_if_exists(
        "optin_transactions",
        "fk_optin_transactions_lineage_ref_id_lineage_refs",
    )
    _drop_fk_if_exists(
        "ticket_sales",
        "fk_ticket_sales_lineage_ref_id_lineage_refs",
    )
    _drop_fk_if_exists(
        "attendance_access_control",
        "fk_attendance_access_control_lineage_ref_id_lineage_refs",
    )

    _drop_index_if_exists("optin_transactions", "ix_optin_transactions_lineage_ref_id")
    _drop_index_if_exists("ticket_sales", "ix_ticket_sales_lineage_ref_id")
    _drop_index_if_exists("attendance_access_control", "ix_attendance_access_control_lineage_ref_id")

    _drop_column_if_exists("optin_transactions", "qty")
    _drop_column_if_exists("optin_transactions", "optin_status")
    _drop_column_if_exists("optin_transactions", "optin_flag")
    _drop_column_if_exists("optin_transactions", "lineage_ref_id")

    _drop_column_if_exists("ticket_sales", "lineage_ref_id")
    _drop_column_if_exists("attendance_access_control", "lineage_ref_id")

