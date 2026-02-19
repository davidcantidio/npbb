# Contrato Canonico S1 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 1 do epico Contrato Canonico + Validacao Estrita + Linhagem Obrigatoria, com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/contracts/s1_scaffold.py`
- `core/contracts/s1_core.py`
- `core/contracts/s1_observability.py`
- `core/contracts/s1_validation.py`
- `backend/app/services/contract_validation_service.py`
- `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- `scripts/contract_tools.py`

## Quando usar
- Validar contrato CONT S1 antes de integrar com proximas sprints de contrato canonico.
- Simular o fluxo principal em nivel core e service.
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

## Contrato CONT S1 (resumo)
Entrada:
- `contract_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `source_kind` (`pdf`, `docx`, `pptx`, `xlsx`, `csv`, `api`, `manual`, `other`)
- `schema_version` (`vN`, ex: `v1`)
- `strict_validation` (bool)
- `lineage_required` (bool)
- `owner_team` (minimo de 2 caracteres)
- `correlation_id` (opcional)

Saida core (`execute_s1_contract_validation_main_flow`):
- `contrato_versao=cont.s1.core.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `canonical_contract`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts1coreevt-*`)

Saida service (`execute_s1_contract_validation_service`):
- `contrato_versao=cont.s1.service.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `canonical_contract`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts1evt-*` + referencias do core)
- `scaffold`

## Observabilidade e logs
Validacao e core:
- loggers: `npbb.core.contracts.s1.validation`, `npbb.core.contracts.s1.core`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `conts1coreevt-`

Service:
- logger: `app.services.contract_validation`
- ids: `event_id` com prefixo `conts1evt-`

Ferramenta operacional:
- logger: `npbb.contract_tools`
- eventos: `cont_s1_*`

Campos minimos para rastreio:
- `correlation_id`
- `contract_id`
- `dataset_name`
- `source_kind`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/contract_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/contract_tools.py s1:validate-input \
  --contract-id CONT_STG_OPTIN_V1 \
  --dataset-name stg_optin_events \
  --source-kind csv \
  --schema-version v1 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl
```

Saida esperada:
- `[OK] s1:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/contract_tools.py s1:simulate-core \
  --contract-id CONT_FCT_TICKET_SALES_V1 \
  --dataset-name fct_ticket_sales \
  --source-kind xlsx \
  --schema-version v1 \
  --strict-validation true \
  --lineage-required true \
  --owner-team analytics
```

Saida esperada:
- `[OK] s1:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/contract_tools.py s1:simulate-service \
  --contract-id CONT_STG_API_EVENTS_V1 \
  --dataset-name stg_api_events \
  --source-kind api \
  --schema-version v1 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl
```

Saida esperada:
- `[OK] s1:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/contract_tools.py s1:runbook-check
```

Saida esperada:
- `[OK] s1:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/contract_tools.py \
  --output-format json \
  s1:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s1:validate-input`.
2. Simular fluxo no core com `s1:simulate-core`.
3. Simular fluxo no service com `s1:simulate-service`.
4. Executar `s1:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_CONTRACT_ID`:
- Sintoma: `contract_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_DATASET_NAME`:
- Sintoma: `dataset_name` com menos de 3 caracteres.
- Acao: definir nome estavel para rastreabilidade.

`INVALID_SOURCE_KIND`:
- Sintoma: tipo de fonte nao suportado.
- Acao: usar `pdf`, `docx`, `pptx`, `xlsx`, `csv`, `api`, `manual` ou `other`.

`INVALID_SCHEMA_VERSION`:
- Sintoma: formato de schema invalido.
- Acao: usar `vN` (exemplo: `v1`).

`INVALID_STRICT_VALIDATION_FLAG_TYPE` ou `INVALID_LINEAGE_REQUIRED_FLAG_TYPE`:
- Sintoma: flags booleanas invalidas.
- Acao: enviar `true` ou `false`.

`CONT_S1_VALIDATION_FAILED`:
- Sintoma: validacao retornou status final de erro.
- Acao: revisar `execucao.status`, `validation_result_id` e regras do contrato canonico.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload de saida nao segue `cont.s1.core.v1` ou `cont.s1.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`CONT_S1_MAIN_FLOW_FAILED` ou `CONTRACT_VALIDATION_S1_FLOW_FAILED`:
- Sintoma: falha inesperada no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_contract_validation_s1.py
pytest -q tests/test_contrato_canonico_s1.py
python scripts/contract_tools.py s1:runbook-check
```

## Limites da Sprint 1
- Fluxo focado em contrato canonico v1, validacao estrita e linhagem obrigatoria.
- Nao inclui evolucoes das sprints 2, 3 e 4 do epico.
- Nao inclui persistencia final em storage externo.
