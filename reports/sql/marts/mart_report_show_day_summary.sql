-- TMJ-ETL-098: resumo por dia de show com status por regua e rastreabilidade minima.
DROP VIEW IF EXISTS mart_report_show_day_summary;

CREATE VIEW mart_report_show_day_summary AS
WITH expected_days AS (
  SELECT '2025-12-12' AS dia
  UNION ALL SELECT '2025-12-13'
  UNION ALL SELECT '2025-12-14'
),
show_sessions AS (
  SELECT
    ed.dia AS dia,
    es.event_id AS event_id,
    es.id AS session_id,
    CAST(es.session_key AS TEXT) AS session_key,
    CAST(es.session_name AS TEXT) AS session_name,
    CAST(es.session_type AS TEXT) AS session_type,
    CAST(es.session_date AS TEXT) AS session_date,
    CAST(es.session_start_at AS TEXT) AS session_start_at,
    ROW_NUMBER() OVER (
      PARTITION BY ed.dia
      ORDER BY
        COALESCE(CAST(es.session_start_at AS TEXT), CAST(es.session_date AS TEXT) || ' 00:00:00'),
        es.id
    ) AS session_pick_rank
  FROM expected_days ed
  LEFT JOIN event_sessions es
    ON CAST(es.session_date AS TEXT) = ed.dia
    AND UPPER(CAST(es.session_type AS TEXT)) = 'NOTURNO_SHOW'
),
picked_sessions AS (
  SELECT
    dia,
    event_id,
    session_id,
    session_key,
    session_name,
    session_type,
    session_date,
    session_start_at
  FROM show_sessions
  WHERE session_pick_rank = 1
),
access_fact AS (
  SELECT
    session_id,
    CAST(COUNT(*) AS INTEGER) AS row_count,
    CAST(SUM(COALESCE(presentes, 0)) AS INTEGER) AS entradas_validadas,
    CAST(MAX(ingressos_validos) AS INTEGER) AS ingressos_validos,
    CAST(GROUP_CONCAT(DISTINCT source_id) AS TEXT) AS source_ids
  FROM attendance_access_control
  GROUP BY session_id
),
optin_fact AS (
  SELECT
    session_id,
    CAST(COUNT(*) AS INTEGER) AS row_count,
    CAST(GROUP_CONCAT(DISTINCT source_id) AS TEXT) AS source_ids
  FROM optin_transactions
  GROUP BY session_id
),
sales_fact AS (
  SELECT
    session_id,
    CAST(COUNT(*) AS INTEGER) AS row_count,
    CAST(MAX(sold_total) AS INTEGER) AS sold_total,
    CAST(MAX(net_sold_total) AS INTEGER) AS net_sold_total,
    CAST(GROUP_CONCAT(DISTINCT source_id) AS TEXT) AS source_ids
  FROM ticket_sales
  GROUP BY session_id
),
latest_source_runs AS (
  SELECT
    s.id AS source_pk,
    CAST(s.source_id AS TEXT) AS source_id,
    UPPER(
      TRIM(
        COALESCE(CAST(s.source_id AS TEXT), '')
        || ' '
        || COALESCE(CAST(s.uri AS TEXT), '')
        || ' '
        || COALESCE(CAST(i.extractor_name AS TEXT), '')
      )
    ) AS source_blob,
    UPPER(CAST(COALESCE(i.status, '') AS TEXT)) AS latest_status,
    ROW_NUMBER() OVER (
      PARTITION BY s.id
      ORDER BY i.started_at DESC, i.id DESC
    ) AS run_rank
  FROM sources s
  LEFT JOIN ingestions i ON i.source_pk = s.id
),
classified_sources AS (
  SELECT
    source_id,
    latest_status,
    CASE
      WHEN source_blob LIKE '%ACESSO%'
        OR source_blob LIKE '%ACCESS%'
        OR source_blob LIKE '%CATRACA%'
        OR source_blob LIKE '%TURNSTILE%'
      THEN 'access_control'
      WHEN source_blob LIKE '%VENDA%'
        OR source_blob LIKE '%VENDAS%'
        OR source_blob LIKE '%SALE%'
        OR source_blob LIKE '%SALES%'
        OR source_blob LIKE '%SOLD%'
      THEN 'ticket_sales'
      WHEN source_blob LIKE '%OPTIN%'
        OR source_blob LIKE '%OPT_IN%'
      THEN 'optin'
      ELSE NULL
    END AS dataset_key,
    CASE
      WHEN source_blob LIKE '%2025-12-12%'
        OR source_blob LIKE '%20251212%'
        OR source_blob LIKE '%12/12%'
        OR source_blob LIKE '%DOZE%'
      THEN '2025-12-12'
      WHEN source_blob LIKE '%2025-12-13%'
        OR source_blob LIKE '%20251213%'
        OR source_blob LIKE '%13/12%'
        OR source_blob LIKE '%TREZE%'
      THEN '2025-12-13'
      WHEN source_blob LIKE '%2025-12-14%'
        OR source_blob LIKE '%20251214%'
        OR source_blob LIKE '%14/12%'
        OR source_blob LIKE '%QUATORZE%'
      THEN '2025-12-14'
      ELSE NULL
    END AS dia
  FROM latest_source_runs
  WHERE run_rank = 1
),
candidate_source_agg AS (
  SELECT
    dia,
    dataset_key,
    CAST(COUNT(*) AS INTEGER) AS candidate_count,
    CAST(MAX(CASE WHEN latest_status = 'FAILED' THEN 1 ELSE 0 END) AS INTEGER) AS has_failed,
    CAST(MAX(CASE WHEN latest_status = 'PARTIAL' THEN 1 ELSE 0 END) AS INTEGER) AS has_partial,
    CAST(MAX(CASE WHEN latest_status = 'SUCCESS' THEN 1 ELSE 0 END) AS INTEGER) AS has_success,
    CAST(GROUP_CONCAT(DISTINCT source_id) AS TEXT) AS source_ids
  FROM classified_sources
  WHERE dataset_key IS NOT NULL
    AND dia IS NOT NULL
  GROUP BY dia, dataset_key
),
base AS (
  SELECT
    ps.dia AS dia,
    ps.event_id AS event_id,
    ps.session_id AS session_id,
    CAST(COALESCE(ps.session_name, ps.session_key, 'SHOW_' || REPLACE(ps.dia, '-', '')) AS TEXT) AS sessao,
    CAST(COALESCE(ps.session_key, 'TMJ2025_' || REPLACE(ps.dia, '-', '') || '_SHOW') AS TEXT) AS session_key,
    CAST(COALESCE(ps.session_type, 'NOTURNO_SHOW') AS TEXT) AS session_type,
    CAST(ps.session_start_at AS TEXT) AS session_start_at,
    CAST(COALESCE(af.entradas_validadas, 0) AS INTEGER) AS entradas_validadas,
    CAST(COALESCE(af.ingressos_validos, 0) AS INTEGER) AS ingressos_validos,
    CAST(COALESCE(ofc.row_count, 0) AS INTEGER) AS optin_tx_count,
    CAST(COALESCE(sf.sold_total, 0) AS INTEGER) AS sold_total,
    CAST(COALESCE(sf.net_sold_total, 0) AS INTEGER) AS net_sold_total,
    CAST(COALESCE(af.source_ids, cas.source_ids, '') AS TEXT) AS source_ids_access_control,
    CAST(COALESCE(ofc.source_ids, cos.source_ids, '') AS TEXT) AS source_ids_optin,
    CAST(COALESCE(sf.source_ids, cts.source_ids, '') AS TEXT) AS source_ids_ticket_sales,
    CAST(
      CASE
        WHEN ps.session_id IS NULL THEN 'gap'
        WHEN COALESCE(af.row_count, 0) > 0 THEN 'ok'
        WHEN COALESCE(cas.candidate_count, 0) = 0 THEN 'gap'
        ELSE 'partial'
      END AS TEXT
    ) AS status_access_control,
    CAST(
      CASE
        WHEN ps.session_id IS NULL THEN 'gap'
        WHEN COALESCE(ofc.row_count, 0) > 0 THEN 'ok'
        WHEN COALESCE(cos.candidate_count, 0) = 0 THEN 'partial'
        ELSE 'partial'
      END AS TEXT
    ) AS status_optin,
    CAST(
      CASE
        WHEN ps.session_id IS NULL THEN 'gap'
        WHEN COALESCE(sf.row_count, 0) > 0 THEN 'ok'
        WHEN COALESCE(cts.candidate_count, 0) = 0 THEN 'gap'
        ELSE 'partial'
      END AS TEXT
    ) AS status_ticket_sales
  FROM picked_sessions ps
  LEFT JOIN access_fact af ON af.session_id = ps.session_id
  LEFT JOIN optin_fact ofc ON ofc.session_id = ps.session_id
  LEFT JOIN sales_fact sf ON sf.session_id = ps.session_id
  LEFT JOIN candidate_source_agg cas
    ON cas.dia = ps.dia
    AND cas.dataset_key = 'access_control'
  LEFT JOIN candidate_source_agg cos
    ON cos.dia = ps.dia
    AND cos.dataset_key = 'optin'
  LEFT JOIN candidate_source_agg cts
    ON cts.dia = ps.dia
    AND cts.dataset_key = 'ticket_sales'
),
ranked AS (
  SELECT
    dia,
    event_id,
    session_id,
    sessao,
    session_key,
    session_type,
    session_start_at,
    status_access_control,
    status_optin,
    status_ticket_sales,
    entradas_validadas,
    ingressos_validos,
    optin_tx_count,
    sold_total,
    net_sold_total,
    source_ids_access_control,
    source_ids_optin,
    source_ids_ticket_sales,
    CAST(
      TRIM(
        COALESCE(
          (CASE WHEN session_id IS NULL THEN 'sessao_show_ausente_no_catalogo; ' ELSE '' END) ||
          (CASE WHEN status_access_control <> 'ok' THEN 'falta_entradas_validadas; ' ELSE '' END) ||
          (CASE WHEN status_optin <> 'ok' THEN 'falta_optin_aceitos_recorte; ' ELSE '' END) ||
          (CASE WHEN status_ticket_sales <> 'ok' THEN 'falta_vendidos_total; ' ELSE '' END)
        , '')
      ) AS TEXT
    ) AS observacoes,
    CAST(
      ROW_NUMBER() OVER (
        ORDER BY dia, session_key
      ) AS INTEGER
    ) AS row_rank
  FROM base
)
SELECT
  CAST(dia AS TEXT) AS dia,
  CAST(event_id AS INTEGER) AS event_id,
  CAST(session_id AS INTEGER) AS session_id,
  CAST(sessao AS TEXT) AS sessao,
  CAST(session_key AS TEXT) AS session_key,
  CAST(session_type AS TEXT) AS session_type,
  CAST(session_start_at AS TEXT) AS session_start_at,
  CAST(status_access_control AS TEXT) AS status_access_control,
  CAST(status_optin AS TEXT) AS status_optin,
  CAST(status_ticket_sales AS TEXT) AS status_ticket_sales,
  CAST(entradas_validadas AS INTEGER) AS entradas_validadas,
  CAST(ingressos_validos AS INTEGER) AS ingressos_validos,
  CAST(optin_tx_count AS INTEGER) AS optin_tx_count,
  CAST(sold_total AS INTEGER) AS sold_total,
  CAST(net_sold_total AS INTEGER) AS net_sold_total,
  CAST(source_ids_access_control AS TEXT) AS source_ids_access_control,
  CAST(source_ids_optin AS TEXT) AS source_ids_optin,
  CAST(source_ids_ticket_sales AS TEXT) AS source_ids_ticket_sales,
  CAST(observacoes AS TEXT) AS observacoes,
  CAST(row_rank AS INTEGER) AS row_rank
FROM ranked
ORDER BY row_rank;
