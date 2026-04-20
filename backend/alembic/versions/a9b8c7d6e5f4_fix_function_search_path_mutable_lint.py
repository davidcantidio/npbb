"""Fix Supabase lint 0011: set immutable search_path on public helper and trigger functions.

Revision ID: a9b8c7d6e5f4
Revises: 8b6f4c2d9a1e
Create Date: 2026-04-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "a9b8c7d6e5f4"
down_revision = "8b6f4c2d9a1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

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

            create or replace function public.validate_lead_evento_activation_link()
            returns trigger
            language plpgsql
            set search_path = ''
            as $$
            declare
                matched_ativacao_lead_id integer;
            begin
                if cast(new.source_kind as text) <> 'ativacao' then
                    return new;
                end if;

                if new.source_ref_id is null then
                    raise exception
                        'lead_evento de ativacao exige source_ref_id com ativacao_lead.id';
                end if;

                select al.id
                into matched_ativacao_lead_id
                from public.ativacao_lead as al
                join public.ativacao as a on a.id = al.ativacao_id
                where al.id = new.source_ref_id
                  and al.lead_id = new.lead_id
                  and a.evento_id = new.evento_id;

                if matched_ativacao_lead_id is null then
                    raise exception
                        'lead_evento de ativacao exige ativacao_lead compatível com lead_id=%, evento_id=% e source_ref_id=%',
                        new.lead_id,
                        new.evento_id,
                        new.source_ref_id;
                end if;

                return new;
            end;
            $$;

            create or replace function public.prevent_ativacao_lead_delete_if_linked()
            returns trigger
            language plpgsql
            set search_path = ''
            as $$
            begin
                if exists (
                    select 1
                    from public.lead_evento as le
                    where cast(le.source_kind as text) = 'ativacao'
                      and le.source_ref_id = old.id
                ) then
                    raise exception
                        'Nao e permitido remover ativacao_lead % enquanto existir lead_evento de ativacao apontando para ele',
                        old.id;
                end if;
                return old;
            end;
            $$;
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        sa.text(
            """
            create or replace function public.npbb_current_user_id()
            returns integer
            language sql
            stable
            as $$
              select nullif(current_setting('app.user_id', true), '')::integer
            $$;

            create or replace function public.npbb_current_user_type()
            returns text
            language sql
            stable
            as $$
              select nullif(lower(current_setting('app.user_type', true)), '')
            $$;

            create or replace function public.npbb_current_agencia_id()
            returns integer
            language sql
            stable
            as $$
              select nullif(current_setting('app.agencia_id', true), '')::integer
            $$;

            create or replace function public.npbb_is_internal_user()
            returns boolean
            language sql
            stable
            as $$
              select coalesce(public.npbb_current_user_type() in ('npbb', 'bb'), false)
            $$;

            create or replace function public.validate_lead_evento_activation_link()
            returns trigger
            language plpgsql
            as $$
            declare
                matched_ativacao_lead_id integer;
            begin
                if cast(new.source_kind as text) <> 'ativacao' then
                    return new;
                end if;

                if new.source_ref_id is null then
                    raise exception
                        'lead_evento de ativacao exige source_ref_id com ativacao_lead.id';
                end if;

                select al.id
                into matched_ativacao_lead_id
                from ativacao_lead as al
                join ativacao as a on a.id = al.ativacao_id
                where al.id = new.source_ref_id
                  and al.lead_id = new.lead_id
                  and a.evento_id = new.evento_id;

                if matched_ativacao_lead_id is null then
                    raise exception
                        'lead_evento de ativacao exige ativacao_lead compatível com lead_id=%, evento_id=% e source_ref_id=%',
                        new.lead_id,
                        new.evento_id,
                        new.source_ref_id;
                end if;

                return new;
            end;
            $$;

            create or replace function public.prevent_ativacao_lead_delete_if_linked()
            returns trigger
            language plpgsql
            as $$
            begin
                if exists (
                    select 1
                    from lead_evento as le
                    where cast(le.source_kind as text) = 'ativacao'
                      and le.source_ref_id = old.id
                ) then
                    raise exception
                        'Nao e permitido remover ativacao_lead % enquanto existir lead_evento de ativacao apontando para ele',
                        old.id;
                end if;
                return old;
            end;
            $$;
            """
        )
    )
