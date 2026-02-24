"""Add publicidade import tables, import_alias and evento.external_project_code.

Revision ID: c6a2d9f1b4e7
Revises: b4f6c8d0e2a1
Create Date: 2026-02-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c6a2d9f1b4e7"
down_revision = "b4f6c8d0e2a1"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return bool(_inspector().has_table(table_name))


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    columns = {column["name"] for column in _inspector().get_columns(table_name)}
    return column_name in columns


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    indexes = {index["name"] for index in _inspector().get_indexes(table_name)}
    return index_name in indexes


def upgrade() -> None:
    if _table_exists("evento") and not _column_exists("evento", "external_project_code"):
        op.add_column("evento", sa.Column("external_project_code", sa.String(length=120), nullable=True))
    if _table_exists("evento") and not _index_exists("evento", "ix_evento_external_project_code"):
        op.create_index("ix_evento_external_project_code", "evento", ["external_project_code"], unique=False)

    if not _table_exists("publicity_import_staging"):
        op.create_table(
            "publicity_import_staging",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("source_file", sa.String(length=260), nullable=False),
            sa.Column("source_row_hash", sa.String(length=64), nullable=False),
            sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("codigo_projeto", sa.String(length=120), nullable=False),
            sa.Column("projeto", sa.String(length=200), nullable=False),
            sa.Column("data_vinculacao", sa.Date(), nullable=False),
            sa.Column("meio", sa.String(length=120), nullable=False),
            sa.Column("veiculo", sa.String(length=160), nullable=False),
            sa.Column("uf", sa.String(length=8), nullable=False),
            sa.Column("uf_extenso", sa.String(length=80), nullable=True),
            sa.Column("municipio", sa.String(length=160), nullable=True),
            sa.Column("camada", sa.String(length=120), nullable=False),
            sa.Column("normalized_payload", sa.Text(), nullable=True),
            sa.UniqueConstraint(
                "source_file",
                "source_row_hash",
                name="uq_publicity_import_staging_file_hash",
            ),
        )
    if _table_exists("publicity_import_staging"):
        if not _index_exists("publicity_import_staging", "ix_publicity_import_staging_source_file"):
            op.create_index(
                "ix_publicity_import_staging_source_file",
                "publicity_import_staging",
                ["source_file"],
                unique=False,
            )
        if not _index_exists("publicity_import_staging", "ix_publicity_import_staging_source_row_hash"):
            op.create_index(
                "ix_publicity_import_staging_source_row_hash",
                "publicity_import_staging",
                ["source_row_hash"],
                unique=False,
            )
        if not _index_exists("publicity_import_staging", "ix_publicity_import_staging_imported_at"):
            op.create_index(
                "ix_publicity_import_staging_imported_at",
                "publicity_import_staging",
                ["imported_at"],
                unique=False,
            )

    if not _table_exists("event_publicity"):
        op.create_table(
            "event_publicity",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("event_id", sa.Integer(), nullable=True),
            sa.Column("publicity_project_code", sa.String(length=120), nullable=False),
            sa.Column("publicity_project_name", sa.String(length=200), nullable=False),
            sa.Column("linked_at", sa.Date(), nullable=False),
            sa.Column("medium", sa.String(length=120), nullable=False),
            sa.Column("vehicle", sa.String(length=160), nullable=False),
            sa.Column("uf", sa.String(length=8), nullable=False),
            sa.Column("uf_name", sa.String(length=80), nullable=True),
            sa.Column("municipality", sa.String(length=160), nullable=True),
            sa.Column("layer", sa.String(length=120), nullable=False),
            sa.Column("source_file", sa.String(length=260), nullable=True),
            sa.Column("source_row_hash", sa.String(length=64), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["event_id"], ["evento.id"]),
            sa.UniqueConstraint(
                "publicity_project_code",
                "linked_at",
                "medium",
                "vehicle",
                "uf",
                "layer",
                name="uq_event_publicity_natural_key",
            ),
        )
    if _table_exists("event_publicity"):
        if not _index_exists("event_publicity", "ix_event_publicity_event_id"):
            op.create_index("ix_event_publicity_event_id", "event_publicity", ["event_id"], unique=False)
        if not _index_exists("event_publicity", "ix_event_publicity_linked_at"):
            op.create_index("ix_event_publicity_linked_at", "event_publicity", ["linked_at"], unique=False)

    if not _table_exists("import_alias"):
        op.create_table(
            "import_alias",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("domain", sa.String(length=64), nullable=False),
            sa.Column("field_name", sa.String(length=80), nullable=False),
            sa.Column("source_value", sa.String(length=255), nullable=False),
            sa.Column("source_normalized", sa.String(length=255), nullable=False),
            sa.Column("canonical_value", sa.String(length=255), nullable=True),
            sa.Column("canonical_ref_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint(
                "domain",
                "field_name",
                "source_normalized",
                name="uq_import_alias_domain_field_source",
            ),
        )
    if _table_exists("import_alias"):
        if not _index_exists("import_alias", "ix_import_alias_canonical_ref_id"):
            op.create_index("ix_import_alias_canonical_ref_id", "import_alias", ["canonical_ref_id"], unique=False)


def downgrade() -> None:
    # Politica nao-destrutiva deste rollout: sem DROP/DOWNGRADE destrutivo automatico.
    pass
