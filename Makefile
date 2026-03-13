SHELL := /bin/bash

PHASE_F4_EVIDENCE_DIR ?= artifacts/phase-f4/evidence

.PHONY: eval-integrations __eval-integrations ci-quality __ci-quality phase-f4-summary

eval-integrations:
	mkdir -p "$(PHASE_F4_EVIDENCE_DIR)"
	status=PASS; \
	if ! $(MAKE) --no-print-directory __eval-integrations; then status=FAIL; fi; \
	python3 scripts/write_gate_status.py --output "$(PHASE_F4_EVIDENCE_DIR)/eval-integrations.json" --gate eval-integrations --status "$$status"; \
	test "$$status" = PASS

__eval-integrations:
	./scripts/check_migration_legacy.sh
	./scripts/check_architecture_guards.sh
	./scripts/check_repo_hygiene.sh

ci-quality:
	mkdir -p "$(PHASE_F4_EVIDENCE_DIR)"
	status=PASS; \
	if ! $(MAKE) --no-print-directory __ci-quality; then status=FAIL; fi; \
	python3 scripts/write_gate_status.py --output "$(PHASE_F4_EVIDENCE_DIR)/ci-quality.json" --gate ci-quality --status "$$status"; \
	test "$$status" = PASS

__ci-quality:
	cd frontend && npm run lint
	cd frontend && npm run typecheck
	cd frontend && npm run test -- --run
	cd frontend && npm run build
	./scripts/check_frontend_bundle_api_base.sh
	cd backend && ruff check app tests
	cd backend && SECRET_KEY=ci-secret-key python -m pytest -q
	PYTHONPATH=. python -m pytest -q tests/test_compare_restore_counts.py
	python3 scripts/check_etl_cross_layer_coverage.py
	./scripts/check_architecture_guards.sh
	./scripts/check_repo_hygiene.sh

phase-f4-summary:
	python3 scripts/render_phase_validation_summary.py --project LEAD-ETL-FUSION --output artifacts/phase-f4/validation-summary.md
