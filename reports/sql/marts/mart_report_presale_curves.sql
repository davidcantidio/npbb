-- TMJ-ETL-058: pre-venda (opt-in aceitos) curva diaria e acumulada por sessao.
DROP VIEW IF EXISTS mart_report_presale_curves;

CREATE VIEW mart_report_presale_curves AS
WITH base_tx AS (
  SELECT
    es.event_id AS event_id,
    es.id AS session_id,
    es.session_key AS session_key,
    es.session_name AS session_name,
    CAST(es.session_type AS TEXT) AS session_type,
    CAST(es.session_date AS TEXT) AS session_date,
    CAST(es.session_start_at AS TEXT) AS session_start_at,
    CAST(COALESCE(ot.purchase_date, DATE(ot.purchase_at)) AS TEXT) AS purchase_day,
    ot.id AS tx_id,
    CAST(COALESCE(ot.ticket_qty, 0) AS INTEGER) AS tickets_qty,
    CASE
      WHEN TRIM(COALESCE(ot.person_key_hash, '')) <> '' THEN TRIM(ot.person_key_hash)
      ELSE NULL
    END AS person_key_hash
  FROM optin_transactions ot
  JOIN event_sessions es ON es.id = ot.session_id
  WHERE COALESCE(ot.purchase_date, DATE(ot.purchase_at)) IS NOT NULL
),
daily AS (
  SELECT
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at,
    purchase_day,
    COUNT(tx_id) AS tx_count_day,
    SUM(COALESCE(tickets_qty, 0)) AS tickets_qty_day,
    COUNT(DISTINCT person_key_hash) AS buyers_unique_day
  FROM base_tx
  GROUP BY
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at,
    purchase_day
),
ranked AS (
  SELECT
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at,
    purchase_day,
    CAST(tx_count_day AS INTEGER) AS tx_count_day,
    CAST(tickets_qty_day AS INTEGER) AS tickets_qty_day,
    CAST(buyers_unique_day AS INTEGER) AS buyers_unique_day,
    CAST(
      SUM(tickets_qty_day) OVER (
        PARTITION BY session_id
        ORDER BY purchase_day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS INTEGER
    ) AS tickets_qty_cum,
    CAST(
      SUM(tx_count_day) OVER (
        PARTITION BY session_id
        ORDER BY purchase_day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS INTEGER
    ) AS tx_count_cum,
    CAST('optin_aceitos' AS TEXT) AS metric_type,
    CAST('optin_aceitos' AS TEXT) AS audience_measure,
    CAST(
      'Recorte de pre-venda por opt-in aceitos (nao representa vendidos totais).' AS TEXT
    ) AS recorte_observacao,
    CAST(
      ROW_NUMBER() OVER (
        ORDER BY
          session_date,
          COALESCE(session_start_at, session_date || ' 00:00:00'),
          session_id,
          purchase_day
      ) AS INTEGER
    ) AS row_rank
  FROM daily
)
SELECT
  event_id,
  session_id,
  session_key,
  session_name,
  session_type,
  session_date,
  session_start_at,
  purchase_day,
  tx_count_day,
  tickets_qty_day,
  buyers_unique_day,
  tickets_qty_cum,
  tx_count_cum,
  metric_type,
  audience_measure,
  recorte_observacao,
  row_rank
FROM ranked
ORDER BY row_rank;
