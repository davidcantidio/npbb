# EPIC-F2-01 - Usecase ETL Import (evidence)

Date: 2026-03-03
Status: implemented

## Scope delivered

- Public ETL usecase facade created in `backend/app/modules/leads_publicidade/application/leads_import_etl_usecases.py`.
- ETL preview/commit internals isolated in `backend/app/modules/leads_publicidade/application/etl_import/`.
- Dedicated preview session storage implemented with model + migration:
  - `backend/app/models/models.py` (`LeadImportEtlPreviewSession`)
  - `backend/alembic/versions/d7e2a4b9c1f0_add_lead_import_etl_preview_session_table.py`
- Backend router integration completed:
  - `POST /leads/import/etl/preview`
  - `POST /leads/import/etl/commit`

## Contract and behavior decisions

- Core ETL remains pure (`core/leads_etl/*`) with no FastAPI/ORM coupling introduced by this epic.
- Commit consumes snapshot by `session_token` (no file reprocessing in commit path).
- `strict` for commit is explicit and overridable:
  - `strict=true` blocks when preview has validation errors.
  - `strict=false` allows commit of approved rows.
- Warnings require explicit confirmation via `force_warnings=true`.
- Commit is idempotent for already committed `session_token`.
- Dedupe/merge stays backend-only via `etl_import/persistence.py`.

## Test evidence

Executed on 2026-03-03:

- `PYTHONPATH=backend:. pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_leads_import_etl_endpoint.py`
  - result: 11 passed
- `PYTHONPATH=backend:. pytest -q tests/test_lead_etl_contract_gate.py tests/test_lead_etl_cross_layer_gate.py`
  - result: 2 passed
- `PYTHONPATH=backend:. pytest -q backend/tests/test_leads_import_csv_smoke.py backend/tests/test_lead_constraints.py`
  - result: 7 passed

Covered scenarios include:

- Preview ETL returns `session_token`, row counters, and `dq_report`.
- Commit blocks on warnings without explicit confirmation.
- Commit strict gate blocks validation errors when strict is active.
- Commit can override strict to false and still finalize session.
- Commit replay with same `session_token` returns idempotent result.
- Unknown session token returns not found contract error.
- Legacy CSV import smoke remains green.

## Rollback notes

- Preview session migration is additive and non-destructive.
- Downgrade is intentionally no-op in this rollout (`d7e2a4b9c1f0`).
