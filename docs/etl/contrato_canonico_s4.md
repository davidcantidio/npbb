# Contrato Canonico S4 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 4 do epico Contrato Canonico + Validacao Estrita + Linhagem Obrigatoria, com foco em:
- compatibilidade de versoes de contrato;
- gate de regressao com limite configuravel;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/contracts/s4_scaffold.py`
- `core/contracts/s4_core.py`
- `core/contracts/s4_observability.py`
- `core/contracts/s4_validation.py`
- `backend/app/services/contract_validation_service.py`
- `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- `scripts/contract_tools.py`
- `tests/test_contract_validation_s4.py`
- `tests/test_contract_validation_s4_observability.py`
- `tests/test_contract_validation_s4_telemetry.py`
- `tests/test_contrato_canonico_s4.py`

## Quando usar
- Validar contrato CONT S4 antes de liberar novas versoes de schema.
- Simular fluxo principal em nivel core/service com politica de compatibilidade e regressao.
- Executar checklist operacional local sem dependencia externa.
- Investigar falhas com `correlation_id`, `observability_event_id` e `event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias do projeto instaladas.
- Logging ativo para rastrear eventos operacionais.

Comando minimo:
```bash
python scripts/contract_tools.py --help
```

## Contrato CONT S4 (resumo)
Entrada:
- `contract_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `source_kind` (`pdf`, `docx`, `pptx`, `xlsx`, `csv`, `api`, `manual`, `other`)
- `schema_version` (`vN`, ex: `v4`)
- `strict_validation` (bool)
- `lineage_required` (bool)
- `owner_team` (minimo de 2 caracteres)
- `schema_required_fields`
- `lineage_field_requirements`
- `metric_lineage_requirements`
- `compatibility_mode` (`strict_backward`, `backward_with_deprecation`, `forward_and_backward`)
- `previous_contract_versions`
- `regression_gate_required`
- `regression_suite_version`
- `max_regression_failures`
- `breaking_change_policy` (`block`, `allow_with_waiver`)
- `deprecation_window_days`
- `correlation_id` (opcional)

Saida core (`execute_s4_contract_validation_main_flow`):
- `contrato_versao=cont.s4.core.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `versioning_profile`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts4coreevt-*`)
- `scaffold`

Saida service (`execute_s4_contract_validation_service`):
- `contrato_versao=cont.s4.service.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `versioning_profile`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts4evt-*` + referencias do core)
- `scaffold`

## Observabilidade, telemetria e logs
Validacao, scaffold, core e observabilidade:
- loggers: `npbb.core.contracts.s4.validation`, `npbb.core.contracts.s4`, `npbb.core.contracts.s4.core`
- modulo de observabilidade: `core/contracts/s4_observability.py`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `conts4coreevt-`

Service e telemetria:
- logger: `app.services.contract_validation`
- modulo de telemetria: `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- ids: `event_id` com prefixo `conts4evt-`

Ferramenta operacional:
- logger: `npbb.contract_tools`
- eventos: `cont_s4_*`

Campos minimos para rastreio:
- `correlation_id`
- `contract_id`
- `dataset_name`
- `source_kind`
- `schema_version`
- `compatibility_mode`
- `previous_contract_versions`
- `regression_gate_required`
- `max_regression_failures`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/contract_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/contract_tools.py s4:validate-input \
  --contract-id CONT_STG_OPTIN_V4 \
  --dataset-name stg_optin_events \
  --source-kind csv \
  --schema-version v4 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --lineage-field-requirement record_id=crm.orders.id \
  --lineage-field-requirement source_id=crm.sources.origin_system \
  --metric-lineage-requirement optin_total=crm.optin.total \
  --compatibility-mode strict_backward \
  --previous-contract-versions v3 \
  --regression-gate-required true \
  --regression-suite-version s4 \
  --max-regression-failures 0 \
  --breaking-change-policy block \
  --deprecation-window-days 0
```

Saida esperada:
- `[OK] s4:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/contract_tools.py s4:simulate-core \
  --contract-id CONT_FCT_TICKET_SALES_V4 \
  --dataset-name fct_ticket_sales \
  --source-kind xlsx \
  --schema-version v4 \
  --strict-validation true \
  --lineage-required true \
  --owner-team analytics \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --lineage-field-requirement record_id=erp.sales.id \
  --lineage-field-requirement source_id=erp.sales.channel \
  --metric-lineage-requirement ticket_count=erp.sales.qty \
  --metric-lineage-requirement gross_revenue=erp.sales.total_amount \
  --compatibility-mode strict_backward \
  --previous-contract-versions v3 \
  --regression-gate-required true \
  --regression-suite-version s4 \
  --max-regression-failures 0 \
  --breaking-change-policy block \
  --deprecation-window-days 0
```

Saida esperada:
- `[OK] s4:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/contract_tools.py s4:simulate-service \
  --contract-id CONT_STG_API_EVENTS_V4 \
  --dataset-name stg_api_events \
  --source-kind api \
  --schema-version v4 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --lineage-field-requirement record_id=api.events.id \
  --lineage-field-requirement source_id=api.events.origin \
  --metric-lineage-requirement event_count=api.events.count \
  --compatibility-mode strict_backward \
  --previous-contract-versions v3 \
  --regression-gate-required true \
  --regression-suite-version s4 \
  --max-regression-failures 0 \
  --breaking-change-policy block \
  --deprecation-window-days 0
```

Saida esperada:
- `[OK] s4:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/contract_tools.py s4:runbook-check
```

Saida esperada:
- `[OK] s4:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/contract_tools.py \
  --output-format json \
  s4:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s4:validate-input`.
2. Simular fluxo no core com `s4:simulate-core`.
3. Simular fluxo no service com `s4:simulate-service`.
4. Executar `s4:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_COMPATIBILITY_MODE`:
- Sintoma: `compatibility_mode` fora dos valores suportados.
- Acao: usar `strict_backward`, `backward_with_deprecation` ou `forward_and_backward`.

`MISSING_PREVIOUS_CONTRACT_VERSION`:
- Sintoma: `previous_contract_versions` ausente/vazio.
- Acao: informar versoes anteriores no formato `vN` (ex: `v3`).

`CONT_S4_BREAKING_CHANGE_BLOCKED`:
- Sintoma: breaking change detectada com politica de bloqueio.
- Acao: ajustar compatibilidade do contrato ou revisar politica (`allow_with_waiver` quando aplicavel).

`CONT_S4_REGRESSION_GATE_FAILED`:
- Sintoma: gate de regressao reprovado.
- Acao: reduzir falhas abaixo de `max_regression_failures` ou revisar parametros de gate.

`INVALID_REGRESSION_FAILURES` ou `INVALID_MAX_REGRESSION_FAILURES`:
- Sintoma: contagens invalidas no output.
- Acao: retornar inteiros >= 0 no payload de execucao.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload de saida nao segue `cont.s4.core.v1` ou `cont.s4.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`INVALID_PREVIOUS_CONTRACT_VERSIONS_FORMAT`:
- Sintoma: CLI com formato invalido para versoes anteriores.
- Acao: usar `--previous-contract-versions v3` ou `--previous-contract-versions v2,v3`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_contract_validation_s4.py
pytest -q tests/test_contract_validation_s4_observability.py
pytest -q tests/test_contract_validation_s4_telemetry.py
pytest -q tests/test_contrato_canonico_s4.py
python scripts/contract_tools.py s4:runbook-check
```

## Limites da Sprint 4
- Fluxo focado em compatibilidade e regressao do contrato canonico.
- Nao inclui persistencia externa do resultado de regressao.
- Nao inclui automacao de rollout fora do escopo do contrato.
