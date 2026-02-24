-- TMJ-ETL-059: catalogo de fontes + ultimo status de ingestao para transparencia metodologica.
DROP VIEW IF EXISTS mart_report_sources;

CREATE VIEW mart_report_sources AS
WITH latest_runs AS (
  SELECT
    i.id AS ingestion_id,
    i.source_pk AS source_pk,
    CAST(i.status AS TEXT) AS status,
    CAST(i.started_at AS TEXT) AS started_at,
    CAST(i.finished_at AS TEXT) AS finished_at,
    CAST(i.extractor_name AS TEXT) AS extractor_name,
    i.records_read AS records_read,
    i.records_loaded AS records_loaded,
    CAST(i.notes AS TEXT) AS notes,
    CAST(i.error_message AS TEXT) AS error_message,
    CAST(i.created_at AS TEXT) AS created_at,
    ROW_NUMBER() OVER (
      PARTITION BY i.source_pk
      ORDER BY i.started_at DESC, i.id DESC
    ) AS run_rank
  FROM ingestions i
),
joined AS (
  SELECT
    s.id AS source_pk,
    s.source_id AS source_id,
    CAST(s.kind AS TEXT) AS source_kind,
    CAST(s.uri AS TEXT) AS source_uri,
    CAST(COALESCE(s.display_name, '') AS TEXT) AS source_display_name,
    CAST(COALESCE(s.is_active, 0) AS INTEGER) AS source_is_active,
    CAST(COALESCE(s.file_sha256, '') AS TEXT) AS file_sha256,
    s.file_size_bytes AS file_size_bytes,
    CAST(s.file_mtime_utc AS TEXT) AS file_mtime_utc,
    lr.ingestion_id AS latest_ingestion_id,
    CAST(COALESCE(lr.status, '') AS TEXT) AS latest_status,
    CAST(COALESCE(lr.started_at, '') AS TEXT) AS latest_started_at,
    CAST(COALESCE(lr.finished_at, '') AS TEXT) AS latest_finished_at,
    CAST(COALESCE(lr.extractor_name, '') AS TEXT) AS latest_extractor_name,
    lr.records_read AS latest_records_read,
    lr.records_loaded AS latest_records_loaded,
    CAST(COALESCE(lr.notes, '') AS TEXT) AS latest_notes,
    CAST(COALESCE(lr.error_message, '') AS TEXT) AS latest_error_message,
    CAST(COALESCE(lr.created_at, '') AS TEXT) AS latest_created_at
  FROM sources s
  LEFT JOIN latest_runs lr
    ON lr.source_pk = s.id
    AND lr.run_rank = 1
),
ranked AS (
  SELECT
    source_pk,
    source_id,
    source_kind,
    source_uri,
    source_display_name,
    source_is_active,
    file_sha256,
    file_size_bytes,
    file_mtime_utc,
    latest_ingestion_id,
    latest_status,
    latest_started_at,
    latest_finished_at,
    latest_extractor_name,
    latest_records_read,
    latest_records_loaded,
    latest_notes,
    latest_error_message,
    latest_created_at,
    CAST(
      CASE
        WHEN latest_ingestion_id IS NULL
          THEN 'Sem execucao de ingestao registrada para esta fonte.'
        WHEN UPPER(latest_status) = 'FAILED'
          THEN 'Ultima ingestao falhou; revisar error_message/log_text.'
        WHEN UPPER(latest_status) = 'PARTIAL'
          THEN 'Ultima ingestao parcial; revisar lacunas e cobertura.'
        ELSE 'Fonte com ingestao registrada sem falha critica no ultimo run.'
      END AS TEXT
    ) AS limitation_note,
    CAST(
      CASE
        WHEN latest_ingestion_id IS NULL
          THEN 'evidence: source_id'
        ELSE 'evidence: source_id + latest_ingestion_id'
      END AS TEXT
    ) AS evidence_note,
    CAST('nao_aplicavel' AS TEXT) AS audience_measure,
    CAST(
      ROW_NUMBER() OVER (
        ORDER BY source_id
      ) AS INTEGER
    ) AS row_rank
  FROM joined
)
SELECT
  source_pk,
  source_id,
  source_kind,
  source_uri,
  source_display_name,
  source_is_active,
  file_sha256,
  file_size_bytes,
  file_mtime_utc,
  latest_ingestion_id,
  latest_status,
  latest_started_at,
  latest_finished_at,
  latest_extractor_name,
  latest_records_read,
  latest_records_loaded,
  latest_notes,
  latest_error_message,
  latest_created_at,
  limitation_note,
  evidence_note,
  audience_measure,
  row_rank
FROM ranked
ORDER BY row_rank;
