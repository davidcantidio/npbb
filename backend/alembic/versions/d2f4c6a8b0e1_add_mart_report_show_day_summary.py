"""Add mart_report_show_day_summary (TMJ 2025 shows coverage).

Revision ID: d2f4c6a8b0e1
Revises: c9d4a1b2e3f4
Create Date: 2026-02-10
"""

from alembic import op


revision = "d2f4c6a8b0e1"
down_revision = "c9d4a1b2e3f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS mart_report_show_day_summary")
    op.execute(
        """
CREATE VIEW mart_report_show_day_summary AS
WITH expected AS (
  -- Keep as ISO text to be portable across SQLite and Postgres.
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


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS mart_report_show_day_summary")
