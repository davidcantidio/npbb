"""Apply central RLS policies for leads and events.

Revision ID: 8b6f4c2d9a1e
Revises: 7a3c8d1e2f4b
Create Date: 2026-04-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "8b6f4c2d9a1e"
down_revision = "7a3c8d1e2f4b"
branch_labels = None
depends_on = None


CENTRAL_RLS_TABLES = (
    "usuario",
    "evento",
    "ativacao",
    "ativacao_lead",
    "lead",
    "lead_evento",
)


POLICIES = {
    "usuario": ("usuario_select", "usuario_insert", "usuario_update", "usuario_delete"),
    "evento": ("evento_select", "evento_insert", "evento_update", "evento_delete"),
    "ativacao": ("ativacao_select", "ativacao_insert", "ativacao_update", "ativacao_delete"),
    "ativacao_lead": (
        "ativacao_lead_select",
        "ativacao_lead_insert",
        "ativacao_lead_update",
        "ativacao_lead_delete",
    ),
    "lead": ("lead_select", "lead_insert", "lead_update", "lead_delete"),
    "lead_evento": (
        "lead_evento_select",
        "lead_evento_insert",
        "lead_evento_update",
        "lead_evento_delete",
    ),
}


def _existing_public_tables() -> set[str]:
    bind = op.get_bind()
    return set(sa.inspect(bind).get_table_names(schema="public"))


def _drop_policy(table_name: str, policy_name: str) -> None:
    op.execute(sa.text(f'DROP POLICY IF EXISTS "{policy_name}" ON public."{table_name}"'))


def _drop_known_policies(existing_tables: set[str]) -> None:
    for table_name, policy_names in POLICIES.items():
        if table_name not in existing_tables:
            continue
        for policy_name in policy_names:
            _drop_policy(table_name, policy_name)


def _event_access_sql(table_alias: str) -> str:
    return f"""
      (select public.npbb_is_internal_user())
      or (
        (select public.npbb_current_user_type()) = 'agencia'
        and {table_alias}.agencia_id = (select public.npbb_current_agencia_id())
      )
    """


def _activation_access_sql(table_name: str) -> str:
    return f"""
      exists (
        select 1
        from public.evento e
        where e.id = {table_name}.evento_id
          and ({_event_access_sql("e")})
      )
    """


def _activation_lead_access_sql() -> str:
    return f"""
      exists (
        select 1
        from public.ativacao a
        join public.evento e on e.id = a.evento_id
        where a.id = ativacao_lead.ativacao_id
          and ({_event_access_sql("e")})
      )
    """


def _lead_event_access_sql() -> str:
    return f"""
      exists (
        select 1
        from public.evento e
        where e.id = lead_evento.evento_id
          and ({_event_access_sql("e")})
      )
      or (
        (select public.npbb_current_user_type()) = 'agencia'
        and lead_evento.responsavel_agencia_id = (select public.npbb_current_agencia_id())
      )
    """


def _lead_access_sql() -> str:
    return f"""
      (select public.npbb_is_internal_user())
      or exists (
        select 1
        from public.lead_evento le
        join public.evento e on e.id = le.evento_id
        where le.lead_id = lead.id
          and ({_event_access_sql("e")})
      )
      or exists (
        select 1
        from public.lead_batches b
        left join public.evento e on e.id = b.evento_id
        where b.id = lead.batch_id
          and (
            b.enviado_por = (select public.npbb_current_user_id())
            or (
              e.id is not null
              and ({_event_access_sql("e")})
            )
          )
      )
    """


def _create_usuario_policies(existing_tables: set[str]) -> None:
    if "usuario" not in existing_tables:
        return
    access_sql = """
      (select public.npbb_is_internal_user())
      or id = (select public.npbb_current_user_id())
    """
    op.execute(sa.text(f"create policy usuario_select on public.usuario for select using ({access_sql})"))
    op.execute(
        sa.text(
            """
            create policy usuario_insert
            on public.usuario
            for insert
            with check ((select public.npbb_is_internal_user()))
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            create policy usuario_update
            on public.usuario
            for update
            using ({access_sql})
            with check ({access_sql})
            """
        )
    )
    op.execute(
        sa.text(
            """
            create policy usuario_delete
            on public.usuario
            for delete
            using ((select public.npbb_is_internal_user()))
            """
        )
    )


def _create_evento_policies(existing_tables: set[str]) -> None:
    if "evento" not in existing_tables:
        return
    access_sql = _event_access_sql("evento")
    op.execute(sa.text(f"create policy evento_select on public.evento for select using ({access_sql})"))
    op.execute(sa.text(f"create policy evento_insert on public.evento for insert with check ({access_sql})"))
    op.execute(
        sa.text(
            f"""
            create policy evento_update
            on public.evento
            for update
            using ({access_sql})
            with check ({access_sql})
            """
        )
    )
    op.execute(sa.text(f"create policy evento_delete on public.evento for delete using ({access_sql})"))


def _create_ativacao_policies(existing_tables: set[str]) -> None:
    if "ativacao" not in existing_tables or "evento" not in existing_tables:
        return
    access_sql = _activation_access_sql("ativacao")
    op.execute(sa.text(f"create policy ativacao_select on public.ativacao for select using ({access_sql})"))
    op.execute(sa.text(f"create policy ativacao_insert on public.ativacao for insert with check ({access_sql})"))
    op.execute(
        sa.text(
            f"""
            create policy ativacao_update
            on public.ativacao
            for update
            using ({access_sql})
            with check ({access_sql})
            """
        )
    )
    op.execute(sa.text(f"create policy ativacao_delete on public.ativacao for delete using ({access_sql})"))


def _create_ativacao_lead_policies(existing_tables: set[str]) -> None:
    required = {"ativacao_lead", "ativacao", "evento"}
    if not required.issubset(existing_tables):
        return
    access_sql = _activation_lead_access_sql()
    op.execute(sa.text(f"create policy ativacao_lead_select on public.ativacao_lead for select using ({access_sql})"))
    op.execute(
        sa.text(f"create policy ativacao_lead_insert on public.ativacao_lead for insert with check ({access_sql})")
    )
    op.execute(
        sa.text(
            f"""
            create policy ativacao_lead_update
            on public.ativacao_lead
            for update
            using ({access_sql})
            with check ({access_sql})
            """
        )
    )
    op.execute(sa.text(f"create policy ativacao_lead_delete on public.ativacao_lead for delete using ({access_sql})"))


def _create_lead_evento_policies(existing_tables: set[str]) -> None:
    required = {"lead_evento", "evento"}
    if not required.issubset(existing_tables):
        return
    access_sql = _lead_event_access_sql()
    op.execute(sa.text(f"create policy lead_evento_select on public.lead_evento for select using ({access_sql})"))
    op.execute(sa.text(f"create policy lead_evento_insert on public.lead_evento for insert with check ({access_sql})"))
    op.execute(
        sa.text(
            f"""
            create policy lead_evento_update
            on public.lead_evento
            for update
            using ({access_sql})
            with check ({access_sql})
            """
        )
    )
    op.execute(sa.text(f"create policy lead_evento_delete on public.lead_evento for delete using ({access_sql})"))


def _create_lead_policies(existing_tables: set[str]) -> None:
    required = {"lead", "lead_evento", "evento", "lead_batches"}
    if not required.issubset(existing_tables):
        return
    access_sql = _lead_access_sql()
    insert_sql = """
      (select public.npbb_is_internal_user())
      or (select public.npbb_current_user_id()) is not null
    """
    op.execute(sa.text(f"create policy lead_select on public.lead for select using ({access_sql})"))
    op.execute(sa.text(f"create policy lead_insert on public.lead for insert with check ({insert_sql})"))
    op.execute(
        sa.text(
            f"""
            create policy lead_update
            on public.lead
            for update
            using ({access_sql})
            with check ({access_sql})
            """
        )
    )
    op.execute(sa.text(f"create policy lead_delete on public.lead for delete using ({access_sql})"))


def upgrade() -> None:
    existing_tables = _existing_public_tables()
    _drop_known_policies(existing_tables)
    for table_name in CENTRAL_RLS_TABLES:
        if table_name in existing_tables:
            op.execute(sa.text(f'ALTER TABLE public."{table_name}" ENABLE ROW LEVEL SECURITY'))
    _create_usuario_policies(existing_tables)
    _create_evento_policies(existing_tables)
    _create_ativacao_policies(existing_tables)
    _create_ativacao_lead_policies(existing_tables)
    _create_lead_evento_policies(existing_tables)
    _create_lead_policies(existing_tables)


def downgrade() -> None:
    _drop_known_policies(_existing_public_tables())
