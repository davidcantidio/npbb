"""Harden lead import storage paths, indexes, and realistic RLS.

Revision ID: 3f7b9c2d1e4a
Revises: 2f1c4e6a8b9d
Create Date: 2026-04-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "3f7b9c2d1e4a"
down_revision = "2f1c4e6a8b9d"
branch_labels = None
depends_on = None


RLS_DISABLED_TABLES = ("evento", "ativacao", "lead", "lead_evento")
RLS_ENABLED_TABLES = (
    "lead_batches",
    "leads_silver",
    "lead_import_etl_preview_session",
    "lead_import_etl_job",
    "lead_import_etl_staging",
    "lead_column_aliases",
)
LEAD_BATCHES_STORAGE_COLUMNS = (
    sa.Column("bronze_storage_bucket", sa.String(length=120), nullable=True),
    sa.Column("bronze_storage_key", sa.String(length=500), nullable=True),
    sa.Column("bronze_content_type", sa.String(length=160), nullable=True),
    sa.Column("bronze_size_bytes", sa.Integer(), nullable=True),
    sa.Column("bronze_uploaded_at", sa.DateTime(timezone=True), nullable=True),
)
ETL_JOB_STORAGE_COLUMNS = (
    sa.Column("file_storage_bucket", sa.String(length=120), nullable=True),
    sa.Column("file_storage_key", sa.String(length=500), nullable=True),
    sa.Column("file_content_type", sa.String(length=160), nullable=True),
    sa.Column("file_size_bytes", sa.Integer(), nullable=True),
    sa.Column("file_uploaded_at", sa.DateTime(timezone=True), nullable=True),
)


def _bind():
    return op.get_bind()


def _inspector():
    return sa.inspect(_bind())


def _is_postgresql() -> bool:
    return _bind().dialect.name == "postgresql"


def _table_exists(table_name: str) -> bool:
    return table_name in _inspector().get_table_names(schema="public")


def _column_exists(table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in _inspector().get_columns(table_name, schema="public"))


def _index_exists(table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in _inspector().get_indexes(table_name, schema="public"))


def _drop_policy(table_name: str, policy_name: str) -> None:
    op.execute(sa.text(f'DROP POLICY IF EXISTS "{policy_name}" ON public."{table_name}"'))


def _create_helper_functions() -> None:
    op.execute(
        sa.text(
            """
            create or replace function public.npbb_current_user_id()
            returns integer
            language sql
            stable
            set search_path = ''
            as $$
              select nullif(current_setting('app.user_id', true), '')::integer
            $$;

            create or replace function public.npbb_current_user_type()
            returns text
            language sql
            stable
            set search_path = ''
            as $$
              select nullif(lower(current_setting('app.user_type', true)), '')
            $$;

            create or replace function public.npbb_current_agencia_id()
            returns integer
            language sql
            stable
            set search_path = ''
            as $$
              select nullif(current_setting('app.agencia_id', true), '')::integer
            $$;

            create or replace function public.npbb_is_internal_user()
            returns boolean
            language sql
            stable
            set search_path = ''
            as $$
              select coalesce(public.npbb_current_user_type() in ('npbb', 'bb'), false)
            $$;
            """
        )
    )


def _drop_helper_functions() -> None:
    op.execute("drop function if exists public.npbb_is_internal_user()")
    op.execute("drop function if exists public.npbb_current_agencia_id()")
    op.execute("drop function if exists public.npbb_current_user_type()")
    op.execute("drop function if exists public.npbb_current_user_id()")


def _configure_storage_columns() -> None:
    if _table_exists("lead_batches"):
        for column in LEAD_BATCHES_STORAGE_COLUMNS:
            if not _column_exists("lead_batches", column.name):
                op.add_column("lead_batches", column)
        if _column_exists("lead_batches", "arquivo_bronze"):
            op.alter_column("lead_batches", "arquivo_bronze", existing_type=sa.LargeBinary(), nullable=True)

    if _table_exists("lead_import_etl_job"):
        for column in ETL_JOB_STORAGE_COLUMNS:
            if not _column_exists("lead_import_etl_job", column.name):
                op.add_column("lead_import_etl_job", column)


def _drop_storage_columns() -> None:
    if _table_exists("lead_import_etl_job"):
        for column_name in (
            "file_uploaded_at",
            "file_size_bytes",
            "file_content_type",
            "file_storage_key",
            "file_storage_bucket",
        ):
            if _column_exists("lead_import_etl_job", column_name):
                op.drop_column("lead_import_etl_job", column_name)

    if _table_exists("lead_batches"):
        for column_name in (
            "bronze_uploaded_at",
            "bronze_size_bytes",
            "bronze_content_type",
            "bronze_storage_key",
            "bronze_storage_bucket",
        ):
            if _column_exists("lead_batches", column_name):
                op.drop_column("lead_batches", column_name)


def _configure_indexes() -> None:
    if not _is_postgresql():
        return
    context = op.get_context()
    with context.autocommit_block():
        if _table_exists("lead") and not _index_exists("lead", "idx_lead_data_compra_not_null"):
            op.execute(
                sa.text(
                    """
                    create index concurrently idx_lead_data_compra_not_null
                    on public.lead (data_compra)
                    where data_compra is not null
                    """
                )
            )
        if _table_exists("leads_silver") and _index_exists("leads_silver", "ix_leads_silver_leads_silver_batch_id"):
            op.execute("drop index concurrently if exists public.ix_leads_silver_leads_silver_batch_id")


def _drop_indexes() -> None:
    if not _is_postgresql():
        return
    context = op.get_context()
    with context.autocommit_block():
        op.execute("drop index concurrently if exists public.idx_lead_data_compra_not_null")
        if _table_exists("leads_silver") and not _index_exists("leads_silver", "ix_leads_silver_leads_silver_batch_id"):
            op.execute(
                sa.text(
                    """
                    create index concurrently ix_leads_silver_leads_silver_batch_id
                    on public.leads_silver (batch_id)
                    """
                )
            )


def _configure_rls() -> None:
    for table_name in RLS_DISABLED_TABLES:
        if _table_exists(table_name):
            op.execute(sa.text(f'alter table public."{table_name}" disable row level security'))

    for table_name in RLS_ENABLED_TABLES:
        if _table_exists(table_name):
            op.execute(sa.text(f'alter table public."{table_name}" enable row level security'))

    for table_name, policy_name in (
        ("lead_batches", "lead_batches_select"),
        ("lead_batches", "lead_batches_insert"),
        ("lead_batches", "lead_batches_update"),
        ("lead_batches", "lead_batches_delete"),
        ("leads_silver", "leads_silver_select"),
        ("leads_silver", "leads_silver_insert"),
        ("leads_silver", "leads_silver_update"),
        ("leads_silver", "leads_silver_delete"),
        ("lead_import_etl_preview_session", "lead_import_etl_preview_session_select"),
        ("lead_import_etl_preview_session", "lead_import_etl_preview_session_insert"),
        ("lead_import_etl_preview_session", "lead_import_etl_preview_session_update"),
        ("lead_import_etl_preview_session", "lead_import_etl_preview_session_delete"),
        ("lead_import_etl_job", "lead_import_etl_job_select"),
        ("lead_import_etl_job", "lead_import_etl_job_insert"),
        ("lead_import_etl_job", "lead_import_etl_job_update"),
        ("lead_import_etl_job", "lead_import_etl_job_delete"),
        ("lead_import_etl_staging", "lead_import_etl_staging_select"),
        ("lead_import_etl_staging", "lead_import_etl_staging_insert"),
        ("lead_import_etl_staging", "lead_import_etl_staging_update"),
        ("lead_import_etl_staging", "lead_import_etl_staging_delete"),
        ("lead_column_aliases", "lead_column_aliases_select"),
        ("lead_column_aliases", "lead_column_aliases_insert"),
        ("lead_column_aliases", "lead_column_aliases_update"),
        ("lead_column_aliases", "lead_column_aliases_delete"),
    ):
        if _table_exists(table_name):
            _drop_policy(table_name, policy_name)

    if _table_exists("lead_batches"):
        op.execute(
            sa.text(
                """
                create policy lead_batches_select
                on public.lead_batches
                for select
                using (
                  (select public.npbb_is_internal_user())
                  or enviado_por = (select public.npbb_current_user_id())
                  or (
                    (select public.npbb_current_user_type()) = 'agencia'
                    and exists (
                      select 1
                      from public.evento e
                      where e.id = lead_batches.evento_id
                        and e.agencia_id = (select public.npbb_current_agencia_id())
                    )
                  )
                )
                """
            )
        )
        op.execute(
            sa.text(
                """
                create policy lead_batches_insert
                on public.lead_batches
                for insert
                with check (
                  (select public.npbb_is_internal_user())
                  or enviado_por = (select public.npbb_current_user_id())
                )
                """
            )
        )
        op.execute(
            sa.text(
                """
                create policy lead_batches_update
                on public.lead_batches
                for update
                using (
                  (select public.npbb_is_internal_user())
                  or enviado_por = (select public.npbb_current_user_id())
                  or (
                    (select public.npbb_current_user_type()) = 'agencia'
                    and exists (
                      select 1
                      from public.evento e
                      where e.id = lead_batches.evento_id
                        and e.agencia_id = (select public.npbb_current_agencia_id())
                    )
                  )
                )
                with check (
                  (select public.npbb_is_internal_user())
                  or enviado_por = (select public.npbb_current_user_id())
                )
                """
            )
        )
        op.execute(
            sa.text(
                """
                create policy lead_batches_delete
                on public.lead_batches
                for delete
                using (
                  (select public.npbb_is_internal_user())
                  or enviado_por = (select public.npbb_current_user_id())
                )
                """
            )
        )

    if _table_exists("leads_silver"):
        batch_access_sql = """
          exists (
            select 1
            from public.lead_batches b
            left join public.evento e on e.id = b.evento_id
            where b.id = leads_silver.batch_id
              and (
                (select public.npbb_is_internal_user())
                or b.enviado_por = (select public.npbb_current_user_id())
                or (
                  (select public.npbb_current_user_type()) = 'agencia'
                  and e.agencia_id = (select public.npbb_current_agencia_id())
                )
              )
          )
        """
        op.execute(sa.text(f'create policy leads_silver_select on public.leads_silver for select using ({batch_access_sql})'))
        op.execute(sa.text(f'create policy leads_silver_insert on public.leads_silver for insert with check ({batch_access_sql})'))
        op.execute(
            sa.text(
                f"""
                create policy leads_silver_update
                on public.leads_silver
                for update
                using ({batch_access_sql})
                with check ({batch_access_sql})
                """
            )
        )
        op.execute(sa.text(f'create policy leads_silver_delete on public.leads_silver for delete using ({batch_access_sql})'))

    for table_name in ("lead_import_etl_preview_session", "lead_import_etl_job", "lead_import_etl_staging"):
        if not _table_exists(table_name):
            continue
        requested_by_column = "requested_by"
        access_sql = f"""
          (select public.npbb_is_internal_user())
          or {requested_by_column} = (select public.npbb_current_user_id())
        """
        op.execute(sa.text(f'create policy {table_name}_select on public."{table_name}" for select using ({access_sql})'))
        op.execute(sa.text(f'create policy {table_name}_insert on public."{table_name}" for insert with check ({access_sql})'))
        op.execute(
            sa.text(
                f"""
                create policy {table_name}_update
                on public."{table_name}"
                for update
                using ({access_sql})
                with check ({access_sql})
                """
            )
        )
        op.execute(sa.text(f'create policy {table_name}_delete on public."{table_name}" for delete using ({access_sql})'))

    if _table_exists("lead_column_aliases"):
        op.execute(
            sa.text(
                """
                create policy lead_column_aliases_select
                on public.lead_column_aliases
                for select
                using (
                  (select public.npbb_is_internal_user())
                  or (select public.npbb_current_user_id()) is not null
                )
                """
            )
        )
        op.execute(
            sa.text(
                """
                create policy lead_column_aliases_insert
                on public.lead_column_aliases
                for insert
                with check (
                  (select public.npbb_is_internal_user())
                  or criado_por = (select public.npbb_current_user_id())
                )
                """
            )
        )
        op.execute(
            sa.text(
                """
                create policy lead_column_aliases_update
                on public.lead_column_aliases
                for update
                using (
                  (select public.npbb_is_internal_user())
                  or criado_por = (select public.npbb_current_user_id())
                )
                with check (
                  (select public.npbb_is_internal_user())
                  or criado_por = (select public.npbb_current_user_id())
                )
                """
            )
        )
        op.execute(
            sa.text(
                """
                create policy lead_column_aliases_delete
                on public.lead_column_aliases
                for delete
                using (
                  (select public.npbb_is_internal_user())
                  or criado_por = (select public.npbb_current_user_id())
                )
                """
            )
        )


def _drop_rls_policies() -> None:
    for table_name in RLS_ENABLED_TABLES:
        if not _table_exists(table_name):
            continue
        for suffix in ("select", "insert", "update", "delete"):
            _drop_policy(table_name, f"{table_name}_{suffix}")


def upgrade() -> None:
    _configure_storage_columns()
    _configure_indexes()
    _create_helper_functions()
    _configure_rls()


def downgrade() -> None:
    _drop_rls_policies()
    for table_name in RLS_ENABLED_TABLES:
        if _table_exists(table_name):
            op.execute(sa.text(f'alter table public."{table_name}" disable row level security'))
    for table_name in RLS_DISABLED_TABLES:
        if _table_exists(table_name):
            op.execute(sa.text(f'alter table public."{table_name}" enable row level security'))
    _drop_helper_functions()
    _drop_indexes()
    _drop_storage_columns()
