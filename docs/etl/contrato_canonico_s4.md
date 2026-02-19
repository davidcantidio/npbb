# Contrato Canonico S4 - Fluxo Principal

## Objetivo
Documentar o fluxo principal da Sprint 4 do epico Contrato Canonico + Validacao Estrita + Linhagem Obrigatoria, com foco em:
- compatibilidade de versoes de contrato;
- gate de regressao com limite configuravel;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis.

Arquivos principais da sprint:
- `core/contracts/s4_scaffold.py`
- `core/contracts/s4_core.py`
- `core/contracts/s4_observability.py`
- `backend/app/services/contract_validation_service.py`
- `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- `tests/test_contract_validation_s4.py`
- `tests/test_contract_validation_s4_observability.py`
- `tests/test_contract_validation_s4_telemetry.py`

## Escopo funcional da Sprint 4
- Validar entrada canonicamente no scaffold S4.
- Executar o fluxo principal no core S4 com callback de validacao de compatibilidade/regressao.
- Bloquear liberacao quando:
  - `status` final da execucao nao e de sucesso;
  - houver `breaking_change_detected=true` com `breaking_change_policy=block`;
  - `regression_gate_required=true` e o gate nao passar.
- Expor contrato estavel na camada de service com IDs de observabilidade do service e do core.

## Contratos de entrada e saida
Entrada base (`S4CanonicalContractCoreInput` e `S4CanonicalContractScaffoldRequest`):
- `contract_id`, `dataset_name`, `source_kind`, `schema_version`
- `strict_validation`, `lineage_required`, `owner_team`
- `schema_required_fields`
- `lineage_field_requirements`, `metric_lineage_requirements`
- `compatibility_mode`, `previous_contract_versions`
- `regression_gate_required`, `regression_suite_version`, `max_regression_failures`
- `breaking_change_policy`, `deprecation_window_days`
- `correlation_id` (opcional)

Saida core (`execute_s4_contract_validation_main_flow`):
- `contrato_versao=cont.s4.core.v1`
- `status=completed`
- `versioning_profile`
- `execucao`:
  - `status`
  - `decision_reason`
  - `validation_result_id`
  - `compatibility_result`
  - `breaking_change_detected`
  - `regression_failures`
  - `max_regression_failures`
  - `regression_gate_required`
  - `regression_gate_passed`
- `pontos_integracao`
- `observabilidade` (`conts4coreevt-*`)
- `scaffold`

Saida service (`execute_s4_contract_validation_service`):
- `contrato_versao=cont.s4.service.v1`
- `status=completed`
- `versioning_profile`
- `execucao` (repasse do core)
- `pontos_integracao`
- `observabilidade` (`conts4evt-*` + referencias do core)
- `scaffold`

## Logs e rastreabilidade
Observabilidade do core:
- modulo: `core/contracts/s4_observability.py`
- principais funcoes: `build_s4_contract_observability_event`, `log_s4_contract_observability_event`, `build_s4_contract_actionable_error`

Telemetria do backend:
- modulo: `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- principais funcoes: `build_s4_contract_telemetry_event`, `emit_s4_contract_telemetry_event`, `build_s4_contract_error_detail`

Core:
- logger: `npbb.core.contracts.s4.core`
- eventos: `contract_validation_s4_main_flow_started`, `contract_validation_s4_main_flow_completed`
- IDs: `conts4coreevt-*`

Service:
- logger: `app.services.contract_validation`
- eventos: `contract_validation_s4_flow_started`, `contract_validation_s4_versioning_profile_ready`, `contract_validation_s4_flow_completed`
- IDs: `conts4evt-*`

Campos minimos para diagnostico:
- `correlation_id`
- `contract_id`
- `dataset_name`
- `schema_version`
- `compatibility_mode`
- `regression_gate_required`
- `max_regression_failures`
- `error_code` e `recommended_action` (em falhas)

## Erros acionaveis principais
- `CONT_S4_COMPATIBILITY_VALIDATION_FAILED`
- `CONT_S4_BREAKING_CHANGE_BLOCKED`
- `CONT_S4_REGRESSION_GATE_FAILED`
- `CONT_S4_MAIN_FLOW_FAILED`
- `CONTRACT_VALIDATION_S4_FLOW_FAILED`
- `INVALID_CONT_S4_OBSERVABILITY_*`
- `INVALID_CONT_S4_TELEMETRY_*`

## Validacao local
```bash
pytest -q tests/test_contract_validation_s4.py
pytest -q tests/test_contract_validation_s4_observability.py
pytest -q tests/test_contract_validation_s4_telemetry.py
```

## Limites da Sprint 4
- Fluxo focado em compatibilidade e gate de regressao no contrato canonico.
- Nao inclui persistencia externa de resultados de regressao.
- Nao inclui automacao de observabilidade/validacao das tasks seguintes da sprint.
