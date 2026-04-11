"""add lead_evento table for ISSUE-F1-01-002"""

revision = 'c0d63429d56d'
down_revision = 'a7b8c9d0e1f2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

_DROP_VIEWS_FOR_TABLE_ALLOWED = frozenset({"data_quality_result", "event_sessions", "ingestion"})


def _drop_views_for_table(table_name: str) -> None:
    if table_name not in _DROP_VIEWS_FOR_TABLE_ALLOWED:
        raise ValueError(f"unsupported table for view drop: {table_name}")
    # pg_depend cobre dependencias que information_schema.view_table_usage omite.
    op.execute(
        sa.text(
            f"""
            DO $$
            DECLARE r RECORD;
            BEGIN
              FOR r IN (
                SELECT DISTINCT n.nspname AS view_schema, v.relname AS view_name
                FROM pg_depend d
                JOIN pg_rewrite rw ON rw.oid = d.objid
                JOIN pg_class v ON v.oid = rw.ev_class AND v.relkind = 'v'
                JOIN pg_namespace n ON n.oid = v.relnamespace
                JOIN pg_class t ON t.oid = d.refobjid AND t.relkind = 'r'
                JOIN pg_namespace tn ON tn.oid = t.relnamespace
                WHERE t.relname = '{table_name}'
                  AND tn.nspname = ANY (current_schemas(false))
              ) LOOP
                EXECUTE format('DROP VIEW IF EXISTS %I.%I CASCADE', r.view_schema, r.view_name);
              END LOOP;
            END $$;
            """
        )
    )


def _recreate_mart_dq_views() -> None:
    """Recria vistas DQ (c9d4a1b2e3f4); mart_dq_ingestion_with_summary depende de ingestion.status."""
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_dq_ingestion_summary AS
SELECT
  ingestion_id,
  source_id,
  SUM(CASE WHEN severity = 'ERROR' AND status = 'FAIL' THEN 1 ELSE 0 END) AS error_fail_count,
  SUM(CASE WHEN severity = 'WARN' AND status = 'FAIL' THEN 1 ELSE 0 END) AS warn_fail_count,
  SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS pass_count,
  COUNT(*) AS total_count,
  MAX(created_at) AS last_checked_at
FROM data_quality_result
GROUP BY ingestion_id, source_id
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_dq_ingestion_with_summary AS
SELECT
  i.id AS ingestion_id,
  i.source_id AS source_id,
  i.pipeline AS pipeline,
  i.status AS ingestion_status,
  i.started_at AS started_at,
  i.finished_at AS finished_at,
  COALESCE(s.error_fail_count, 0) AS error_fail_count,
  COALESCE(s.warn_fail_count, 0) AS warn_fail_count,
  COALESCE(s.pass_count, 0) AS pass_count,
  COALESCE(s.total_count, 0) AS total_count,
  s.last_checked_at AS last_checked_at
FROM ingestion i
LEFT JOIN mart_dq_ingestion_summary s ON s.ingestion_id = i.id
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_dq_session_summary AS
SELECT
  session_id,
  SUM(CASE WHEN severity = 'ERROR' AND status = 'FAIL' THEN 1 ELSE 0 END) AS error_fail_count,
  SUM(CASE WHEN severity = 'WARN' AND status = 'FAIL' THEN 1 ELSE 0 END) AS warn_fail_count,
  COUNT(*) AS total_count,
  MAX(created_at) AS last_checked_at
FROM data_quality_result
WHERE session_id IS NOT NULL
GROUP BY session_id
"""
        )
    )


def _recreate_mart_report_views() -> None:
    """Recria marts TMJ removidas antes de ALTER em event_sessions (7e3c2b1a9f0d + d2f4c6a8b0e1)."""
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_attendance_by_session AS
SELECT
  es.id AS session_id,
  es.event_id AS event_id,
  es.session_key,
  es.session_name,
  es.session_type,
  es.session_date,
  MAX(ac.source_id) AS source_id,
  MAX(ac.ingestion_id) AS ingestion_id,
  MAX(ac.ingressos_validos) AS ingressos_validos,
  MAX(ac.presentes) AS presentes,
  MAX(ac.ausentes) AS ausentes,
  MAX(ac.invalidos) AS invalidos,
  MAX(ac.bloqueados) AS bloqueados,
  CASE
    WHEN MAX(ac.ingressos_validos) IS NOT NULL
      AND MAX(ac.ingressos_validos) > 0
      AND MAX(ac.presentes) IS NOT NULL
    THEN (CAST(MAX(ac.presentes) AS FLOAT) * 100.0) / CAST(MAX(ac.ingressos_validos) AS FLOAT)
    ELSE NULL
  END AS comparecimento_pct_calc
FROM event_sessions es
LEFT JOIN attendance_access_control ac ON ac.session_id = es.id
GROUP BY es.id, es.event_id, es.session_key, es.session_name, es.session_type, es.session_date
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_optin_by_session AS
SELECT
  es.id AS session_id,
  es.event_id AS event_id,
  es.session_key,
  es.session_name,
  es.session_type,
  es.session_date,
  COUNT(ot.id) AS tx_count,
  SUM(COALESCE(ot.ticket_qty, 0)) AS tickets_qty,
  COUNT(DISTINCT ot.person_key_hash) AS unique_people
FROM event_sessions es
LEFT JOIN optin_transactions ot ON ot.session_id = es.id
GROUP BY es.id, es.event_id, es.session_key, es.session_name, es.session_type, es.session_date
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_bb_share_by_session AS
WITH base AS (
  SELECT
    es.id AS session_id,
    es.session_key,
    es.session_date,
    COALESCE(m.segment::text, 'DESCONHECIDO') AS segment,
    SUM(COALESCE(ot.ticket_qty, 0)) AS tickets_qty
  FROM event_sessions es
  LEFT JOIN optin_transactions ot ON ot.session_id = es.id
  LEFT JOIN ticket_category_segment_map m ON m.ticket_category_norm = ot.ticket_category_norm
  GROUP BY es.id, es.session_key, es.session_date, COALESCE(m.segment::text, 'DESCONHECIDO')
),
tot AS (
  SELECT session_id, SUM(tickets_qty) AS session_total
  FROM base
  GROUP BY session_id
)
SELECT
  base.session_id,
  base.session_key,
  base.session_date,
  base.segment,
  base.tickets_qty,
  CASE
    WHEN tot.session_total > 0
    THEN (CAST(base.tickets_qty AS FLOAT) * 100.0) / CAST(tot.session_total AS FLOAT)
    ELSE NULL
  END AS share_pct
FROM base
JOIN tot ON tot.session_id = base.session_id
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_sales_curve_daily AS
SELECT
  es.id AS session_id,
  es.session_key,
  es.session_date AS session_date,
  ot.purchase_date,
  SUM(COALESCE(ot.ticket_qty, 0)) AS tickets_qty
FROM optin_transactions ot
JOIN event_sessions es ON es.id = ot.session_id
WHERE ot.purchase_date IS NOT NULL
GROUP BY es.id, es.session_key, es.session_date, ot.purchase_date
ORDER BY es.session_key, ot.purchase_date
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_sales_curve_cum AS
SELECT
  d.session_id,
  d.session_key,
  d.session_date,
  d.purchase_date,
  d.tickets_qty,
  SUM(d.tickets_qty) OVER (
    PARTITION BY d.session_key
    ORDER BY d.purchase_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS tickets_qty_cum
FROM mart_report_sales_curve_daily d
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_leads_by_day AS
SELECT
  fl.session_id AS session_id,
  es.session_key,
  fl.lead_created_date AS day,
  COUNT(fl.id) AS leads_count,
  COUNT(DISTINCT fl.person_key_hash) AS unique_people
FROM festival_leads fl
LEFT JOIN event_sessions es ON es.id = fl.session_id
WHERE fl.lead_created_date IS NOT NULL
GROUP BY fl.session_id, es.session_key, fl.lead_created_date
ORDER BY fl.lead_created_date
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_audience_ruler_by_session AS
SELECT
  es.id AS session_id,
  es.session_key,
  es.session_date,
  es.session_type,
  att.ingressos_validos AS ingressos_validos,
  att.presentes AS entradas_validadas,
  opt.tx_count AS optin_tx_count,
  opt.tickets_qty AS optin_tickets_qty,
  opt.unique_people AS optin_unique_people,
  ts.sold_total AS ingressos_vendidos_total,
  ts.net_sold_total AS ingressos_vendidos_liquidos
FROM event_sessions es
LEFT JOIN (
  SELECT
    session_id,
    MAX(ingressos_validos) AS ingressos_validos,
    MAX(presentes) AS presentes
  FROM attendance_access_control
  GROUP BY session_id
) att ON att.session_id = es.id
LEFT JOIN (
  SELECT
    session_id,
    COUNT(id) AS tx_count,
    SUM(COALESCE(ticket_qty, 0)) AS tickets_qty,
    COUNT(DISTINCT person_key_hash) AS unique_people
  FROM optin_transactions
  GROUP BY session_id
) opt ON opt.session_id = es.id
LEFT JOIN (
  SELECT
    session_id,
    MAX(sold_total) AS sold_total,
    MAX(net_sold_total) AS net_sold_total
  FROM ticket_sales
  GROUP BY session_id
) ts ON ts.session_id = es.id
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_session_coverage AS
SELECT
  es.id AS session_id,
  es.session_key,
  es.session_name,
  es.session_type,
  es.session_date,
  CASE WHEN EXISTS (SELECT 1 FROM optin_transactions ot WHERE ot.session_id = es.id) THEN 1 ELSE 0 END AS has_optin,
  CASE WHEN EXISTS (SELECT 1 FROM attendance_access_control ac WHERE ac.session_id = es.id) THEN 1 ELSE 0 END AS has_access_control,
  CASE WHEN EXISTS (SELECT 1 FROM festival_leads fl WHERE fl.session_id = es.id) THEN 1 ELSE 0 END AS has_leads
FROM event_sessions es
"""
        )
    )
    op.execute(
        sa.text(
            """
CREATE OR REPLACE VIEW mart_report_show_day_summary AS
WITH expected AS (
  SELECT '2025-12-12' AS show_date
  UNION ALL SELECT '2025-12-13'
  UNION ALL SELECT '2025-12-14'
),
expected_keys AS (
  SELECT
    show_date,
    ('TMJ2025_' || REPLACE(CAST(show_date AS TEXT), '-', '') || '_SHOW') AS session_key_expected
  FROM expected
),
sess AS (
  SELECT
    ek.show_date,
    ek.session_key_expected,
    es.id AS session_id,
    es.session_name,
    es.session_type,
    es.session_date
  FROM expected_keys ek
  LEFT JOIN event_sessions es ON es.session_key = ek.session_key_expected
),
opt AS (
  SELECT
    session_id,
    COUNT(id) AS optin_tx_count,
    SUM(COALESCE(ticket_qty, 0)) AS optin_tickets_qty,
    COUNT(DISTINCT person_key_hash) AS optin_unique_people
  FROM optin_transactions
  GROUP BY session_id
),
att AS (
  SELECT
    session_id,
    MAX(ingressos_validos) AS ingressos_validos,
    MAX(presentes) AS entradas_validadas
  FROM attendance_access_control
  GROUP BY session_id
),
sales AS (
  SELECT
    session_id,
    MAX(sold_total) AS sold_total,
    MAX(net_sold_total) AS net_sold_total
  FROM ticket_sales
  GROUP BY session_id
),
base AS (
  SELECT
    sess.show_date,
    sess.session_key_expected,
    sess.session_id,
    sess.session_name,
    sess.session_type,
    sess.session_date,
    CASE WHEN sess.session_id IS NOT NULL THEN 1 ELSE 0 END AS has_session,
    COALESCE(opt.optin_tx_count, 0) AS optin_tx_count,
    COALESCE(opt.optin_tickets_qty, 0) AS optin_tickets_qty,
    COALESCE(opt.optin_unique_people, 0) AS optin_unique_people,
    att.ingressos_validos AS ingressos_validos,
    att.entradas_validadas AS entradas_validadas,
    sales.sold_total AS sold_total,
    sales.net_sold_total AS net_sold_total,
    CASE WHEN COALESCE(opt.optin_tickets_qty, 0) > 0 THEN 1 ELSE 0 END AS has_optin,
    CASE WHEN COALESCE(att.entradas_validadas, 0) > 0 THEN 1 ELSE 0 END AS has_access_control,
    CASE WHEN sales.sold_total IS NOT NULL OR sales.net_sold_total IS NOT NULL THEN 1 ELSE 0 END AS has_ticket_sales,
    CASE
      WHEN att.entradas_validadas IS NOT NULL
        AND att.ingressos_validos IS NOT NULL
        AND att.entradas_validadas > att.ingressos_validos
      THEN 1
      WHEN sales.net_sold_total IS NOT NULL
        AND sales.sold_total IS NOT NULL
        AND sales.net_sold_total > sales.sold_total
      THEN 1
      WHEN opt.optin_unique_people IS NOT NULL
        AND opt.optin_tickets_qty IS NOT NULL
        AND opt.optin_unique_people > opt.optin_tickets_qty
      THEN 1
      ELSE 0
    END AS has_inconsistency,
    TRIM(
      COALESCE(
        (CASE
          WHEN att.entradas_validadas IS NOT NULL
            AND att.ingressos_validos IS NOT NULL
            AND att.entradas_validadas > att.ingressos_validos
          THEN 'acesso_presentes_maior_que_validos; '
          ELSE ''
        END) ||
        (CASE
          WHEN sales.net_sold_total IS NOT NULL
            AND sales.sold_total IS NOT NULL
            AND sales.net_sold_total > sales.sold_total
          THEN 'vendas_liquidas_maior_que_total; '
          ELSE ''
        END) ||
        (CASE
          WHEN opt.optin_unique_people IS NOT NULL
            AND opt.optin_tickets_qty IS NOT NULL
            AND opt.optin_unique_people > opt.optin_tickets_qty
          THEN 'optin_unicos_maior_que_tickets; '
          ELSE ''
        END)
      , '')
    ) AS inconsistency_details
  FROM sess
  LEFT JOIN opt ON opt.session_id = sess.session_id
  LEFT JOIN att ON att.session_id = sess.session_id
  LEFT JOIN sales ON sales.session_id = sess.session_id
)
SELECT
  show_date,
  session_key_expected,
  session_id,
  session_name,
  session_type,
  session_date,
  has_session,
  has_optin,
  has_access_control,
  has_ticket_sales,
  optin_tx_count,
  optin_tickets_qty,
  optin_unique_people,
  ingressos_validos,
  entradas_validadas,
  sold_total,
  net_sold_total,
  has_inconsistency,
  inconsistency_details,
  TRIM(
    COALESCE(
      (CASE WHEN has_session = 0 THEN 'sessao_ausente; optin; acesso; vendas; ' ELSE '' END) ||
      (CASE WHEN has_session = 1 AND has_optin = 0 THEN 'optin; ' ELSE '' END) ||
      (CASE WHEN has_session = 1 AND has_access_control = 0 THEN 'acesso; ' ELSE '' END) ||
      (CASE WHEN has_session = 1 AND has_ticket_sales = 0 THEN 'vendas; ' ELSE '' END)
    , '')
  ) AS missing_flags,
  CASE
    WHEN has_session = 0 THEN 'GAP'
    WHEN has_inconsistency = 1 THEN 'INCONSISTENTE'
    WHEN has_optin = 1 AND has_access_control = 1 AND has_ticket_sales = 1 THEN 'OK'
    ELSE 'GAP'
  END AS status,
  CASE
    WHEN has_session = 0 THEN 'Solicitar agenda master da sessao (show) e fontes minimas (acesso, vendas, opt-in).'
    WHEN has_optin = 0 AND has_access_control = 0 AND has_ticket_sales = 0 THEN 'Solicitar: XLSX opt-in aceitos (Eventim); PDF controle de acesso (show) por sessao; base de vendas total/liquida por sessao.'
    WHEN has_optin = 0 THEN 'Solicitar: XLSX opt-in aceitos (Eventim) por sessao.'
    WHEN has_access_control = 0 THEN 'Solicitar: PDF controle de acesso (show) com ingressos_validos/presentes por sessao.'
    WHEN has_ticket_sales = 0 THEN 'Solicitar: base de vendas (sold_total/net_sold_total) por sessao.'
    ELSE ''
  END AS request_needed
FROM base
ORDER BY show_date
"""
        )
    )


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('framework_project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('canonical_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('draft', 'intake', 'prd', 'planning', 'execution', 'audit', 'completed', 'cancelled', name='framework_project_status'), nullable=False),
    sa.Column('agent_mode', sa.Enum('human_in_loop', 'semi_autonomous', 'fully_autonomous', name='framework_agent_mode'), nullable=False),
    sa.Column('source_of_truth', sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
    sa.Column('project_root_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('audit_log_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('current_intake_id', sa.Integer(), nullable=True),
    sa.Column('current_prd_id', sa.Integer(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('owner', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_project'))
    )
    op.create_index(op.f('ix_framework_project_framework_project_canonical_name'), 'framework_project', ['canonical_name'], unique=True)
    op.create_table('framework_intake',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('doc_id', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('status', sa.Enum('draft', 'active', 'done', 'cancelled', name='framework_artifact_status'), nullable=False),
    sa.Column('approval_status', sa.Enum('pending', 'approved', 'rejected', 'auto_approved', name='framework_approval_status'), nullable=False),
    sa.Column('intake_kind', sa.Enum('new-product', 'new-capability', 'problem', 'refactor', 'audit-remediation', name='framework_intake_kind'), nullable=True),
    sa.Column('source_mode', sa.Enum('original', 'backfilled', 'audit-derived', name='framework_source_mode'), nullable=True),
    sa.Column('content_md', sa.Text(), nullable=False),
    sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('checklist_status_json', sa.JSON(), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('approved_by', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_intake_project_id_framework_project')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_intake')),
    sa.UniqueConstraint('project_id', 'doc_id', name='uq_framework_intake_doc')
    )
    op.create_table('framework_prd',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('intake_id', sa.Integer(), nullable=True),
    sa.Column('doc_id', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('status', sa.Enum('draft', 'active', 'done', 'cancelled', name='framework_artifact_status'), nullable=False),
    sa.Column('approval_status', sa.Enum('pending', 'approved', 'rejected', 'auto_approved', name='framework_approval_status'), nullable=False),
    sa.Column('content_md', sa.Text(), nullable=False),
    sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('approved_by', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['intake_id'], ['framework_intake.id'], name=op.f('fk_framework_prd_intake_id_framework_intake')),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_prd_project_id_framework_project')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_prd')),
    sa.UniqueConstraint('project_id', 'doc_id', name='uq_framework_prd_doc')
    )
    op.create_table('framework_phase',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('phase_number', sa.Integer(), nullable=False),
    sa.Column('canonical_id', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('status', sa.Enum('todo', 'active', 'done', 'cancelled', name='framework_document_status'), nullable=False),
    sa.Column('audit_gate', sa.Enum('not_ready', 'pending', 'hold', 'approved', name='framework_audit_gate_state'), nullable=False),
    sa.Column('objective', sa.Text(), nullable=True),
    sa.Column('exit_gate', sa.Text(), nullable=True),
    sa.Column('scope_in_json', sa.JSON(), nullable=True),
    sa.Column('scope_out_json', sa.JSON(), nullable=True),
    sa.Column('dependency_refs_json', sa.JSON(), nullable=True),
    sa.Column('definition_of_done_json', sa.JSON(), nullable=True),
    sa.Column('story_points_target', sa.Integer(), nullable=True),
    sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_phase_project_id_framework_project')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_phase')),
    sa.UniqueConstraint('project_id', 'phase_number', name='uq_framework_phase_number'),
    sa.UniqueConstraint('project_id', 'canonical_id', name='uq_framework_phase_canonical')
    )
    op.create_table('framework_epic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('phase_id', sa.Integer(), nullable=False),
    sa.Column('epic_number', sa.Integer(), nullable=False),
    sa.Column('canonical_id', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('objective', sa.Text(), nullable=True),
    sa.Column('measurable_outcome', sa.Text(), nullable=True),
    sa.Column('context_architecture', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('todo', 'active', 'done', 'cancelled', name='framework_document_status'), nullable=False),
    sa.Column('dependency_refs_json', sa.JSON(), nullable=True),
    sa.Column('definition_of_done_json', sa.JSON(), nullable=True),
    sa.Column('artifact_minimum', sa.Text(), nullable=True),
    sa.Column('story_points_target', sa.Integer(), nullable=True),
    sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_epic_project_id_framework_project')),
    sa.ForeignKeyConstraint(['phase_id'], ['framework_phase.id'], name=op.f('fk_framework_epic_phase_id_framework_phase')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_epic')),
    sa.UniqueConstraint('phase_id', 'epic_number', name='uq_framework_epic_number'),
    sa.UniqueConstraint('project_id', 'canonical_id', name='uq_framework_epic_canonical')
    )
    op.create_table('framework_sprint',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('phase_id', sa.Integer(), nullable=False),
    sa.Column('sprint_number', sa.Integer(), nullable=False),
    sa.Column('canonical_id', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
    sa.Column('objective', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('todo', 'active', 'done', 'cancelled', name='framework_document_status'), nullable=False),
    sa.Column('capacity_story_points', sa.Integer(), nullable=False),
    sa.Column('capacity_issues', sa.Integer(), nullable=False),
    sa.Column('override_note', sa.Text(), nullable=True),
    sa.Column('risks_text', sa.Text(), nullable=True),
    sa.Column('closing_decision', sa.Text(), nullable=True),
    sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['phase_id'], ['framework_phase.id'], name=op.f('fk_framework_sprint_phase_id_framework_phase')),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_sprint_project_id_framework_project')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_sprint')),
    sa.UniqueConstraint('phase_id', 'sprint_number', name='uq_framework_sprint_number'),
    sa.UniqueConstraint('project_id', 'canonical_id', name='uq_framework_sprint_canonical')
    )
    op.create_table('framework_issue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('phase_id', sa.Integer(), nullable=False),
    sa.Column('epic_id', sa.Integer(), nullable=False),
    sa.Column('sprint_id', sa.Integer(), nullable=True),
    sa.Column('issue_number', sa.Integer(), nullable=False),
    sa.Column('canonical_id', sqlmodel.sql.sqltypes.AutoString(length=48), nullable=False),
    sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=160), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=220), nullable=False),
    sa.Column('status', sa.Enum('todo', 'active', 'done', 'cancelled', name='framework_document_status'), nullable=False),
    sa.Column('issue_format', sa.Enum('directory', 'legacy', name='framework_issue_format'), nullable=False),
    sa.Column('task_instruction_mode', sa.Enum('optional', 'required', name='framework_task_instruction_mode'), nullable=False),
    sa.Column('story_points', sa.Integer(), nullable=False),
    sa.Column('user_story', sa.Text(), nullable=True),
    sa.Column('technical_context', sa.Text(), nullable=True),
    sa.Column('tdd_red', sa.Text(), nullable=True),
    sa.Column('tdd_green', sa.Text(), nullable=True),
    sa.Column('tdd_refactor', sa.Text(), nullable=True),
    sa.Column('acceptance_criteria_json', sa.JSON(), nullable=True),
    sa.Column('definition_of_done_json', sa.JSON(), nullable=True),
    sa.Column('real_files_json', sa.JSON(), nullable=True),
    sa.Column('dependency_refs_json', sa.JSON(), nullable=True),
    sa.Column('decision_refs_json', sa.JSON(), nullable=True),
    sa.Column('artifact_minimum', sa.Text(), nullable=True),
    sa.Column('origin_issue_ref', sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True),
    sa.Column('origin_audit_id', sqlmodel.sql.sqltypes.AutoString(length=80), nullable=True),
    sa.Column('evidence_ref', sa.Text(), nullable=True),
    sa.Column('document_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['epic_id'], ['framework_epic.id'], name=op.f('fk_framework_issue_epic_id_framework_epic')),
    sa.ForeignKeyConstraint(['phase_id'], ['framework_phase.id'], name=op.f('fk_framework_issue_phase_id_framework_phase')),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_issue_project_id_framework_project')),
    sa.ForeignKeyConstraint(['sprint_id'], ['framework_sprint.id'], name=op.f('fk_framework_issue_sprint_id_framework_sprint')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_issue')),
    sa.UniqueConstraint('epic_id', 'issue_number', name='uq_framework_issue_number'),
    sa.UniqueConstraint('project_id', 'canonical_id', name='uq_framework_issue_canonical')
    )
    op.create_table('framework_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('issue_id', sa.Integer(), nullable=False),
    sa.Column('task_number', sa.Integer(), nullable=False),
    sa.Column('canonical_id', sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False),
    sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=220), nullable=False),
    sa.Column('status', sa.Enum('todo', 'active', 'done', 'cancelled', name='framework_document_status'), nullable=False),
    sa.Column('objective', sa.Text(), nullable=True),
    sa.Column('preconditions_json', sa.JSON(), nullable=True),
    sa.Column('files_to_touch_json', sa.JSON(), nullable=True),
    sa.Column('tdd_aplicavel', sa.Boolean(), nullable=False),
    sa.Column('red_tests_json', sa.JSON(), nullable=True),
    sa.Column('red_command', sa.Text(), nullable=True),
    sa.Column('red_criteria', sa.Text(), nullable=True),
    sa.Column('atomic_steps_json', sa.JSON(), nullable=True),
    sa.Column('allowed_commands_json', sa.JSON(), nullable=True),
    sa.Column('expected_result', sa.Text(), nullable=True),
    sa.Column('required_validations_json', sa.JSON(), nullable=True),
    sa.Column('stop_conditions_json', sa.JSON(), nullable=True),
    sa.Column('instruction_payload_json', sa.JSON(), nullable=True),
    sa.Column('document_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('executed_by_agent', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('result_summary', sa.Text(), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['issue_id'], ['framework_issue.id'], name=op.f('fk_framework_task_issue_id_framework_issue')),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_framework_task_project_id_framework_project')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_framework_task')),
    sa.UniqueConstraint('issue_id', 'task_number', name='uq_framework_task_number'),
    sa.UniqueConstraint('project_id', 'canonical_id', name='uq_framework_task_canonical')
    )
    op.create_table('agent_execution',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('phase_id', sa.Integer(), nullable=True),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('step', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
    sa.Column('target_ref', sqlmodel.sql.sqltypes.AutoString(length=160), nullable=True),
    sa.Column('prompt_used', sa.Text(), nullable=False),
    sa.Column('output_generated', sa.Text(), nullable=False),
    sa.Column('evidence_ref', sa.Text(), nullable=True),
    sa.Column('agent_model', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('duration_ms', sa.Integer(), nullable=True),
    sa.Column('success', sa.Boolean(), nullable=False),
    sa.Column('human_approval', sa.Enum('pending', 'approved', 'rejected', 'auto_approved', name='framework_approval_status'), nullable=True),
    sa.Column('approved_by', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['issue_id'], ['framework_issue.id'], name=op.f('fk_agent_execution_issue_id_framework_issue')),
    sa.ForeignKeyConstraint(['phase_id'], ['framework_phase.id'], name=op.f('fk_agent_execution_phase_id_framework_phase')),
    sa.ForeignKeyConstraint(['project_id'], ['framework_project.id'], name=op.f('fk_agent_execution_project_id_framework_project')),
    sa.ForeignKeyConstraint(['task_id'], ['framework_task.id'], name=op.f('fk_agent_execution_task_id_framework_task')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_agent_execution'))
    )
    op.create_table('lead_evento',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lead_id', sa.Integer(), nullable=False),
    sa.Column('evento_id', sa.Integer(), nullable=False),
    sa.Column('source_kind', sa.Enum('ACTIVATION', 'EVENT_DIRECT', 'LEAD_BATCH', 'EVENT_NAME_BACKFILL', 'MANUAL_RECONCILED', name='leadeventosourcekind'), nullable=False),
    sa.Column('source_ref_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['evento_id'], ['evento.id'], name=op.f('fk_lead_evento_evento_id_evento')),
    sa.ForeignKeyConstraint(['lead_id'], ['lead.id'], name=op.f('fk_lead_evento_lead_id_lead')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_lead_evento')),
    sa.UniqueConstraint('lead_id', 'evento_id', name='uq_lead_evento_lead_id_evento_id')
    )
    op.create_index(op.f('ix_lead_evento_lead_evento_evento_id'), 'lead_evento', ['evento_id'], unique=False)
    op.create_index(op.f('ix_lead_evento_lead_evento_lead_id'), 'lead_evento', ['lead_id'], unique=False)
    op.create_index(op.f('ix_lead_evento_lead_evento_source_kind'), 'lead_evento', ['source_kind'], unique=False)
    op.create_index(op.f('ix_lead_evento_lead_evento_source_ref_id'), 'lead_evento', ['source_ref_id'], unique=False)
    # Staging/ETL tables and views have cross-FKs and marts views; sequential drop_index+drop_table
    # fails on production (Render) with DependentObjectsStillExist. CASCADE removes dependent views/FKs.
    _etl_drop_order = (
        "stg_access_control_sessions",
        "stg_mtc_metrics",
        "stg_dimac_metrics",
        "ingestions",
        "stg_leads",
        "stg_social_metrics",
        "lineage_refs",
        "stg_optin_transactions",
        "stg_lead_actions",
        "dq_check_result",
        "dq_inconsistency",
    )
    for _tbl in _etl_drop_order:
        op.execute(sa.text(f'DROP TABLE IF EXISTS "{_tbl}" CASCADE'))
    op.alter_column('ativacao', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=True)
    op.drop_index('ix_ativacao_gamificacao_id', table_name='ativacao')
    op.drop_index('ix_ativacao_lead_gamificacao_id', table_name='ativacao_lead')
    op.create_index(op.f('ix_ativacao_lead_ativacao_lead_lead_id'), 'ativacao_lead', ['lead_id'], unique=False)
    op.drop_constraint('fk_ativacao_lead_gamificacao_id', 'ativacao_lead', type_='foreignkey')
    op.create_foreign_key(op.f('fk_ativacao_lead_gamificacao_id_gamificacao'), 'ativacao_lead', 'gamificacao', ['gamificacao_id'], ['id'])
    op.alter_column('attendance_access_control', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_attendance_access_control_ingestion_id', table_name='attendance_access_control')
    op.drop_index('ix_attendance_access_control_lineage_ref_id', table_name='attendance_access_control')
    op.drop_index('ix_attendance_access_control_session_id', table_name='attendance_access_control')
    op.drop_index('ix_attendance_access_control_source_id', table_name='attendance_access_control')
    op.create_index(op.f('ix_attendance_access_control_attendance_access_control_ingestion_id'), 'attendance_access_control', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_attendance_access_control_attendance_access_control_source_id'), 'attendance_access_control', ['source_id'], unique=False)
    op.create_index(op.f('ix_attendance_access_control_attendance_access_control_session_id'), 'attendance_access_control', ['session_id'], unique=False)
    op.drop_constraint('fk_attendance_access_control_source_id_sources', 'attendance_access_control', type_='foreignkey')
    op.execute(
        sa.text(
            "ALTER TABLE attendance_access_control DROP CONSTRAINT IF EXISTS "
            "fk_attendance_access_control_lineage_ref_id_lineage_refs"
        )
    )
    op.drop_column('attendance_access_control', 'lineage_ref_id')
    op.alter_column('conversao_ativacao', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_constraint('convidado_cpf_key', 'convidado', type_='unique')
    op.drop_constraint('convidado_email_key', 'convidado', type_='unique')
    op.create_unique_constraint(op.f('uq_convidado_cpf'), 'convidado', ['cpf'])
    op.create_unique_constraint(op.f('uq_convidado_email'), 'convidado', ['email'])
    op.create_index(op.f('ix_cota_cortesia_cota_cortesia_diretoria_id'), 'cota_cortesia', ['diretoria_id'], unique=False)
    op.create_unique_constraint(op.f('uq_cota_cortesia_evento_id'), 'cota_cortesia', ['evento_id', 'diretoria_id'])
    op.drop_constraint('fk_cota_cortesia_alterado_por_usuario', 'cota_cortesia', type_='foreignkey')
    op.drop_column('cota_cortesia', 'valor_anterior')
    op.drop_column('cota_cortesia', 'valor_novo')
    op.drop_column('cota_cortesia', 'alterado_por')
    op.drop_column('cota_cortesia', 'alterado_em')
    op.drop_constraint('cupom_codigo_key', 'cupom', type_='unique')
    op.create_unique_constraint(op.f('uq_cupom_codigo'), 'cupom', ['codigo'])
    # Qualquer vista sobre data_quality_result bloqueia ALTER TYPE nas colunas.
    # mart_dq_ingestion_summary nao referencia scope; por isso scope alterava e severity falhava.
    _drop_views_for_table("data_quality_result")
    # Garantir tipos ENUM no Postgres (alter_column com sa.Enum nao os cria sozinhos aqui).
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE dataqualityscope AS ENUM "
            "('STAGING', 'CANONICAL', 'MARTS'); EXCEPTION WHEN duplicate_object THEN NULL; END $$"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE dataqualityseverity AS ENUM "
            "('WARN', 'ERROR'); EXCEPTION WHEN duplicate_object THEN NULL; END $$"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE dataqualitystatus AS ENUM "
            "('PASS', 'FAIL', 'SKIP'); EXCEPTION WHEN duplicate_object THEN NULL; END $$"
        )
    )
    op.alter_column(
        "data_quality_result",
        "scope",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM("STAGING", "CANONICAL", "MARTS", name="dataqualityscope", create_type=False),
        existing_nullable=False,
        postgresql_using="scope::dataqualityscope",
    )
    op.alter_column(
        "data_quality_result",
        "severity",
        existing_type=sa.VARCHAR(length=10),
        type_=postgresql.ENUM("WARN", "ERROR", name="dataqualityseverity", create_type=False),
        existing_nullable=False,
        postgresql_using="severity::dataqualityseverity",
    )
    op.alter_column(
        "data_quality_result",
        "status",
        existing_type=sa.VARCHAR(length=10),
        type_=postgresql.ENUM("PASS", "FAIL", "SKIP", name="dataqualitystatus", create_type=False),
        existing_nullable=False,
        postgresql_using="status::dataqualitystatus",
    )
    op.alter_column('data_quality_result', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_data_quality_result_check_key', table_name='data_quality_result')
    op.drop_index('ix_data_quality_result_ingestion_id', table_name='data_quality_result')
    op.drop_index('ix_data_quality_result_scope', table_name='data_quality_result')
    op.drop_index('ix_data_quality_result_session_id', table_name='data_quality_result')
    op.drop_index('ix_data_quality_result_severity', table_name='data_quality_result')
    op.drop_index('ix_data_quality_result_source_id', table_name='data_quality_result')
    op.drop_index('ix_data_quality_result_status', table_name='data_quality_result')
    op.create_index(op.f('ix_data_quality_result_data_quality_result_check_key'), 'data_quality_result', ['check_key'], unique=False)
    op.create_index(op.f('ix_data_quality_result_data_quality_result_ingestion_id'), 'data_quality_result', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_data_quality_result_data_quality_result_scope'), 'data_quality_result', ['scope'], unique=False)
    op.create_index(op.f('ix_data_quality_result_data_quality_result_session_id'), 'data_quality_result', ['session_id'], unique=False)
    op.create_index(op.f('ix_data_quality_result_data_quality_result_severity'), 'data_quality_result', ['severity'], unique=False)
    op.create_index(op.f('ix_data_quality_result_data_quality_result_source_id'), 'data_quality_result', ['source_id'], unique=False)
    op.create_index(op.f('ix_data_quality_result_data_quality_result_status'), 'data_quality_result', ['status'], unique=False)
    # mart_dq_* com ingestion so no fim do upgrade (apos ALTER em ingestion.status).
    op.drop_constraint('diretoria_nome_key', 'diretoria', type_='unique')
    op.create_unique_constraint(op.f('uq_diretoria_nome'), 'diretoria', ['nome'])
    op.drop_constraint('divisao_demandante_nome_key', 'divisao_demandante', type_='unique')
    op.create_unique_constraint(op.f('uq_divisao_demandante_nome'), 'divisao_demandante', ['nome'])
    op.alter_column('event_publicity', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('event_publicity', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_index('ix_event_publicity_event_id', table_name='event_publicity')
    op.drop_index('ix_event_publicity_linked_at', table_name='event_publicity')
    op.create_index(op.f('ix_event_publicity_event_publicity_event_id'), 'event_publicity', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_publicity_event_publicity_linked_at'), 'event_publicity', ['linked_at'], unique=False)
    # mart_report_* referenciam event_sessions.session_type (VARCHAR->ENUM bloqueia se vistas existirem).
    _drop_views_for_table("event_sessions")
    # sa.Enum em alter_column nao cria o tipo no Postgres; um execute multiplo pode falhar no driver.
    _pg_enum_ddl = (
        (
            "eventsessiontype",
            "'DIURNO_GRATUITO', 'NOTURNO_SHOW', 'OUTRO'",
        ),
        (
            "ingestionstatus",
            "'RUNNING', 'SUCCEEDED', 'FAILED', 'SKIPPED'",
        ),
        (
            "leadaliastipo",
            "'EVENTO', 'CIDADE', 'ESTADO', 'GENERO'",
        ),
        ("batchstage", "'BRONZE', 'SILVER', 'GOLD'"),
        (
            "pipelinestatus",
            "'PENDING', 'PASS', 'PASS_WITH_WARNINGS', 'FAIL'",
        ),
        ("leadconversaotipo", "'COMPRA_INGRESSO', 'ACAO_EVENTO'"),
        ("solicitacaoingressotipo", "'SELF', 'TERCEIRO'"),
        ("solicitacaoingressostatus", "'SOLICITADO', 'CANCELADO'"),
        (
            "sourcekind",
            "'DOCX', 'PDF', 'XLSX', 'PPTX', 'CSV', 'MANUAL', 'OTHER'",
        ),
        (
            "bbrelationshipsegment",
            "'CLIENTE_BB', 'CARTAO_BB', 'FUNCIONARIO_BB', 'PUBLICO_GERAL', 'OUTRO', 'DESCONHECIDO'",
        ),
    )
    for _enum_name, _labels in _pg_enum_ddl:
        op.execute(
            sa.text(
                f"DO $$ BEGIN CREATE TYPE {_enum_name} AS ENUM ({_labels}); "
                "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
            )
        )
    op.alter_column(
        "event_sessions",
        "session_type",
        existing_type=sa.VARCHAR(length=30),
        type_=postgresql.ENUM(
            "DIURNO_GRATUITO",
            "NOTURNO_SHOW",
            "OUTRO",
            name="eventsessiontype",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="session_type::eventsessiontype",
    )
    op.alter_column('event_sessions', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('event_sessions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_index('ix_event_sessions_event_id', table_name='event_sessions')
    op.drop_index('ix_event_sessions_session_date', table_name='event_sessions')
    op.drop_index('ix_event_sessions_session_type', table_name='event_sessions')
    op.drop_index('ix_event_sessions_source_of_truth_source_id', table_name='event_sessions')
    op.drop_constraint('uq_event_sessions_session_key', 'event_sessions', type_='unique')
    op.create_index(op.f('ix_event_sessions_event_sessions_event_id'), 'event_sessions', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_sessions_event_sessions_session_date'), 'event_sessions', ['session_date'], unique=False)
    op.create_index(op.f('ix_event_sessions_event_sessions_session_key'), 'event_sessions', ['session_key'], unique=True)
    op.create_index(op.f('ix_event_sessions_event_sessions_session_type'), 'event_sessions', ['session_type'], unique=False)
    op.create_index(op.f('ix_event_sessions_event_sessions_source_of_truth_source_id'), 'event_sessions', ['source_of_truth_source_id'], unique=False)
    op.alter_column('evento', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=True)
    op.drop_index('ix_evento_external_project_code', table_name='evento')
    op.create_index(op.f('ix_evento_evento_cidade'), 'evento', ['cidade'], unique=False)
    op.create_index(op.f('ix_evento_evento_estado'), 'evento', ['estado'], unique=False)
    op.create_index(op.f('ix_evento_evento_external_project_code'), 'evento', ['external_project_code'], unique=False)
    op.alter_column('evento_landing_customization_audit', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_evento_landing_customization_audit_changed_by_user_id', table_name='evento_landing_customization_audit')
    op.drop_index('ix_evento_landing_customization_audit_event_id', table_name='evento_landing_customization_audit')
    op.create_index(op.f('ix_evento_landing_customization_audit_evento_landing_customization_audit_changed_by_user_id'), 'evento_landing_customization_audit', ['changed_by_user_id'], unique=False)
    op.create_index(op.f('ix_evento_landing_customization_audit_evento_landing_customization_audit_event_id'), 'evento_landing_customization_audit', ['event_id'], unique=False)
    op.alter_column('festival_leads', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_festival_leads_event_id', table_name='festival_leads')
    op.drop_index('ix_festival_leads_ingestion_id', table_name='festival_leads')
    op.drop_index('ix_festival_leads_lead_created_date', table_name='festival_leads')
    op.drop_index('ix_festival_leads_person_key_hash', table_name='festival_leads')
    op.drop_index('ix_festival_leads_session_id', table_name='festival_leads')
    op.drop_index('ix_festival_leads_source_id', table_name='festival_leads')
    op.create_index(op.f('ix_festival_leads_festival_leads_cpf_hash'), 'festival_leads', ['cpf_hash'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_email_hash'), 'festival_leads', ['email_hash'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_event_id'), 'festival_leads', ['event_id'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_ingestion_id'), 'festival_leads', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_lead_created_date'), 'festival_leads', ['lead_created_date'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_person_key_hash'), 'festival_leads', ['person_key_hash'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_session_id'), 'festival_leads', ['session_id'], unique=False)
    op.create_index(op.f('ix_festival_leads_festival_leads_source_id'), 'festival_leads', ['source_id'], unique=False)
    op.drop_constraint('formulario_landing_template_nome_key', 'formulario_landing_template', type_='unique')
    op.create_unique_constraint(op.f('uq_formulario_landing_template_nome'), 'formulario_landing_template', ['nome'])
    op.drop_constraint('funcionario_chave_c_key', 'funcionario', type_='unique')
    op.drop_constraint('funcionario_email_key', 'funcionario', type_='unique')
    op.create_unique_constraint(op.f('uq_funcionario_chave_c'), 'funcionario', ['chave_c'])
    op.create_unique_constraint(op.f('uq_funcionario_email'), 'funcionario', ['email'])
    op.drop_column('funcionario', 'area_codigo')
    op.drop_column('funcionario', 'area')
    op.drop_index('ix_gamificacao_evento_id', table_name='gamificacao')
    op.alter_column('import_alias', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('import_alias', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_index('ix_import_alias_canonical_ref_id', table_name='import_alias')
    op.create_index(op.f('ix_import_alias_import_alias_canonical_ref_id'), 'import_alias', ['canonical_ref_id'], unique=False)
    _drop_views_for_table("ingestion")
    op.alter_column(
        "ingestion",
        "status",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM(
            "RUNNING",
            "SUCCEEDED",
            "FAILED",
            "SKIPPED",
            name="ingestionstatus",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="status::ingestionstatus",
    )
    op.alter_column('ingestion', 'started_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('ingestion', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_ingestion_source_id', table_name='ingestion')
    op.drop_index('ix_ingestion_status', table_name='ingestion')
    op.create_index(op.f('ix_ingestion_ingestion_source_id'), 'ingestion', ['source_id'], unique=False)
    op.alter_column('ingestion_evidence', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_ingestion_evidence_ingestion_id', table_name='ingestion_evidence')
    op.drop_index('ix_ingestion_evidence_layout_signature', table_name='ingestion_evidence')
    op.drop_index('ix_ingestion_evidence_source_id', table_name='ingestion_evidence')
    op.create_index(op.f('ix_ingestion_evidence_ingestion_evidence_ingestion_id'), 'ingestion_evidence', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_ingestion_evidence_ingestion_evidence_layout_signature'), 'ingestion_evidence', ['layout_signature'], unique=False)
    op.create_index(op.f('ix_ingestion_evidence_ingestion_evidence_source_id'), 'ingestion_evidence', ['source_id'], unique=False)
    op.alter_column('landing_analytics_event', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_landing_analytics_event_ativacao_id', table_name='landing_analytics_event')
    op.drop_index('ix_landing_analytics_event_categoria', table_name='landing_analytics_event')
    op.drop_index('ix_landing_analytics_event_created_at', table_name='landing_analytics_event')
    op.drop_index('ix_landing_analytics_event_cta_variant_id', table_name='landing_analytics_event')
    op.drop_index('ix_landing_analytics_event_event_id', table_name='landing_analytics_event')
    op.drop_index('ix_landing_analytics_event_event_name', table_name='landing_analytics_event')
    op.drop_index('ix_landing_analytics_event_landing_session_id', table_name='landing_analytics_event')
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_ativacao_id'), 'landing_analytics_event', ['ativacao_id'], unique=False)
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_categoria'), 'landing_analytics_event', ['categoria'], unique=False)
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_created_at'), 'landing_analytics_event', ['created_at'], unique=False)
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_cta_variant_id'), 'landing_analytics_event', ['cta_variant_id'], unique=False)
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_event_id'), 'landing_analytics_event', ['event_id'], unique=False)
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_event_name'), 'landing_analytics_event', ['event_name'], unique=False)
    op.create_index(op.f('ix_landing_analytics_event_landing_analytics_event_landing_session_id'), 'landing_analytics_event', ['landing_session_id'], unique=False)
    op.alter_column('lead', 'data_compra',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.drop_index('ix_lead_batch_id', table_name='lead')
    op.drop_index('ix_lead_is_cliente_bb', table_name='lead')
    op.drop_index('ix_lead_is_cliente_estilo', table_name='lead')
    op.drop_constraint('lead_cpf_key', 'lead', type_='unique')
    op.drop_constraint('lead_id_salesforce_key', 'lead', type_='unique')
    op.create_index(op.f('ix_lead_lead_batch_id'), 'lead', ['batch_id'], unique=False)
    op.create_index(op.f('ix_lead_lead_data_criacao'), 'lead', ['data_criacao'], unique=False)
    op.create_index(op.f('ix_lead_lead_is_cliente_bb'), 'lead', ['is_cliente_bb'], unique=False)
    op.create_index(op.f('ix_lead_lead_is_cliente_estilo'), 'lead', ['is_cliente_estilo'], unique=False)
    op.create_unique_constraint(op.f('uq_lead_id_salesforce'), 'lead', ['id_salesforce'])
    op.alter_column(
        "lead_alias",
        "tipo",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM(
            "EVENTO",
            "CIDADE",
            "ESTADO",
            "GENERO",
            name="leadaliastipo",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="tipo::leadaliastipo",
    )
    op.alter_column('lead_batches', 'data_upload',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.execute(sa.text("ALTER TABLE lead_batches ALTER COLUMN stage DROP DEFAULT"))
    op.execute(
        sa.text(
            "ALTER TABLE lead_batches ALTER COLUMN stage TYPE batchstage "
            "USING upper(stage)::batchstage"
        )
    )
    op.execute(sa.text("ALTER TABLE lead_batches ALTER COLUMN stage SET DEFAULT 'BRONZE'::batchstage"))
    op.execute(sa.text("ALTER TABLE lead_batches ALTER COLUMN pipeline_status DROP DEFAULT"))
    op.execute(
        sa.text(
            "ALTER TABLE lead_batches ALTER COLUMN pipeline_status TYPE pipelinestatus "
            "USING upper(replace(pipeline_status, '-', '_'))::pipelinestatus"
        )
    )
    op.execute(sa.text("ALTER TABLE lead_batches ALTER COLUMN pipeline_status SET DEFAULT 'PENDING'::pipelinestatus"))
    op.alter_column('lead_batches', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('lead_batches', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_index('ix_lead_batches_enviado_por', table_name='lead_batches')
    op.drop_index('ix_lead_batches_evento_id', table_name='lead_batches')
    op.drop_index('ix_lead_batches_pipeline_status', table_name='lead_batches')
    op.drop_index('ix_lead_batches_stage', table_name='lead_batches')
    op.create_index(op.f('ix_lead_batches_lead_batches_enviado_por'), 'lead_batches', ['enviado_por'], unique=False)
    op.create_index(op.f('ix_lead_batches_lead_batches_evento_id'), 'lead_batches', ['evento_id'], unique=False)
    op.create_index(op.f('ix_lead_batches_lead_batches_pipeline_status'), 'lead_batches', ['pipeline_status'], unique=False)
    op.alter_column('lead_column_aliases', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_lead_column_aliases_criado_por', table_name='lead_column_aliases')
    op.drop_index('ix_lead_column_aliases_plataforma_origem', table_name='lead_column_aliases')
    op.create_index(op.f('ix_lead_column_aliases_lead_column_aliases_criado_por'), 'lead_column_aliases', ['criado_por'], unique=False)
    op.create_index(op.f('ix_lead_column_aliases_lead_column_aliases_plataforma_origem'), 'lead_column_aliases', ['plataforma_origem'], unique=False)
    op.alter_column(
        "lead_conversao",
        "tipo",
        existing_type=sa.VARCHAR(length=30),
        type_=postgresql.ENUM(
            "COMPRA_INGRESSO",
            "ACAO_EVENTO",
            name="leadconversaotipo",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="tipo::leadconversaotipo",
    )
    op.drop_index('idx_lead_conversao_evento_id', table_name='lead_conversao')
    op.drop_index('idx_lead_conversao_lead_id', table_name='lead_conversao')
    op.drop_index('idx_lead_conversao_tipo', table_name='lead_conversao')
    op.alter_column('lead_import_etl_preview_session', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_lead_import_etl_preview_session_created_at', table_name='lead_import_etl_preview_session')
    op.drop_index('ix_lead_import_etl_preview_session_evento_id', table_name='lead_import_etl_preview_session')
    op.drop_index('ix_lead_import_etl_preview_session_idempotency_key', table_name='lead_import_etl_preview_session')
    op.drop_index('ix_lead_import_etl_preview_session_status', table_name='lead_import_etl_preview_session')
    op.drop_constraint('uq_lead_import_etl_preview_session_idempotency_key', 'lead_import_etl_preview_session', type_='unique')
    op.create_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_idempotency_key'), 'lead_import_etl_preview_session', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_created_at'), 'lead_import_etl_preview_session', ['created_at'], unique=False)
    op.create_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_status'), 'lead_import_etl_preview_session', ['status'], unique=False)
    op.create_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_evento_id'), 'lead_import_etl_preview_session', ['evento_id'], unique=False)
    op.drop_index('ix_lead_reconhecimento_token_token_hash', table_name='lead_reconhecimento_token')
    op.create_index(op.f('ix_lead_reconhecimento_token_lead_reconhecimento_token_token_hash'), 'lead_reconhecimento_token', ['token_hash'], unique=False)
    op.alter_column('leads_silver', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_leads_silver_batch_id', table_name='leads_silver')
    op.drop_index('ix_leads_silver_evento_id', table_name='leads_silver')
    op.drop_index('ix_leads_silver_row_index', table_name='leads_silver')
    op.create_index(op.f('ix_leads_silver_leads_silver_batch_id'), 'leads_silver', ['batch_id'], unique=False)
    op.create_index(op.f('ix_leads_silver_leads_silver_evento_id'), 'leads_silver', ['evento_id'], unique=False)
    op.create_index(op.f('ix_leads_silver_leads_silver_row_index'), 'leads_silver', ['row_index'], unique=False)
    op.alter_column('metric_lineage', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_metric_lineage_ingestion_id', table_name='metric_lineage')
    op.drop_index('ix_metric_lineage_metric_key', table_name='metric_lineage')
    op.drop_index('ix_metric_lineage_source_id', table_name='metric_lineage')
    op.create_index(op.f('ix_metric_lineage_metric_lineage_ingestion_id'), 'metric_lineage', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_metric_lineage_metric_lineage_metric_key'), 'metric_lineage', ['metric_key'], unique=False)
    op.create_index(op.f('ix_metric_lineage_metric_lineage_source_id'), 'metric_lineage', ['source_id'], unique=False)
    op.alter_column('optin_transactions', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_optin_transactions_ingestion_id', table_name='optin_transactions')
    op.drop_index('ix_optin_transactions_lineage_ref_id', table_name='optin_transactions')
    op.drop_index('ix_optin_transactions_person_key_hash', table_name='optin_transactions')
    op.drop_index('ix_optin_transactions_purchase_date', table_name='optin_transactions')
    op.drop_index('ix_optin_transactions_session_id', table_name='optin_transactions')
    op.drop_index('ix_optin_transactions_source_id', table_name='optin_transactions')
    op.drop_index('ix_optin_transactions_ticket_category_norm', table_name='optin_transactions')
    op.create_index(op.f('ix_optin_transactions_optin_transactions_cpf_hash'), 'optin_transactions', ['cpf_hash'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_email_hash'), 'optin_transactions', ['email_hash'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_ingestion_id'), 'optin_transactions', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_person_key_hash'), 'optin_transactions', ['person_key_hash'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_purchase_date'), 'optin_transactions', ['purchase_date'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_session_id'), 'optin_transactions', ['session_id'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_source_id'), 'optin_transactions', ['source_id'], unique=False)
    op.create_index(op.f('ix_optin_transactions_optin_transactions_ticket_category_norm'), 'optin_transactions', ['ticket_category_norm'], unique=False)
    op.execute(
        sa.text(
            "ALTER TABLE optin_transactions DROP CONSTRAINT IF EXISTS "
            "fk_optin_transactions_lineage_ref_id_lineage_refs"
        )
    )
    op.drop_constraint('fk_optin_transactions_source_id_sources', 'optin_transactions', type_='foreignkey')
    op.drop_column('optin_transactions', 'optin_status')
    op.drop_column('optin_transactions', 'optin_flag')
    op.drop_column('optin_transactions', 'lineage_ref_id')
    op.drop_column('optin_transactions', 'qty')
    op.drop_index('ix_password_reset_token_token_hash', table_name='password_reset_token')
    op.drop_index('ix_password_reset_token_usuario_id', table_name='password_reset_token')
    op.drop_constraint('uq_password_reset_token_hash', 'password_reset_token', type_='unique')
    op.create_index(op.f('ix_password_reset_token_password_reset_token_token_hash'), 'password_reset_token', ['token_hash'], unique=True)
    op.create_index(op.f('ix_password_reset_token_password_reset_token_usuario_id'), 'password_reset_token', ['usuario_id'], unique=False)
    op.alter_column('publicity_import_staging', 'imported_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_publicity_import_staging_imported_at', table_name='publicity_import_staging')
    op.drop_index('ix_publicity_import_staging_source_file', table_name='publicity_import_staging')
    op.drop_index('ix_publicity_import_staging_source_row_hash', table_name='publicity_import_staging')
    op.create_index(op.f('ix_publicity_import_staging_publicity_import_staging_imported_at'), 'publicity_import_staging', ['imported_at'], unique=False)
    op.create_index(op.f('ix_publicity_import_staging_publicity_import_staging_source_file'), 'publicity_import_staging', ['source_file'], unique=False)
    op.create_index(op.f('ix_publicity_import_staging_publicity_import_staging_source_row_hash'), 'publicity_import_staging', ['source_row_hash'], unique=False)
    op.alter_column(
        "solicitacao_ingresso",
        "tipo",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM(
            "SELF",
            "TERCEIRO",
            name="solicitacaoingressotipo",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="tipo::solicitacaoingressotipo",
    )
    op.alter_column(
        "solicitacao_ingresso",
        "status",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM(
            "SOLICITADO",
            "CANCELADO",
            name="solicitacaoingressostatus",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="status::solicitacaoingressostatus",
    )
    op.drop_index('idx_solicitacao_cota_id', table_name='solicitacao_ingresso')
    op.drop_index('idx_solicitacao_diretoria_id', table_name='solicitacao_ingresso')
    op.drop_index('idx_solicitacao_evento_id', table_name='solicitacao_ingresso')
    op.drop_index('idx_solicitacao_solicitante_email', table_name='solicitacao_ingresso')
    op.drop_constraint('uq_solicitacao_cota_indicado', 'solicitacao_ingresso', type_='unique')
    op.create_index(op.f('ix_solicitacao_ingresso_solicitacao_ingresso_cota_id'), 'solicitacao_ingresso', ['cota_id'], unique=False)
    op.drop_column('solicitacao_ingresso', 'beneficiario_cpf')
    op.drop_column('solicitacao_ingresso', 'solicitante_area')
    op.drop_column('solicitacao_ingresso', 'beneficiario_email')
    op.drop_column('solicitacao_ingresso', 'solicitante_matricula')
    op.drop_column('solicitacao_ingresso', 'solicitante_nome')
    op.drop_column('solicitacao_ingresso', 'solicitante_area_codigo')
    op.drop_column('solicitacao_ingresso', 'beneficiario_nome')
    op.drop_column('solicitacao_ingresso', 'beneficiario_data_nascimento')
    op.alter_column(
        "source",
        "kind",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM(
            "DOCX",
            "PDF",
            "XLSX",
            "PPTX",
            "CSV",
            "MANUAL",
            "OTHER",
            name="sourcekind",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="kind::sourcekind",
    )
    op.alter_column('source', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('source', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_index('ix_source_kind', table_name='source')
    op.drop_constraint('status_evento_nome_key', 'status_evento', type_='unique')
    op.create_unique_constraint(op.f('uq_status_evento_nome'), 'status_evento', ['nome'])
    op.drop_constraint('tag_nome_key', 'tag', type_='unique')
    op.create_unique_constraint(op.f('uq_tag_nome'), 'tag', ['nome'])
    op.drop_constraint('termo_uso_ativacao_ativacao_id_key', 'termo_uso_ativacao', type_='unique')
    op.create_unique_constraint(op.f('uq_termo_uso_ativacao_ativacao_id'), 'termo_uso_ativacao', ['ativacao_id'])
    op.drop_constraint('territorio_nome_key', 'territorio', type_='unique')
    op.create_unique_constraint(op.f('uq_territorio_nome'), 'territorio', ['nome'])
    op.alter_column(
        "ticket_category_segment_map",
        "segment",
        existing_type=sa.VARCHAR(length=30),
        type_=postgresql.ENUM(
            "CLIENTE_BB",
            "CARTAO_BB",
            "FUNCIONARIO_BB",
            "PUBLICO_GERAL",
            "OUTRO",
            "DESCONHECIDO",
            name="bbrelationshipsegment",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="segment::bbrelationshipsegment",
    )
    op.alter_column('ticket_category_segment_map', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('ticket_category_segment_map', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.drop_index('ix_ticket_category_segment_map_segment', table_name='ticket_category_segment_map')
    op.drop_index('ix_ticket_category_segment_map_ticket_category_norm', table_name='ticket_category_segment_map')
    op.create_index(op.f('ix_ticket_category_segment_map_ticket_category_segment_map_ticket_category_norm'), 'ticket_category_segment_map', ['ticket_category_norm'], unique=False)
    op.create_index(op.f('ix_ticket_category_segment_map_ticket_category_segment_map_segment'), 'ticket_category_segment_map', ['segment'], unique=False)
    op.alter_column('ticket_sales', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.drop_index('ix_ticket_sales_ingestion_id', table_name='ticket_sales')
    op.drop_index('ix_ticket_sales_lineage_ref_id', table_name='ticket_sales')
    op.drop_index('ix_ticket_sales_session_id', table_name='ticket_sales')
    op.drop_index('ix_ticket_sales_source_id', table_name='ticket_sales')
    op.create_index(op.f('ix_ticket_sales_ticket_sales_ingestion_id'), 'ticket_sales', ['ingestion_id'], unique=False)
    op.create_index(op.f('ix_ticket_sales_ticket_sales_session_id'), 'ticket_sales', ['session_id'], unique=False)
    op.create_index(op.f('ix_ticket_sales_ticket_sales_source_id'), 'ticket_sales', ['source_id'], unique=False)
    op.execute(
        sa.text(
            "ALTER TABLE ticket_sales DROP CONSTRAINT IF EXISTS "
            "fk_ticket_sales_lineage_ref_id_lineage_refs"
        )
    )
    op.drop_constraint('fk_ticket_sales_source_id_sources', 'ticket_sales', type_='foreignkey')
    op.drop_column('ticket_sales', 'lineage_ref_id')
    # sources/events: drop only after all FK drops above; CASCADE in the ETL loop would remove these FKs too early.
    op.execute(sa.text('DROP TABLE IF EXISTS "events" CASCADE'))
    op.execute(sa.text('DROP TABLE IF EXISTS "sources" CASCADE'))
    op.drop_constraint('tipo_evento_nome_key', 'tipo_evento', type_='unique')
    op.create_unique_constraint(op.f('uq_tipo_evento_nome'), 'tipo_evento', ['nome'])
    op.alter_column('usuario', 'status_aprovacao',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('usuario', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=True)
    op.drop_constraint('usuario_email_key', 'usuario', type_='unique')
    op.create_unique_constraint(op.f('uq_usuario_email'), 'usuario', ['email'])
    op.drop_constraint('fk_usuario_aprovado_por', 'usuario', type_='foreignkey')
    op.drop_column('usuario', 'aprovado_em')
    op.drop_column('usuario', 'email_confirmacao_enviado')
    op.drop_column('usuario', 'aprovado_por')
    _recreate_mart_dq_views()
    _recreate_mart_report_views()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usuario', sa.Column('aprovado_por', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('usuario', sa.Column('email_confirmacao_enviado', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('usuario', sa.Column('aprovado_em', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_usuario_aprovado_por', 'usuario', 'usuario', ['aprovado_por'], ['id'])
    op.drop_constraint(op.f('uq_usuario_email'), 'usuario', type_='unique')
    op.create_unique_constraint('usuario_email_key', 'usuario', ['email'], postgresql_nulls_not_distinct=False)
    op.alter_column('usuario', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('usuario', 'status_aprovacao',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    op.drop_constraint(op.f('uq_tipo_evento_nome'), 'tipo_evento', type_='unique')
    op.create_unique_constraint('tipo_evento_nome_key', 'tipo_evento', ['nome'], postgresql_nulls_not_distinct=False)
    op.add_column('ticket_sales', sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_ticket_sales_ingestion_id_ingestions', 'ticket_sales', 'ingestions', ['ingestion_id'], ['id'])
    op.create_foreign_key('fk_ticket_sales_source_id_sources', 'ticket_sales', 'sources', ['source_id'], ['source_id'])
    op.create_foreign_key('fk_ticket_sales_lineage_ref_id_lineage_refs', 'ticket_sales', 'lineage_refs', ['lineage_ref_id'], ['id'])
    op.drop_index(op.f('ix_ticket_sales_ticket_sales_source_id'), table_name='ticket_sales')
    op.drop_index(op.f('ix_ticket_sales_ticket_sales_session_id'), table_name='ticket_sales')
    op.drop_index(op.f('ix_ticket_sales_ticket_sales_ingestion_id'), table_name='ticket_sales')
    op.create_index('ix_ticket_sales_source_id', 'ticket_sales', ['source_id'], unique=False)
    op.create_index('ix_ticket_sales_session_id', 'ticket_sales', ['session_id'], unique=False)
    op.create_index('ix_ticket_sales_lineage_ref_id', 'ticket_sales', ['lineage_ref_id'], unique=False)
    op.create_index('ix_ticket_sales_ingestion_id', 'ticket_sales', ['ingestion_id'], unique=False)
    op.alter_column('ticket_sales', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_ticket_category_segment_map_ticket_category_segment_map_segment'), table_name='ticket_category_segment_map')
    op.drop_index(op.f('ix_ticket_category_segment_map_ticket_category_segment_map_ticket_category_norm'), table_name='ticket_category_segment_map')
    op.create_index('ix_ticket_category_segment_map_ticket_category_norm', 'ticket_category_segment_map', ['ticket_category_norm'], unique=False)
    op.create_index('ix_ticket_category_segment_map_segment', 'ticket_category_segment_map', ['segment'], unique=False)
    op.alter_column('ticket_category_segment_map', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('ticket_category_segment_map', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('ticket_category_segment_map', 'segment',
               existing_type=sa.Enum('CLIENTE_BB', 'CARTAO_BB', 'FUNCIONARIO_BB', 'PUBLICO_GERAL', 'OUTRO', 'DESCONHECIDO', name='bbrelationshipsegment'),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    op.drop_constraint(op.f('uq_territorio_nome'), 'territorio', type_='unique')
    op.create_unique_constraint('territorio_nome_key', 'territorio', ['nome'], postgresql_nulls_not_distinct=False)
    op.drop_constraint(op.f('uq_termo_uso_ativacao_ativacao_id'), 'termo_uso_ativacao', type_='unique')
    op.create_unique_constraint('termo_uso_ativacao_ativacao_id_key', 'termo_uso_ativacao', ['ativacao_id'], postgresql_nulls_not_distinct=False)
    op.drop_constraint(op.f('uq_tag_nome'), 'tag', type_='unique')
    op.create_unique_constraint('tag_nome_key', 'tag', ['nome'], postgresql_nulls_not_distinct=False)
    op.drop_constraint(op.f('uq_status_evento_nome'), 'status_evento', type_='unique')
    op.create_unique_constraint('status_evento_nome_key', 'status_evento', ['nome'], postgresql_nulls_not_distinct=False)
    op.create_index('ix_source_kind', 'source', ['kind'], unique=False)
    op.alter_column('source', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('source', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('source', 'kind',
               existing_type=sa.Enum('DOCX', 'PDF', 'XLSX', 'PPTX', 'CSV', 'MANUAL', 'OTHER', name='sourcekind'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    op.add_column('solicitacao_ingresso', sa.Column('beneficiario_data_nascimento', sa.DATE(), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('beneficiario_nome', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('solicitante_area_codigo', sa.VARCHAR(length=40), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('solicitante_nome', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('solicitante_matricula', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('beneficiario_email', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('solicitante_area', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('solicitacao_ingresso', sa.Column('beneficiario_cpf', sa.VARCHAR(length=11), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_solicitacao_ingresso_solicitacao_ingresso_cota_id'), table_name='solicitacao_ingresso')
    op.create_unique_constraint('uq_solicitacao_cota_indicado', 'solicitacao_ingresso', ['cota_id', 'indicado_email'], postgresql_nulls_not_distinct=False)
    op.create_index('idx_solicitacao_solicitante_email', 'solicitacao_ingresso', ['solicitante_email'], unique=False)
    op.create_index('idx_solicitacao_evento_id', 'solicitacao_ingresso', ['evento_id'], unique=False)
    op.create_index('idx_solicitacao_diretoria_id', 'solicitacao_ingresso', ['diretoria_id'], unique=False)
    op.create_index('idx_solicitacao_cota_id', 'solicitacao_ingresso', ['cota_id'], unique=False)
    op.alter_column('solicitacao_ingresso', 'status',
               existing_type=sa.Enum('SOLICITADO', 'CANCELADO', name='solicitacaoingressostatus'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    op.alter_column('solicitacao_ingresso', 'tipo',
               existing_type=sa.Enum('SELF', 'TERCEIRO', name='solicitacaoingressotipo'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    op.drop_index(op.f('ix_publicity_import_staging_publicity_import_staging_source_row_hash'), table_name='publicity_import_staging')
    op.drop_index(op.f('ix_publicity_import_staging_publicity_import_staging_source_file'), table_name='publicity_import_staging')
    op.drop_index(op.f('ix_publicity_import_staging_publicity_import_staging_imported_at'), table_name='publicity_import_staging')
    op.create_index('ix_publicity_import_staging_source_row_hash', 'publicity_import_staging', ['source_row_hash'], unique=False)
    op.create_index('ix_publicity_import_staging_source_file', 'publicity_import_staging', ['source_file'], unique=False)
    op.create_index('ix_publicity_import_staging_imported_at', 'publicity_import_staging', ['imported_at'], unique=False)
    op.alter_column('publicity_import_staging', 'imported_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_password_reset_token_password_reset_token_usuario_id'), table_name='password_reset_token')
    op.drop_index(op.f('ix_password_reset_token_password_reset_token_token_hash'), table_name='password_reset_token')
    op.create_unique_constraint('uq_password_reset_token_hash', 'password_reset_token', ['token_hash'], postgresql_nulls_not_distinct=False)
    op.create_index('ix_password_reset_token_usuario_id', 'password_reset_token', ['usuario_id'], unique=False)
    op.create_index('ix_password_reset_token_token_hash', 'password_reset_token', ['token_hash'], unique=False)
    op.add_column('optin_transactions', sa.Column('qty', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('optin_transactions', sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('optin_transactions', sa.Column('optin_flag', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('optin_transactions', sa.Column('optin_status', sa.VARCHAR(length=80), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_optin_transactions_source_id_sources', 'optin_transactions', 'sources', ['source_id'], ['source_id'])
    op.create_foreign_key('fk_optin_transactions_lineage_ref_id_lineage_refs', 'optin_transactions', 'lineage_refs', ['lineage_ref_id'], ['id'])
    op.create_foreign_key('fk_optin_transactions_ingestion_id_ingestions', 'optin_transactions', 'ingestions', ['ingestion_id'], ['id'])
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_ticket_category_norm'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_source_id'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_session_id'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_purchase_date'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_person_key_hash'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_ingestion_id'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_email_hash'), table_name='optin_transactions')
    op.drop_index(op.f('ix_optin_transactions_optin_transactions_cpf_hash'), table_name='optin_transactions')
    op.create_index('ix_optin_transactions_ticket_category_norm', 'optin_transactions', ['ticket_category_norm'], unique=False)
    op.create_index('ix_optin_transactions_source_id', 'optin_transactions', ['source_id'], unique=False)
    op.create_index('ix_optin_transactions_session_id', 'optin_transactions', ['session_id'], unique=False)
    op.create_index('ix_optin_transactions_purchase_date', 'optin_transactions', ['purchase_date'], unique=False)
    op.create_index('ix_optin_transactions_person_key_hash', 'optin_transactions', ['person_key_hash'], unique=False)
    op.create_index('ix_optin_transactions_lineage_ref_id', 'optin_transactions', ['lineage_ref_id'], unique=False)
    op.create_index('ix_optin_transactions_ingestion_id', 'optin_transactions', ['ingestion_id'], unique=False)
    op.alter_column('optin_transactions', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_metric_lineage_metric_lineage_source_id'), table_name='metric_lineage')
    op.drop_index(op.f('ix_metric_lineage_metric_lineage_metric_key'), table_name='metric_lineage')
    op.drop_index(op.f('ix_metric_lineage_metric_lineage_ingestion_id'), table_name='metric_lineage')
    op.create_index('ix_metric_lineage_source_id', 'metric_lineage', ['source_id'], unique=False)
    op.create_index('ix_metric_lineage_metric_key', 'metric_lineage', ['metric_key'], unique=False)
    op.create_index('ix_metric_lineage_ingestion_id', 'metric_lineage', ['ingestion_id'], unique=False)
    op.alter_column('metric_lineage', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_leads_silver_leads_silver_row_index'), table_name='leads_silver')
    op.drop_index(op.f('ix_leads_silver_leads_silver_evento_id'), table_name='leads_silver')
    op.drop_index(op.f('ix_leads_silver_leads_silver_batch_id'), table_name='leads_silver')
    op.create_index('ix_leads_silver_row_index', 'leads_silver', ['row_index'], unique=False)
    op.create_index('ix_leads_silver_evento_id', 'leads_silver', ['evento_id'], unique=False)
    op.create_index('ix_leads_silver_batch_id', 'leads_silver', ['batch_id'], unique=False)
    op.alter_column('leads_silver', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_lead_reconhecimento_token_lead_reconhecimento_token_token_hash'), table_name='lead_reconhecimento_token')
    op.create_index('ix_lead_reconhecimento_token_token_hash', 'lead_reconhecimento_token', ['token_hash'], unique=False)
    op.drop_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_evento_id'), table_name='lead_import_etl_preview_session')
    op.drop_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_status'), table_name='lead_import_etl_preview_session')
    op.drop_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_created_at'), table_name='lead_import_etl_preview_session')
    op.drop_index(op.f('ix_lead_import_etl_preview_session_lead_import_etl_preview_session_idempotency_key'), table_name='lead_import_etl_preview_session')
    op.create_unique_constraint('uq_lead_import_etl_preview_session_idempotency_key', 'lead_import_etl_preview_session', ['idempotency_key'], postgresql_nulls_not_distinct=False)
    op.create_index('ix_lead_import_etl_preview_session_status', 'lead_import_etl_preview_session', ['status'], unique=False)
    op.create_index('ix_lead_import_etl_preview_session_idempotency_key', 'lead_import_etl_preview_session', ['idempotency_key'], unique=True)
    op.create_index('ix_lead_import_etl_preview_session_evento_id', 'lead_import_etl_preview_session', ['evento_id'], unique=False)
    op.create_index('ix_lead_import_etl_preview_session_created_at', 'lead_import_etl_preview_session', ['created_at'], unique=False)
    op.alter_column('lead_import_etl_preview_session', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.create_index('idx_lead_conversao_tipo', 'lead_conversao', ['tipo'], unique=False)
    op.create_index('idx_lead_conversao_lead_id', 'lead_conversao', ['lead_id'], unique=False)
    op.create_index('idx_lead_conversao_evento_id', 'lead_conversao', ['evento_id'], unique=False)
    op.alter_column('lead_conversao', 'tipo',
               existing_type=sa.Enum('COMPRA_INGRESSO', 'ACAO_EVENTO', name='leadconversaotipo'),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    op.drop_index(op.f('ix_lead_column_aliases_lead_column_aliases_plataforma_origem'), table_name='lead_column_aliases')
    op.drop_index(op.f('ix_lead_column_aliases_lead_column_aliases_criado_por'), table_name='lead_column_aliases')
    op.create_index('ix_lead_column_aliases_plataforma_origem', 'lead_column_aliases', ['plataforma_origem'], unique=False)
    op.create_index('ix_lead_column_aliases_criado_por', 'lead_column_aliases', ['criado_por'], unique=False)
    op.alter_column('lead_column_aliases', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_lead_batches_lead_batches_pipeline_status'), table_name='lead_batches')
    op.drop_index(op.f('ix_lead_batches_lead_batches_evento_id'), table_name='lead_batches')
    op.drop_index(op.f('ix_lead_batches_lead_batches_enviado_por'), table_name='lead_batches')
    op.create_index('ix_lead_batches_stage', 'lead_batches', ['stage'], unique=False)
    op.create_index('ix_lead_batches_pipeline_status', 'lead_batches', ['pipeline_status'], unique=False)
    op.create_index('ix_lead_batches_evento_id', 'lead_batches', ['evento_id'], unique=False)
    op.create_index('ix_lead_batches_enviado_por', 'lead_batches', ['enviado_por'], unique=False)
    op.alter_column('lead_batches', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('lead_batches', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('lead_batches', 'pipeline_status',
               existing_type=sa.Enum('PENDING', 'PASS', 'PASS_WITH_WARNINGS', 'FAIL', name='pipelinestatus'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::character varying"))
    op.alter_column('lead_batches', 'stage',
               existing_type=sa.Enum('BRONZE', 'SILVER', 'GOLD', name='batchstage'),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False,
               existing_server_default=sa.text("'bronze'::character varying"))
    op.alter_column('lead_batches', 'data_upload',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('lead_alias', 'tipo',
               existing_type=sa.Enum('EVENTO', 'CIDADE', 'ESTADO', 'GENERO', name='leadaliastipo'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    op.drop_constraint(op.f('uq_lead_id_salesforce'), 'lead', type_='unique')
    op.drop_index(op.f('ix_lead_lead_is_cliente_estilo'), table_name='lead')
    op.drop_index(op.f('ix_lead_lead_is_cliente_bb'), table_name='lead')
    op.drop_index(op.f('ix_lead_lead_data_criacao'), table_name='lead')
    op.drop_index(op.f('ix_lead_lead_batch_id'), table_name='lead')
    op.create_unique_constraint('lead_id_salesforce_key', 'lead', ['id_salesforce'], postgresql_nulls_not_distinct=False)
    op.create_unique_constraint('lead_cpf_key', 'lead', ['cpf'], postgresql_nulls_not_distinct=False)
    op.create_index('ix_lead_is_cliente_estilo', 'lead', ['is_cliente_estilo'], unique=False)
    op.create_index('ix_lead_is_cliente_bb', 'lead', ['is_cliente_bb'], unique=False)
    op.create_index('ix_lead_batch_id', 'lead', ['batch_id'], unique=False)
    op.alter_column('lead', 'data_compra',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_landing_session_id'), table_name='landing_analytics_event')
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_event_name'), table_name='landing_analytics_event')
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_event_id'), table_name='landing_analytics_event')
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_cta_variant_id'), table_name='landing_analytics_event')
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_created_at'), table_name='landing_analytics_event')
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_categoria'), table_name='landing_analytics_event')
    op.drop_index(op.f('ix_landing_analytics_event_landing_analytics_event_ativacao_id'), table_name='landing_analytics_event')
    op.create_index('ix_landing_analytics_event_landing_session_id', 'landing_analytics_event', ['landing_session_id'], unique=False)
    op.create_index('ix_landing_analytics_event_event_name', 'landing_analytics_event', ['event_name'], unique=False)
    op.create_index('ix_landing_analytics_event_event_id', 'landing_analytics_event', ['event_id'], unique=False)
    op.create_index('ix_landing_analytics_event_cta_variant_id', 'landing_analytics_event', ['cta_variant_id'], unique=False)
    op.create_index('ix_landing_analytics_event_created_at', 'landing_analytics_event', ['created_at'], unique=False)
    op.create_index('ix_landing_analytics_event_categoria', 'landing_analytics_event', ['categoria'], unique=False)
    op.create_index('ix_landing_analytics_event_ativacao_id', 'landing_analytics_event', ['ativacao_id'], unique=False)
    op.alter_column('landing_analytics_event', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_ingestion_evidence_ingestion_evidence_source_id'), table_name='ingestion_evidence')
    op.drop_index(op.f('ix_ingestion_evidence_ingestion_evidence_layout_signature'), table_name='ingestion_evidence')
    op.drop_index(op.f('ix_ingestion_evidence_ingestion_evidence_ingestion_id'), table_name='ingestion_evidence')
    op.create_index('ix_ingestion_evidence_source_id', 'ingestion_evidence', ['source_id'], unique=False)
    op.create_index('ix_ingestion_evidence_layout_signature', 'ingestion_evidence', ['layout_signature'], unique=False)
    op.create_index('ix_ingestion_evidence_ingestion_id', 'ingestion_evidence', ['ingestion_id'], unique=False)
    op.alter_column('ingestion_evidence', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_ingestion_ingestion_source_id'), table_name='ingestion')
    op.create_index('ix_ingestion_status', 'ingestion', ['status'], unique=False)
    op.create_index('ix_ingestion_source_id', 'ingestion', ['source_id'], unique=False)
    op.alter_column('ingestion', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('ingestion', 'started_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    _drop_views_for_table("ingestion")
    op.alter_column('ingestion', 'status',
               existing_type=sa.Enum('RUNNING', 'SUCCEEDED', 'FAILED', 'SKIPPED', name='ingestionstatus'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    op.drop_index(op.f('ix_import_alias_import_alias_canonical_ref_id'), table_name='import_alias')
    op.create_index('ix_import_alias_canonical_ref_id', 'import_alias', ['canonical_ref_id'], unique=False)
    op.alter_column('import_alias', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('import_alias', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.create_index('ix_gamificacao_evento_id', 'gamificacao', ['evento_id'], unique=False)
    op.add_column('funcionario', sa.Column('area', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('funcionario', sa.Column('area_codigo', sa.VARCHAR(length=40), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('uq_funcionario_email'), 'funcionario', type_='unique')
    op.drop_constraint(op.f('uq_funcionario_chave_c'), 'funcionario', type_='unique')
    op.create_unique_constraint('funcionario_email_key', 'funcionario', ['email'], postgresql_nulls_not_distinct=False)
    op.create_unique_constraint('funcionario_chave_c_key', 'funcionario', ['chave_c'], postgresql_nulls_not_distinct=False)
    op.drop_constraint(op.f('uq_formulario_landing_template_nome'), 'formulario_landing_template', type_='unique')
    op.create_unique_constraint('formulario_landing_template_nome_key', 'formulario_landing_template', ['nome'], postgresql_nulls_not_distinct=False)
    op.drop_index(op.f('ix_festival_leads_festival_leads_source_id'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_session_id'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_person_key_hash'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_lead_created_date'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_ingestion_id'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_event_id'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_email_hash'), table_name='festival_leads')
    op.drop_index(op.f('ix_festival_leads_festival_leads_cpf_hash'), table_name='festival_leads')
    op.create_index('ix_festival_leads_source_id', 'festival_leads', ['source_id'], unique=False)
    op.create_index('ix_festival_leads_session_id', 'festival_leads', ['session_id'], unique=False)
    op.create_index('ix_festival_leads_person_key_hash', 'festival_leads', ['person_key_hash'], unique=False)
    op.create_index('ix_festival_leads_lead_created_date', 'festival_leads', ['lead_created_date'], unique=False)
    op.create_index('ix_festival_leads_ingestion_id', 'festival_leads', ['ingestion_id'], unique=False)
    op.create_index('ix_festival_leads_event_id', 'festival_leads', ['event_id'], unique=False)
    op.alter_column('festival_leads', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_evento_landing_customization_audit_evento_landing_customization_audit_event_id'), table_name='evento_landing_customization_audit')
    op.drop_index(op.f('ix_evento_landing_customization_audit_evento_landing_customization_audit_changed_by_user_id'), table_name='evento_landing_customization_audit')
    op.create_index('ix_evento_landing_customization_audit_event_id', 'evento_landing_customization_audit', ['event_id'], unique=False)
    op.create_index('ix_evento_landing_customization_audit_changed_by_user_id', 'evento_landing_customization_audit', ['changed_by_user_id'], unique=False)
    op.alter_column('evento_landing_customization_audit', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_index(op.f('ix_evento_evento_external_project_code'), table_name='evento')
    op.drop_index(op.f('ix_evento_evento_estado'), table_name='evento')
    op.drop_index(op.f('ix_evento_evento_cidade'), table_name='evento')
    op.create_index('ix_evento_external_project_code', 'evento', ['external_project_code'], unique=False)
    op.alter_column('evento', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_index(op.f('ix_event_sessions_event_sessions_source_of_truth_source_id'), table_name='event_sessions')
    op.drop_index(op.f('ix_event_sessions_event_sessions_session_type'), table_name='event_sessions')
    op.drop_index(op.f('ix_event_sessions_event_sessions_session_key'), table_name='event_sessions')
    op.drop_index(op.f('ix_event_sessions_event_sessions_session_date'), table_name='event_sessions')
    op.drop_index(op.f('ix_event_sessions_event_sessions_event_id'), table_name='event_sessions')
    op.create_unique_constraint('uq_event_sessions_session_key', 'event_sessions', ['session_key'], postgresql_nulls_not_distinct=False)
    op.create_index('ix_event_sessions_source_of_truth_source_id', 'event_sessions', ['source_of_truth_source_id'], unique=False)
    op.create_index('ix_event_sessions_session_type', 'event_sessions', ['session_type'], unique=False)
    op.create_index('ix_event_sessions_session_date', 'event_sessions', ['session_date'], unique=False)
    op.create_index('ix_event_sessions_event_id', 'event_sessions', ['event_id'], unique=False)
    op.alter_column('event_sessions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('event_sessions', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    _drop_views_for_table("event_sessions")
    op.alter_column('event_sessions', 'session_type',
               existing_type=sa.Enum('DIURNO_GRATUITO', 'NOTURNO_SHOW', 'OUTRO', name='eventsessiontype'),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    op.drop_index(op.f('ix_event_publicity_event_publicity_linked_at'), table_name='event_publicity')
    op.drop_index(op.f('ix_event_publicity_event_publicity_event_id'), table_name='event_publicity')
    op.create_index('ix_event_publicity_linked_at', 'event_publicity', ['linked_at'], unique=False)
    op.create_index('ix_event_publicity_event_id', 'event_publicity', ['event_id'], unique=False)
    op.alter_column('event_publicity', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('event_publicity', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_constraint(op.f('uq_divisao_demandante_nome'), 'divisao_demandante', type_='unique')
    op.create_unique_constraint('divisao_demandante_nome_key', 'divisao_demandante', ['nome'], postgresql_nulls_not_distinct=False)
    op.drop_constraint(op.f('uq_diretoria_nome'), 'diretoria', type_='unique')
    op.create_unique_constraint('diretoria_nome_key', 'diretoria', ['nome'], postgresql_nulls_not_distinct=False)
    _drop_views_for_table("data_quality_result")
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_status'), table_name='data_quality_result')
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_source_id'), table_name='data_quality_result')
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_severity'), table_name='data_quality_result')
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_session_id'), table_name='data_quality_result')
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_scope'), table_name='data_quality_result')
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_ingestion_id'), table_name='data_quality_result')
    op.drop_index(op.f('ix_data_quality_result_data_quality_result_check_key'), table_name='data_quality_result')
    op.create_index('ix_data_quality_result_status', 'data_quality_result', ['status'], unique=False)
    op.create_index('ix_data_quality_result_source_id', 'data_quality_result', ['source_id'], unique=False)
    op.create_index('ix_data_quality_result_severity', 'data_quality_result', ['severity'], unique=False)
    op.create_index('ix_data_quality_result_session_id', 'data_quality_result', ['session_id'], unique=False)
    op.create_index('ix_data_quality_result_scope', 'data_quality_result', ['scope'], unique=False)
    op.create_index('ix_data_quality_result_ingestion_id', 'data_quality_result', ['ingestion_id'], unique=False)
    op.create_index('ix_data_quality_result_check_key', 'data_quality_result', ['check_key'], unique=False)
    op.alter_column('data_quality_result', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('data_quality_result', 'status',
               existing_type=sa.Enum('PASS', 'FAIL', 'SKIP', name='dataqualitystatus'),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False)
    op.alter_column('data_quality_result', 'severity',
               existing_type=sa.Enum('WARN', 'ERROR', name='dataqualityseverity'),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False)
    op.alter_column('data_quality_result', 'scope',
               existing_type=sa.Enum('STAGING', 'CANONICAL', 'MARTS', name='dataqualityscope'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    op.drop_constraint(op.f('uq_cupom_codigo'), 'cupom', type_='unique')
    op.create_unique_constraint('cupom_codigo_key', 'cupom', ['codigo'], postgresql_nulls_not_distinct=False)
    op.add_column('cota_cortesia', sa.Column('alterado_em', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('cota_cortesia', sa.Column('alterado_por', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('cota_cortesia', sa.Column('valor_novo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('cota_cortesia', sa.Column('valor_anterior', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_cota_cortesia_alterado_por_usuario', 'cota_cortesia', 'usuario', ['alterado_por'], ['id'])
    op.drop_constraint(op.f('uq_cota_cortesia_evento_id'), 'cota_cortesia', type_='unique')
    op.drop_index(op.f('ix_cota_cortesia_cota_cortesia_diretoria_id'), table_name='cota_cortesia')
    op.drop_constraint(op.f('uq_convidado_email'), 'convidado', type_='unique')
    op.drop_constraint(op.f('uq_convidado_cpf'), 'convidado', type_='unique')
    op.create_unique_constraint('convidado_email_key', 'convidado', ['email'], postgresql_nulls_not_distinct=False)
    op.create_unique_constraint('convidado_cpf_key', 'convidado', ['cpf'], postgresql_nulls_not_distinct=False)
    op.alter_column('conversao_ativacao', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.add_column('attendance_access_control', sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_attendance_access_control_lineage_ref_id_lineage_refs', 'attendance_access_control', 'lineage_refs', ['lineage_ref_id'], ['id'])
    op.create_foreign_key('fk_attendance_access_control_ingestion_id_ingestions', 'attendance_access_control', 'ingestions', ['ingestion_id'], ['id'])
    op.create_foreign_key('fk_attendance_access_control_source_id_sources', 'attendance_access_control', 'sources', ['source_id'], ['source_id'])
    op.drop_index(op.f('ix_attendance_access_control_attendance_access_control_session_id'), table_name='attendance_access_control')
    op.drop_index(op.f('ix_attendance_access_control_attendance_access_control_source_id'), table_name='attendance_access_control')
    op.drop_index(op.f('ix_attendance_access_control_attendance_access_control_ingestion_id'), table_name='attendance_access_control')
    op.create_index('ix_attendance_access_control_source_id', 'attendance_access_control', ['source_id'], unique=False)
    op.create_index('ix_attendance_access_control_session_id', 'attendance_access_control', ['session_id'], unique=False)
    op.create_index('ix_attendance_access_control_lineage_ref_id', 'attendance_access_control', ['lineage_ref_id'], unique=False)
    op.create_index('ix_attendance_access_control_ingestion_id', 'attendance_access_control', ['ingestion_id'], unique=False)
    op.alter_column('attendance_access_control', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.drop_constraint(op.f('fk_ativacao_lead_gamificacao_id_gamificacao'), 'ativacao_lead', type_='foreignkey')
    op.create_foreign_key('fk_ativacao_lead_gamificacao_id', 'ativacao_lead', 'gamificacao', ['gamificacao_id'], ['id'], ondelete='SET NULL')
    op.drop_index(op.f('ix_ativacao_lead_ativacao_lead_lead_id'), table_name='ativacao_lead')
    op.create_index('ix_ativacao_lead_gamificacao_id', 'ativacao_lead', ['gamificacao_id'], unique=False)
    op.create_index('ix_ativacao_gamificacao_id', 'ativacao', ['gamificacao_id'], unique=False)
    op.alter_column('ativacao', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=False)
    op.create_table('dq_inconsistency',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('check_id', sa.VARCHAR(length=220), autoincrement=False, nullable=False),
    sa.Column('dataset_id', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('metric_key', sa.VARCHAR(length=220), autoincrement=False, nullable=False),
    sa.Column('unit', sa.VARCHAR(length=40), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('severity', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('values_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('sources_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('lineage_refs_json', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('evidence_json', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('suggested_action', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.CheckConstraint("severity::text = ANY (ARRAY['info'::character varying, 'warning'::character varying, 'error'::character varying]::text[])", name='ck_dq_inconsistency_ck_dq_inconsistency_severity_domain'),
    sa.CheckConstraint("status::text = 'inconsistente'::text", name='ck_dq_inconsistency_ck_dq_inconsistency_status_domain'),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_dq_inconsistency_ingestion_id_ingestions'),
    sa.PrimaryKeyConstraint('id', name='pk_dq_inconsistency')
    )
    op.create_index('ix_dq_inconsistency_status', 'dq_inconsistency', ['status'], unique=False)
    op.create_index('ix_dq_inconsistency_severity', 'dq_inconsistency', ['severity'], unique=False)
    op.create_index('ix_dq_inconsistency_metric_key', 'dq_inconsistency', ['metric_key'], unique=False)
    op.create_index('ix_dq_inconsistency_ingestion_id', 'dq_inconsistency', ['ingestion_id'], unique=False)
    op.create_index('ix_dq_inconsistency_dataset_id', 'dq_inconsistency', ['dataset_id'], unique=False)
    op.create_index('ix_dq_inconsistency_check_id', 'dq_inconsistency', ['check_id'], unique=False)
    op.create_table('dq_check_result',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=True),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('check_id', sa.VARCHAR(length=220), autoincrement=False, nullable=False),
    sa.Column('severity', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('message', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('details_json', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.CheckConstraint("severity::text = ANY (ARRAY['info'::character varying, 'warning'::character varying, 'error'::character varying]::text[])", name='ck_dq_check_result_ck_dq_check_result_severity_domain'),
    sa.CheckConstraint("status::text = ANY (ARRAY['pass'::character varying, 'fail'::character varying, 'skip'::character varying]::text[])", name='ck_dq_check_result_ck_dq_check_result_status_domain'),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_dq_check_result_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_dq_check_result_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_dq_check_result_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_dq_check_result')
    )
    op.create_index('ix_dq_check_result_status', 'dq_check_result', ['status'], unique=False)
    op.create_index('ix_dq_check_result_source_id', 'dq_check_result', ['source_id'], unique=False)
    op.create_index('ix_dq_check_result_severity', 'dq_check_result', ['severity'], unique=False)
    op.create_index('ix_dq_check_result_lineage_ref_id', 'dq_check_result', ['lineage_ref_id'], unique=False)
    op.create_index('ix_dq_check_result_ingestion_id', 'dq_check_result', ['ingestion_id'], unique=False)
    op.create_index('ix_dq_check_result_check_id', 'dq_check_result', ['check_id'], unique=False)
    op.create_table('stg_lead_actions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('lead_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('action_order', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('action_raw', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('action_norm', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_lead_actions_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lead_id'], ['stg_leads.id'], name='fk_stg_lead_actions_lead_id_stg_leads'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_lead_actions_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_lead_actions_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_lead_actions'),
    sa.UniqueConstraint('lead_id', 'action_norm', name='uq_stg_lead_actions_lead_action_norm', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_lead_actions_source_id', 'stg_lead_actions', ['source_id'], unique=False)
    op.create_index('ix_stg_lead_actions_lineage_ref_id', 'stg_lead_actions', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_lead_actions_lead_id', 'stg_lead_actions', ['lead_id'], unique=False)
    op.create_index('ix_stg_lead_actions_ingestion_id', 'stg_lead_actions', ['ingestion_id'], unique=False)
    op.create_index('ix_stg_lead_actions_action_norm', 'stg_lead_actions', ['action_norm'], unique=False)
    op.create_table('stg_optin_transactions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sheet_name', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('header_row', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('row_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('source_range', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('evento', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('sessao', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('dt_hr_compra', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('opt_in', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('opt_in_id', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('opt_in_status', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('canal_venda', sa.VARCHAR(length=160), autoincrement=False, nullable=True),
    sa.Column('metodo_entrega', sa.VARCHAR(length=160), autoincrement=False, nullable=True),
    sa.Column('ingresso', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('qtd_ingresso', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('cpf_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('email_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('raw_payload_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('session_resolution_finding', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_optin_transactions_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_optin_transactions_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['session_id'], ['event_sessions.id'], name='fk_stg_optin_transactions_session_id_event_sessions'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_optin_transactions_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_optin_transactions'),
    sa.UniqueConstraint('source_id', 'sheet_name', 'row_number', name='uq_stg_optin_source_sheet_row', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_optin_transactions_source_id', 'stg_optin_transactions', ['source_id'], unique=False)
    op.create_index('ix_stg_optin_transactions_sheet_name', 'stg_optin_transactions', ['sheet_name'], unique=False)
    op.create_index('ix_stg_optin_transactions_session_id', 'stg_optin_transactions', ['session_id'], unique=False)
    op.create_index('ix_stg_optin_transactions_lineage_ref_id', 'stg_optin_transactions', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_optin_transactions_ingestion_id', 'stg_optin_transactions', ['ingestion_id'], unique=False)
    op.create_index('ix_stg_optin_transactions_event_id', 'stg_optin_transactions', ['event_id'], unique=False)
    op.create_index('ix_stg_optin_transactions_email_hash', 'stg_optin_transactions', ['email_hash'], unique=False)
    op.create_index('ix_stg_optin_transactions_cpf_hash', 'stg_optin_transactions', ['cpf_hash'], unique=False)
    op.create_table('lineage_refs',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('lineage_refs_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('location_type', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('location_value', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('evidence_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.CheckConstraint("location_type::text = ANY (ARRAY['page'::character varying, 'slide'::character varying, 'sheet'::character varying, 'range'::character varying]::text[])", name='ck_lineage_refs_ck_lineage_refs_location_type_domain'),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_lineage_refs_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_lineage_refs_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_lineage_refs'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_lineage_refs_source_id', 'lineage_refs', ['source_id'], unique=False)
    op.create_index('ix_lineage_refs_location_type', 'lineage_refs', ['location_type'], unique=False)
    op.create_index('ix_lineage_refs_ingestion_id', 'lineage_refs', ['ingestion_id'], unique=False)
    op.create_table('events',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('event_key', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('event_name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('event_start_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('event_end_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_events'),
    sa.UniqueConstraint('event_key', name='uq_events_event_key', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_events_event_name', 'events', ['event_name'], unique=False)
    op.create_index('ix_events_event_key', 'events', ['event_key'], unique=False)
    op.create_table('sources',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('sources_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('kind', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('uri', sa.VARCHAR(length=800), autoincrement=False, nullable=False),
    sa.Column('display_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('file_sha256', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('file_size_bytes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('file_mtime_utc', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_sources'),
    sa.UniqueConstraint('source_id', name='uq_sources_source_id', postgresql_include=[], postgresql_nulls_not_distinct=False),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_sources_source_id', 'sources', ['source_id'], unique=False)
    op.create_index('ix_sources_kind', 'sources', ['kind'], unique=False)
    op.create_table('stg_social_metrics',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('slide_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('slide_title', sa.VARCHAR(length=400), autoincrement=False, nullable=True),
    sa.Column('location_value', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('platform', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('metric_name', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('metric_value', sa.NUMERIC(precision=20, scale=6), autoincrement=False, nullable=False),
    sa.Column('metric_value_raw', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('unit', sa.VARCHAR(length=40), autoincrement=False, nullable=False),
    sa.Column('evidence_label', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('evidence_text', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('extraction_rule', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('raw_payload_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('session_resolution_finding', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_social_metrics_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_social_metrics_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['session_id'], ['event_sessions.id'], name='fk_stg_social_metrics_session_id_event_sessions'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_social_metrics_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_social_metrics'),
    sa.UniqueConstraint('source_id', 'ingestion_id', 'platform', 'metric_name', 'slide_number', name='uq_stg_social_metrics_source_ingestion_metric_slide', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_social_metrics_source_id', 'stg_social_metrics', ['source_id'], unique=False)
    op.create_index('ix_stg_social_metrics_slide_number', 'stg_social_metrics', ['slide_number'], unique=False)
    op.create_index('ix_stg_social_metrics_session_id', 'stg_social_metrics', ['session_id'], unique=False)
    op.create_index('ix_stg_social_metrics_platform', 'stg_social_metrics', ['platform'], unique=False)
    op.create_index('ix_stg_social_metrics_metric_name', 'stg_social_metrics', ['metric_name'], unique=False)
    op.create_index('ix_stg_social_metrics_lineage_ref_id', 'stg_social_metrics', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_social_metrics_ingestion_id', 'stg_social_metrics', ['ingestion_id'], unique=False)
    op.create_index('ix_stg_social_metrics_event_id', 'stg_social_metrics', ['event_id'], unique=False)
    op.create_table('stg_leads',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sheet_name', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('header_row', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('row_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('source_range', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('evento', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('data_criacao', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('sexo', sa.VARCHAR(length=40), autoincrement=False, nullable=True),
    sa.Column('estado', sa.VARCHAR(length=40), autoincrement=False, nullable=True),
    sa.Column('cidade', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('interesses', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('area_atuacao', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('cpf_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('email_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('person_key_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('cpf_promotor_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('nome_promotor', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('acoes_raw', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('raw_payload_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_leads_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_leads_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_leads_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_leads'),
    sa.UniqueConstraint('source_id', 'sheet_name', 'row_number', name='uq_stg_leads_source_sheet_row', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_leads_source_id', 'stg_leads', ['source_id'], unique=False)
    op.create_index('ix_stg_leads_sheet_name', 'stg_leads', ['sheet_name'], unique=False)
    op.create_index('ix_stg_leads_person_key_hash', 'stg_leads', ['person_key_hash'], unique=False)
    op.create_index('ix_stg_leads_lineage_ref_id', 'stg_leads', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_leads_ingestion_id', 'stg_leads', ['ingestion_id'], unique=False)
    op.create_index('ix_stg_leads_email_hash', 'stg_leads', ['email_hash'], unique=False)
    op.create_index('ix_stg_leads_cpf_promotor_hash', 'stg_leads', ['cpf_promotor_hash'], unique=False)
    op.create_index('ix_stg_leads_cpf_hash', 'stg_leads', ['cpf_hash'], unique=False)
    op.create_table('ingestions',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('ingestions_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('source_pk', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('extractor_name', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
    sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('finished_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('records_read', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('records_loaded', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('file_sha256', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('file_size_bytes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('log_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.CheckConstraint("status::text = ANY (ARRAY['SUCCESS'::character varying, 'FAILED'::character varying, 'PARTIAL'::character varying]::text[])", name='ck_ingestions_ck_ingestions_status_domain'),
    sa.ForeignKeyConstraint(['source_pk'], ['sources.id'], name='fk_ingestions_source_pk_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_ingestions'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_ingestions_status', 'ingestions', ['status'], unique=False)
    op.create_index('ix_ingestions_started_at', 'ingestions', ['started_at'], unique=False)
    op.create_index('ix_ingestions_source_pk', 'ingestions', ['source_pk'], unique=False)
    op.create_table('stg_dimac_metrics',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('metric_key', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('metric_label', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('metric_value', sa.NUMERIC(precision=20, scale=6), autoincrement=False, nullable=True),
    sa.Column('metric_value_raw', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('unit', sa.VARCHAR(length=40), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=8), autoincrement=False, nullable=False),
    sa.Column('gap_reason', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('pdf_page', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('location_value', sa.VARCHAR(length=40), autoincrement=False, nullable=True),
    sa.Column('evidence_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('extraction_rule', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('raw_payload_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.CheckConstraint("status::text = ANY (ARRAY['ok'::character varying, 'gap'::character varying]::text[])", name='ck_stg_dimac_metrics_ck_stg_dimac_metrics_status_domain'),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_dimac_metrics_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_dimac_metrics_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_dimac_metrics_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_dimac_metrics'),
    sa.UniqueConstraint('source_id', 'ingestion_id', 'metric_key', name='uq_stg_dimac_source_ingestion_metric', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_dimac_metrics_status', 'stg_dimac_metrics', ['status'], unique=False)
    op.create_index('ix_stg_dimac_metrics_source_id', 'stg_dimac_metrics', ['source_id'], unique=False)
    op.create_index('ix_stg_dimac_metrics_pdf_page', 'stg_dimac_metrics', ['pdf_page'], unique=False)
    op.create_index('ix_stg_dimac_metrics_metric_key', 'stg_dimac_metrics', ['metric_key'], unique=False)
    op.create_index('ix_stg_dimac_metrics_lineage_ref_id', 'stg_dimac_metrics', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_dimac_metrics_ingestion_id', 'stg_dimac_metrics', ['ingestion_id'], unique=False)
    op.create_table('stg_mtc_metrics',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('metric_key', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('metric_label', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('metric_value', sa.NUMERIC(precision=20, scale=6), autoincrement=False, nullable=True),
    sa.Column('metric_value_raw', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('unit', sa.VARCHAR(length=40), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=8), autoincrement=False, nullable=False),
    sa.Column('gap_reason', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('pdf_page', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('location_value', sa.VARCHAR(length=40), autoincrement=False, nullable=True),
    sa.Column('evidence_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('extraction_rule', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('raw_payload_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.CheckConstraint("status::text = ANY (ARRAY['ok'::character varying, 'gap'::character varying]::text[])", name='ck_stg_mtc_metrics_ck_stg_mtc_metrics_status_domain'),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_mtc_metrics_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_mtc_metrics_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_mtc_metrics_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_mtc_metrics'),
    sa.UniqueConstraint('source_id', 'ingestion_id', 'metric_key', name='uq_stg_mtc_source_ingestion_metric', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_mtc_metrics_status', 'stg_mtc_metrics', ['status'], unique=False)
    op.create_index('ix_stg_mtc_metrics_source_id', 'stg_mtc_metrics', ['source_id'], unique=False)
    op.create_index('ix_stg_mtc_metrics_pdf_page', 'stg_mtc_metrics', ['pdf_page'], unique=False)
    op.create_index('ix_stg_mtc_metrics_metric_key', 'stg_mtc_metrics', ['metric_key'], unique=False)
    op.create_index('ix_stg_mtc_metrics_lineage_ref_id', 'stg_mtc_metrics', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_mtc_metrics_ingestion_id', 'stg_mtc_metrics', ['ingestion_id'], unique=False)
    op.create_table('stg_access_control_sessions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(length=160), autoincrement=False, nullable=False),
    sa.Column('ingestion_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lineage_ref_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('pdf_page', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('session_name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('ingressos_validos', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('invalidos', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('bloqueados', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('presentes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ausentes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('comparecimento_pct', sa.NUMERIC(precision=7, scale=4), autoincrement=False, nullable=True),
    sa.Column('table_header', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('evidence_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('raw_payload_json', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('session_resolution_finding', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ingestion_id'], ['ingestions.id'], name='fk_stg_access_control_sessions_ingestion_id_ingestions'),
    sa.ForeignKeyConstraint(['lineage_ref_id'], ['lineage_refs.id'], name='fk_stg_access_control_sessions_lineage_ref_id_lineage_refs'),
    sa.ForeignKeyConstraint(['session_id'], ['event_sessions.id'], name='fk_stg_access_control_sessions_session_id_event_sessions'),
    sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], name='fk_stg_access_control_sessions_source_id_sources'),
    sa.PrimaryKeyConstraint('id', name='pk_stg_access_control_sessions'),
    sa.UniqueConstraint('source_id', 'ingestion_id', 'pdf_page', 'session_name', name='uq_stg_access_control_source_ingestion_page_session', postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index('ix_stg_access_control_sessions_source_id', 'stg_access_control_sessions', ['source_id'], unique=False)
    op.create_index('ix_stg_access_control_sessions_session_name', 'stg_access_control_sessions', ['session_name'], unique=False)
    op.create_index('ix_stg_access_control_sessions_session_id', 'stg_access_control_sessions', ['session_id'], unique=False)
    op.create_index('ix_stg_access_control_sessions_pdf_page', 'stg_access_control_sessions', ['pdf_page'], unique=False)
    op.create_index('ix_stg_access_control_sessions_lineage_ref_id', 'stg_access_control_sessions', ['lineage_ref_id'], unique=False)
    op.create_index('ix_stg_access_control_sessions_ingestion_id', 'stg_access_control_sessions', ['ingestion_id'], unique=False)
    op.create_index('ix_stg_access_control_sessions_event_id', 'stg_access_control_sessions', ['event_id'], unique=False)
    op.drop_index(op.f('ix_lead_evento_lead_evento_source_ref_id'), table_name='lead_evento')
    op.drop_index(op.f('ix_lead_evento_lead_evento_source_kind'), table_name='lead_evento')
    op.drop_index(op.f('ix_lead_evento_lead_evento_lead_id'), table_name='lead_evento')
    op.drop_index(op.f('ix_lead_evento_lead_evento_evento_id'), table_name='lead_evento')
    op.drop_table('lead_evento')
    op.drop_table('agent_execution')
    op.drop_table('framework_task')
    op.drop_table('framework_issue')
    op.drop_table('framework_sprint')
    op.drop_table('framework_epic')
    op.drop_table('framework_phase')
    op.drop_table('framework_prd')
    op.drop_table('framework_intake')
    op.drop_index(op.f('ix_framework_project_framework_project_canonical_name'), table_name='framework_project')
    op.drop_table('framework_project')
    # ### end Alembic commands ###
