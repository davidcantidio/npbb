# EPIC-F1-01 - Evidencia de Implementacao

Data de validacao: 2026-03-03

## Escopo migrado para `core/leads_etl`

### Transform
- `core/leads_etl/transform/column_normalize.py`
- `core/leads_etl/transform/segment_mapper.py`
- `core/leads_etl/transform/config/segment_mapping.yml`

### Validate
- `core/leads_etl/validate/framework.py`
- `core/leads_etl/validate/checks_schema.py`
- `core/leads_etl/validate/checks_not_null.py`
- `core/leads_etl/validate/checks_duplicates.py`
- `core/leads_etl/validate/checks_access_control.py`
- `core/leads_etl/validate/checks_percentages.py`
- `core/leads_etl/validate/checks_cross_source.py`
- `core/leads_etl/validate/render_dq_report.py`
- `core/leads_etl/validate/config/datasets.yml`

### Quebra interna para evitar arquivos monoliticos
- `_contracts.py`
- `_db_protocols.py`
- `_framework_persistence.py`
- `_runner.py`
- `_dataset_config.py`
- `_schema_check_impl.py`
- `_not_null_check_impl.py`
- `_duplicate_check_impl.py`
- `_access_control_rules.py`
- `_percentage_config.py`
- `_percentage_bounds_impl.py`
- `_percentage_sum_impl.py`
- `_cross_source_impl.py`
- `_cross_source_persistence.py`
- `_report_sections.py`
- `_report_renderers.py`

## Compatibilidade legada mantida
- `etl/transform/column_normalize.py` e `etl/transform/segment_mapper.py` agora sao fachadas de reexport para `core.leads_etl`.
- `etl/validate/framework.py`, `checks_schema.py`, `checks_not_null.py`, `checks_duplicates.py`, `checks_access_control.py`, `checks_percentages.py`, `checks_cross_source.py` e `render_dq_report.py` agora sao fachadas de reexport para `core.leads_etl`.
- `etl/validate/__init__.py` continua agregando a superficie antiga, combinando modulos migrados com modulos ainda legados.
- `etl/validate/coverage_matrix.py` passou a consumir o `datasets.yml` canonicamente em `core/leads_etl/validate/config/datasets.yml`.

## Escopo explicitamente mantido fora do core
- `etl/transform/agenda_loader.py`
- `etl/validate/checks_show_access_control.py`
- `etl/validate/checks_show_optin.py`
- `etl/validate/show_coverage_evaluator.py`
- `etl/validate/coverage_matrix.py`
- `etl/validate/coverage_contract.py`
- `etl/validate/config/coverage_contract.yml`
- `etl/validate/request_list.py`
- `etl/validate/session_coverage_report.py`
- `etl/validate/cli_dq.py`
- `etl/validate/alerts.py`

## Guardrails adicionados
- `scripts/check_architecture_guards.sh` agora falha se `core/leads_etl` importar `fastapi`, `sqlmodel`, `app.*`, `backend.*` ou `etl.*`.
- O mesmo guard agora falha se qualquer arquivo Python em `core/leads_etl` exceder 200 linhas, exceto `__init__.py`.
- O guard tambem verifica se os wrappers legados migrados continuam pequenos e delegando para `core.leads_etl`, reduzindo risco de reintroducao de duplicacao.

## Evidencia de verificacao
- Novo teste de compatibilidade: `tests/test_core_leads_etl_compat.py`
- Comando executado:

```bash
pytest tests/test_core_leads_etl_compat.py \
  tests/test_xlsx_utils.py \
  tests/test_segment_mapper.py \
  tests/test_metrics_and_segments.py \
  tests/test_dq_framework.py \
  tests/test_dq_checks_schema_not_null.py \
  tests/test_dq_checks_duplicates.py \
  tests/test_dq_checks_access_control.py \
  tests/test_dq_checks_percentages.py \
  tests/test_dq_checks_cross_source.py \
  tests/test_dq_advanced_checks.py \
  tests/test_render_dq_report.py -q
```

Resultado:
- `48 passed in 0.98s`

Comando executado:

```bash
bash scripts/check_architecture_guards.sh
```

Resultado:
- `OK`
