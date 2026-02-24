"""Add TMJ canonical tables (sessions + facts) and marts/views.

Revision ID: 7e3c2b1a9f0d
Revises: 0668e4b00eb0
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7e3c2b1a9f0d"
down_revision = "0668e4b00eb0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("session_key", sa.String(length=120), nullable=False),
        sa.Column("session_name", sa.String(length=200), nullable=False),
        sa.Column("session_type", sa.String(length=30), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("session_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("session_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_of_truth_source_id", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["source_of_truth_source_id"], ["source.source_id"]),
        sa.UniqueConstraint("session_key", name="uq_event_sessions_session_key"),
    )
    op.create_index("ix_event_sessions_event_id", "event_sessions", ["event_id"], unique=False)
    op.create_index("ix_event_sessions_session_type", "event_sessions", ["session_type"], unique=False)
    op.create_index("ix_event_sessions_session_date", "event_sessions", ["session_date"], unique=False)
    op.create_index(
        "ix_event_sessions_source_of_truth_source_id",
        "event_sessions",
        ["source_of_truth_source_id"],
        unique=False,
    )

    op.create_table(
        "attendance_access_control",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("ingressos_validos", sa.Integer(), nullable=True),
        sa.Column("invalidos", sa.Integer(), nullable=True),
        sa.Column("bloqueados", sa.Integer(), nullable=True),
        sa.Column("presentes", sa.Integer(), nullable=True),
        sa.Column("ausentes", sa.Integer(), nullable=True),
        sa.Column("comparecimento_pct", sa.Numeric(7, 4), nullable=True),
        sa.Column("pdf_page", sa.Integer(), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
        sa.UniqueConstraint(
            "source_id",
            "session_id",
            name="uq_attendance_access_control_source_session",
        ),
    )
    op.create_index(
        "ix_attendance_access_control_session_id",
        "attendance_access_control",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_attendance_access_control_source_id",
        "attendance_access_control",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "ix_attendance_access_control_ingestion_id",
        "attendance_access_control",
        ["ingestion_id"],
        unique=False,
    )

    op.create_table(
        "optin_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("sheet_name", sa.String(length=120), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("purchase_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("opt_in_text", sa.String(length=200), nullable=True),
        sa.Column("opt_in_id", sa.String(length=80), nullable=True),
        sa.Column("opt_in_status", sa.String(length=80), nullable=True),
        sa.Column("sales_channel", sa.String(length=160), nullable=True),
        sa.Column("delivery_method", sa.String(length=160), nullable=True),
        sa.Column("ticket_category_raw", sa.String(length=200), nullable=True),
        sa.Column("ticket_category_norm", sa.String(length=200), nullable=True),
        sa.Column("ticket_qty", sa.Integer(), nullable=True),
        sa.Column("cpf_hash", sa.String(length=64), nullable=True),
        sa.Column("email_hash", sa.String(length=64), nullable=True),
        sa.Column("person_key_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
        sa.UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_optin_transactions_source_sheet_row",
        ),
    )
    op.create_index("ix_optin_transactions_session_id", "optin_transactions", ["session_id"], unique=False)
    op.create_index("ix_optin_transactions_source_id", "optin_transactions", ["source_id"], unique=False)
    op.create_index("ix_optin_transactions_ingestion_id", "optin_transactions", ["ingestion_id"], unique=False)
    op.create_index("ix_optin_transactions_purchase_date", "optin_transactions", ["purchase_date"], unique=False)
    op.create_index(
        "ix_optin_transactions_ticket_category_norm",
        "optin_transactions",
        ["ticket_category_norm"],
        unique=False,
    )
    op.create_index("ix_optin_transactions_person_key_hash", "optin_transactions", ["person_key_hash"], unique=False)

    op.create_table(
        "ticket_category_segment_map",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ticket_category_raw", sa.String(length=200), nullable=False),
        sa.Column("ticket_category_norm", sa.String(length=200), nullable=False),
        sa.Column("segment", sa.String(length=30), nullable=False),
        sa.Column("inferred", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("inference_rule", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "ticket_category_norm",
            name="uq_ticket_category_segment_map_ticket_category_norm",
        ),
    )
    op.create_index(
        "ix_ticket_category_segment_map_ticket_category_norm",
        "ticket_category_segment_map",
        ["ticket_category_norm"],
        unique=False,
    )
    op.create_index(
        "ix_ticket_category_segment_map_segment",
        "ticket_category_segment_map",
        ["segment"],
        unique=False,
    )

    op.create_table(
        "ticket_sales",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("sold_total", sa.Integer(), nullable=True),
        sa.Column("refunded_total", sa.Integer(), nullable=True),
        sa.Column("net_sold_total", sa.Integer(), nullable=True),
        sa.Column("location_raw", sa.String(length=200), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
        sa.UniqueConstraint("source_id", "session_id", name="uq_ticket_sales_source_session"),
    )
    op.create_index("ix_ticket_sales_session_id", "ticket_sales", ["session_id"], unique=False)
    op.create_index("ix_ticket_sales_source_id", "ticket_sales", ["source_id"], unique=False)
    op.create_index("ix_ticket_sales_ingestion_id", "ticket_sales", ["ingestion_id"], unique=False)

    op.create_table(
        "festival_leads",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("sheet_name", sa.String(length=120), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("lead_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lead_created_date", sa.Date(), nullable=True),
        sa.Column("cpf_hash", sa.String(length=64), nullable=True),
        sa.Column("email_hash", sa.String(length=64), nullable=True),
        sa.Column("person_key_hash", sa.String(length=64), nullable=True),
        sa.Column("sexo", sa.String(length=40), nullable=True),
        sa.Column("estado", sa.String(length=40), nullable=True),
        sa.Column("cidade", sa.String(length=120), nullable=True),
        sa.Column("acoes", sa.Text(), nullable=True),
        sa.Column("interesses", sa.Text(), nullable=True),
        sa.Column("area_atuacao", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["event_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.source_id"]),
        sa.ForeignKeyConstraint(["ingestion_id"], ["ingestion.id"]),
        sa.UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_festival_leads_source_sheet_row",
        ),
    )
    op.create_index("ix_festival_leads_event_id", "festival_leads", ["event_id"], unique=False)
    op.create_index("ix_festival_leads_session_id", "festival_leads", ["session_id"], unique=False)
    op.create_index("ix_festival_leads_source_id", "festival_leads", ["source_id"], unique=False)
    op.create_index("ix_festival_leads_ingestion_id", "festival_leads", ["ingestion_id"], unique=False)
    op.create_index("ix_festival_leads_lead_created_date", "festival_leads", ["lead_created_date"], unique=False)
    op.create_index("ix_festival_leads_person_key_hash", "festival_leads", ["person_key_hash"], unique=False)

    # -------------------------
    # marts/views (report-ready)
    # -------------------------
    op.execute("DROP VIEW IF EXISTS mart_report_session_coverage")
    op.execute("DROP VIEW IF EXISTS mart_report_sales_curve_cum")
    op.execute("DROP VIEW IF EXISTS mart_report_sales_curve_daily")
    op.execute("DROP VIEW IF EXISTS mart_report_bb_share_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_optin_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_attendance_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_leads_by_day")
    op.execute("DROP VIEW IF EXISTS mart_report_audience_ruler_by_session")

    op.execute(
        """
CREATE VIEW mart_report_attendance_by_session AS
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

    op.execute(
        """
CREATE VIEW mart_report_optin_by_session AS
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

    op.execute(
        """
CREATE VIEW mart_report_bb_share_by_session AS
WITH base AS (
  SELECT
    es.id AS session_id,
    es.session_key,
    es.session_date,
    COALESCE(m.segment, 'DESCONHECIDO') AS segment,
    SUM(COALESCE(ot.ticket_qty, 0)) AS tickets_qty
  FROM event_sessions es
  LEFT JOIN optin_transactions ot ON ot.session_id = es.id
  LEFT JOIN ticket_category_segment_map m ON m.ticket_category_norm = ot.ticket_category_norm
  GROUP BY es.id, es.session_key, es.session_date, COALESCE(m.segment, 'DESCONHECIDO')
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

    op.execute(
        """
CREATE VIEW mart_report_sales_curve_daily AS
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

    op.execute(
        """
CREATE VIEW mart_report_sales_curve_cum AS
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

    op.execute(
        """
CREATE VIEW mart_report_leads_by_day AS
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

    op.execute(
        """
CREATE VIEW mart_report_audience_ruler_by_session AS
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

    op.execute(
        """
CREATE VIEW mart_report_session_coverage AS
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


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS mart_report_session_coverage")
    op.execute("DROP VIEW IF EXISTS mart_report_audience_ruler_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_sales_curve_cum")
    op.execute("DROP VIEW IF EXISTS mart_report_sales_curve_daily")
    op.execute("DROP VIEW IF EXISTS mart_report_bb_share_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_optin_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_attendance_by_session")
    op.execute("DROP VIEW IF EXISTS mart_report_leads_by_day")

    op.drop_index("ix_festival_leads_person_key_hash", table_name="festival_leads")
    op.drop_index("ix_festival_leads_lead_created_date", table_name="festival_leads")
    op.drop_index("ix_festival_leads_ingestion_id", table_name="festival_leads")
    op.drop_index("ix_festival_leads_source_id", table_name="festival_leads")
    op.drop_index("ix_festival_leads_session_id", table_name="festival_leads")
    op.drop_index("ix_festival_leads_event_id", table_name="festival_leads")
    op.drop_table("festival_leads")

    op.drop_index("ix_ticket_sales_ingestion_id", table_name="ticket_sales")
    op.drop_index("ix_ticket_sales_source_id", table_name="ticket_sales")
    op.drop_index("ix_ticket_sales_session_id", table_name="ticket_sales")
    op.drop_table("ticket_sales")

    op.drop_index("ix_ticket_category_segment_map_segment", table_name="ticket_category_segment_map")
    op.drop_index(
        "ix_ticket_category_segment_map_ticket_category_norm",
        table_name="ticket_category_segment_map",
    )
    op.drop_table("ticket_category_segment_map")

    op.drop_index("ix_optin_transactions_person_key_hash", table_name="optin_transactions")
    op.drop_index(
        "ix_optin_transactions_ticket_category_norm",
        table_name="optin_transactions",
    )
    op.drop_index("ix_optin_transactions_purchase_date", table_name="optin_transactions")
    op.drop_index("ix_optin_transactions_ingestion_id", table_name="optin_transactions")
    op.drop_index("ix_optin_transactions_source_id", table_name="optin_transactions")
    op.drop_index("ix_optin_transactions_session_id", table_name="optin_transactions")
    op.drop_table("optin_transactions")

    op.drop_index("ix_attendance_access_control_ingestion_id", table_name="attendance_access_control")
    op.drop_index("ix_attendance_access_control_source_id", table_name="attendance_access_control")
    op.drop_index("ix_attendance_access_control_session_id", table_name="attendance_access_control")
    op.drop_table("attendance_access_control")

    op.drop_index(
        "ix_event_sessions_source_of_truth_source_id",
        table_name="event_sessions",
    )
    op.drop_index("ix_event_sessions_session_date", table_name="event_sessions")
    op.drop_index("ix_event_sessions_session_type", table_name="event_sessions")
    op.drop_index("ix_event_sessions_event_id", table_name="event_sessions")
    op.drop_table("event_sessions")
