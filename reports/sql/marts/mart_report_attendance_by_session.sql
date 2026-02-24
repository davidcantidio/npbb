-- TMJ-ETL-057: attendance by session (controle de acesso / entradas validadas).
DROP VIEW IF EXISTS mart_report_attendance_by_session;

CREATE VIEW mart_report_attendance_by_session AS
WITH attendance_agg AS (
  SELECT
    ac.session_id AS session_id,
    SUM(COALESCE(ac.ingressos_validos, 0)) AS ingressos_validos,
    SUM(COALESCE(ac.presentes, 0)) AS presentes,
    SUM(COALESCE(ac.ausentes, 0)) AS ausentes,
    SUM(COALESCE(ac.invalidos, 0)) AS invalidos,
    SUM(COALESCE(ac.bloqueados, 0)) AS bloqueados
  FROM attendance_access_control ac
  GROUP BY ac.session_id
),
ranked AS (
  SELECT
    es.event_id AS event_id,
    es.id AS session_id,
    es.session_key AS session_key,
    es.session_name AS session_name,
    CAST(es.session_type AS TEXT) AS session_type,
    CAST(es.session_date AS TEXT) AS session_date,
    CAST(es.session_start_at AS TEXT) AS session_start_at,
    CAST(COALESCE(att.ingressos_validos, 0) AS INTEGER) AS ingressos_validos,
    CAST(COALESCE(att.presentes, 0) AS INTEGER) AS presentes,
    CAST(COALESCE(att.ausentes, 0) AS INTEGER) AS ausentes,
    CAST(COALESCE(att.invalidos, 0) AS INTEGER) AS invalidos,
    CAST(COALESCE(att.bloqueados, 0) AS INTEGER) AS bloqueados,
    CAST(
      CASE
        WHEN COALESCE(att.ingressos_validos, 0) > 0
        THEN ROUND((COALESCE(att.presentes, 0) * 100.0) / att.ingressos_validos, 4)
        ELSE NULL
      END AS REAL
    ) AS comparecimento_pct,
    CAST('entradas_validadas' AS TEXT) AS metric_type,
    CAST('entradas_validadas' AS TEXT) AS audience_measure,
    CAST(
      ROW_NUMBER() OVER (
        ORDER BY
          CAST(es.session_date AS TEXT),
          COALESCE(CAST(es.session_start_at AS TEXT), CAST(es.session_date AS TEXT) || ' 00:00:00'),
          es.id
      ) AS INTEGER
    ) AS session_rank
  FROM event_sessions es
  LEFT JOIN attendance_agg att ON att.session_id = es.id
)
SELECT
  event_id,
  session_id,
  session_key,
  session_name,
  session_type,
  session_date,
  session_start_at,
  ingressos_validos,
  presentes,
  ausentes,
  invalidos,
  bloqueados,
  comparecimento_pct,
  metric_type,
  audience_measure,
  session_rank
FROM ranked
ORDER BY session_rank;
