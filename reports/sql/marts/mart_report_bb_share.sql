-- TMJ-ETL-059: share por segmento BB (proxy via categoria de ingresso em opt-in).
DROP VIEW IF EXISTS mart_report_bb_share;

CREATE VIEW mart_report_bb_share AS
WITH tx_base AS (
  SELECT
    es.event_id AS event_id,
    es.id AS session_id,
    es.session_key AS session_key,
    es.session_name AS session_name,
    CAST(es.session_type AS TEXT) AS session_type,
    CAST(es.session_date AS TEXT) AS session_date,
    CAST(es.session_start_at AS TEXT) AS session_start_at,
    CASE
      WHEN UPPER(COALESCE(tmap.segment, 'DESCONHECIDO')) IN (
        'CLIENTE_BB',
        'CARTAO_BB',
        'FUNCIONARIO_BB',
        'PUBLICO_GERAL',
        'OUTRO',
        'DESCONHECIDO'
      )
      THEN UPPER(COALESCE(tmap.segment, 'DESCONHECIDO'))
      ELSE 'DESCONHECIDO'
    END AS segment_canonical,
    CAST(COALESCE(ot.ticket_qty, 0) AS INTEGER) AS tickets_qty,
    ot.id AS tx_id,
    CASE
      WHEN TRIM(COALESCE(ot.person_key_hash, '')) <> '' THEN TRIM(ot.person_key_hash)
      ELSE NULL
    END AS person_key_hash,
    ot.source_id AS source_id
  FROM optin_transactions ot
  JOIN event_sessions es ON es.id = ot.session_id
  LEFT JOIN ticket_category_segment_map tmap
    ON tmap.ticket_category_norm = ot.ticket_category_norm
),
segment_agg AS (
  SELECT
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at,
    segment_canonical,
    COUNT(tx_id) AS tx_count,
    SUM(COALESCE(tickets_qty, 0)) AS tickets_qty,
    COUNT(DISTINCT person_key_hash) AS buyers_unique,
    GROUP_CONCAT(DISTINCT source_id) AS source_ids
  FROM tx_base
  GROUP BY
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at,
    segment_canonical
),
session_tot AS (
  SELECT
    session_id,
    SUM(tickets_qty) AS tickets_qty_total
  FROM segment_agg
  GROUP BY session_id
),
ranked AS (
  SELECT
    s.event_id,
    s.session_id,
    s.session_key,
    s.session_name,
    s.session_type,
    s.session_date,
    s.session_start_at,
    CAST(s.segment_canonical AS TEXT) AS segment_canonical,
    CAST(s.tx_count AS INTEGER) AS tx_count,
    CAST(s.tickets_qty AS INTEGER) AS tickets_qty,
    CAST(s.buyers_unique AS INTEGER) AS buyers_unique,
    CAST(t.tickets_qty_total AS INTEGER) AS tickets_qty_total,
    CAST(
      CASE
        WHEN COALESCE(t.tickets_qty_total, 0) > 0
        THEN ROUND((s.tickets_qty * 100.0) / t.tickets_qty_total, 4)
        ELSE NULL
      END AS REAL
    ) AS share_pct,
    CAST(COALESCE(s.source_ids, '') AS TEXT) AS source_ids,
    CAST('optin_aceitos' AS TEXT) AS metric_type,
    CAST('optin_aceitos' AS TEXT) AS audience_measure,
    CAST(
      'Proxy de relacionamento BB por categoria de ingresso (recorte de opt-in aceitos).' AS TEXT
    ) AS recorte_observacao,
    CAST(
      ROW_NUMBER() OVER (
        ORDER BY
          s.session_date,
          COALESCE(s.session_start_at, s.session_date || ' 00:00:00'),
          s.session_id,
          s.segment_canonical
      ) AS INTEGER
    ) AS row_rank
  FROM segment_agg s
  JOIN session_tot t ON t.session_id = s.session_id
)
SELECT
  event_id,
  session_id,
  session_key,
  session_name,
  session_type,
  session_date,
  session_start_at,
  segment_canonical,
  tx_count,
  tickets_qty,
  buyers_unique,
  tickets_qty_total,
  share_pct,
  source_ids,
  metric_type,
  audience_measure,
  recorte_observacao,
  row_rank
FROM ranked
ORDER BY row_rank;
