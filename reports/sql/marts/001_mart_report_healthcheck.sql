-- TMJ-ETL-056: sample mart view to validate SQL runner/contracts pipeline.
DROP VIEW IF EXISTS mart_report_healthcheck;

CREATE VIEW mart_report_healthcheck AS
SELECT
  CAST('tmj2025_healthcheck' AS TEXT) AS section_key,
  CAST('ok' AS TEXT) AS status,
  CAST(datetime('now') AS TEXT) AS generated_at;
