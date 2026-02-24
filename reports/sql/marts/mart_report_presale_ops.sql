-- TMJ-ETL-058: indicadores operacionais de pre-venda (opt-in aceitos) por sessao.
DROP VIEW IF EXISTS mart_report_presale_ops;

CREATE VIEW mart_report_presale_ops AS
WITH tx_base AS (
  SELECT
    es.event_id AS event_id,
    es.id AS session_id,
    es.session_key AS session_key,
    es.session_name AS session_name,
    CAST(es.session_type AS TEXT) AS session_type,
    CAST(es.session_date AS TEXT) AS session_date,
    CAST(es.session_start_at AS TEXT) AS session_start_at,
    ot.id AS tx_id,
    CAST(COALESCE(ot.ticket_qty, 0) AS INTEGER) AS ticket_qty,
    CAST(COALESCE(ot.purchase_date, DATE(ot.purchase_at)) AS TEXT) AS purchase_day,
    CASE
      WHEN TRIM(COALESCE(ot.person_key_hash, '')) <> '' THEN TRIM(ot.person_key_hash)
      ELSE NULL
    END AS person_key_hash
  FROM event_sessions es
  LEFT JOIN optin_transactions ot ON ot.session_id = es.id
),
session_agg AS (
  SELECT
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at,
    COUNT(tx_id) AS tx_count_total,
    SUM(COALESCE(ticket_qty, 0)) AS tickets_qty_total,
    COUNT(DISTINCT person_key_hash) AS buyers_unique_total,
    MIN(purchase_day) AS purchase_day_first,
    MAX(purchase_day) AS purchase_day_last
  FROM tx_base
  GROUP BY
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at
),
buyer_rollup AS (
  SELECT
    session_id,
    person_key_hash,
    COUNT(tx_id) AS tx_count_by_buyer
  FROM tx_base
  WHERE tx_id IS NOT NULL
    AND person_key_hash IS NOT NULL
  GROUP BY session_id, person_key_hash
),
buyer_multi AS (
  SELECT
    session_id,
    SUM(CASE WHEN tx_count_by_buyer > 1 THEN 1 ELSE 0 END) AS buyers_multi_purchase_count
  FROM buyer_rollup
  GROUP BY session_id
),
ranked AS (
  SELECT
    a.event_id,
    a.session_id,
    a.session_key,
    a.session_name,
    a.session_type,
    a.session_date,
    a.session_start_at,
    CAST(COALESCE(a.tx_count_total, 0) AS INTEGER) AS tx_count_total,
    CAST(COALESCE(a.tickets_qty_total, 0) AS INTEGER) AS tickets_qty_total,
    CAST(COALESCE(a.buyers_unique_total, 0) AS INTEGER) AS buyers_unique_total,
    CAST(a.purchase_day_first AS TEXT) AS purchase_day_first,
    CAST(a.purchase_day_last AS TEXT) AS purchase_day_last,
    CAST(
      CASE
        WHEN COALESCE(a.tx_count_total, 0) > 0
        THEN ROUND((COALESCE(a.tickets_qty_total, 0) * 1.0) / a.tx_count_total, 4)
        ELSE NULL
      END AS REAL
    ) AS avg_tickets_per_tx,
    CAST(
      CASE
        WHEN COALESCE(a.buyers_unique_total, 0) > 0
        THEN ROUND((COALESCE(a.tickets_qty_total, 0) * 1.0) / a.buyers_unique_total, 4)
        ELSE NULL
      END AS REAL
    ) AS avg_tickets_per_buyer,
    CAST(COALESCE(m.buyers_multi_purchase_count, 0) AS INTEGER) AS buyers_multi_purchase_count,
    CAST(
      CASE
        WHEN COALESCE(a.buyers_unique_total, 0) > 0
        THEN ROUND((COALESCE(m.buyers_multi_purchase_count, 0) * 100.0) / a.buyers_unique_total, 4)
        ELSE NULL
      END AS REAL
    ) AS buyers_multi_purchase_pct,
    CAST(CASE WHEN COALESCE(a.buyers_unique_total, 0) > 0 THEN 1 ELSE 0 END AS INTEGER) AS has_person_key,
    CAST('optin_aceitos' AS TEXT) AS metric_type,
    CAST('optin_aceitos' AS TEXT) AS audience_measure,
    CAST(
      'Indicadores operacionais sobre recorte de opt-in aceitos (nao substitui vendidos totais).' AS TEXT
    ) AS recorte_observacao,
    CAST(
      ROW_NUMBER() OVER (
        ORDER BY
          a.session_date,
          COALESCE(a.session_start_at, a.session_date || ' 00:00:00'),
          a.session_id
      ) AS INTEGER
    ) AS session_rank
  FROM session_agg a
  LEFT JOIN buyer_multi m ON m.session_id = a.session_id
)
SELECT
  event_id,
  session_id,
  session_key,
  session_name,
  session_type,
  session_date,
  session_start_at,
  tx_count_total,
  tickets_qty_total,
  buyers_unique_total,
  purchase_day_first,
  purchase_day_last,
  avg_tickets_per_tx,
  avg_tickets_per_buyer,
  buyers_multi_purchase_count,
  buyers_multi_purchase_pct,
  has_person_key,
  metric_type,
  audience_measure,
  recorte_observacao,
  session_rank
FROM ranked
ORDER BY session_rank;
