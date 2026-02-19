# Contrato Canonico S2 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 2 do epico Contrato Canonico + Validacao Estrita + Linhagem Obrigatoria, com foco em:
- contrato estavel de entrada e saida;
- validacao estrita de schema e dominio;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/contracts/s2_scaffold.py`
- `core/contracts/s2_core.py`
- `core/contracts/s2_observability.py`
- `core/contracts/s2_validation.py`
- `backend/app/services/contract_validation_service.py`
- `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- `scripts/contract_tools.py`

## Quando usar
- Validar contrato CONT S2 antes de integrar com proximas sprints do contrato canonico.
- Simular o fluxo principal em nivel core e service para schema/domain checks.
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

## Contrato CONT S2 (resumo)
Entrada:
- `contract_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `source_kind` (`pdf`, `docx`, `pptx`, `xlsx`, `csv`, `api`, `manual`, `other`)
- `schema_version` (`vN`, ex: `v2`)
- `strict_validation` (bool)
- `lineage_required` (bool)
- `owner_team` (minimo de 2 caracteres)
- `schema_required_fields` (lista de campos obrigatorios de schema)
- `domain_constraints` (mapa campo -> valores permitidos)
- `correlation_id` (opcional)

Saida core (`execute_s2_contract_validation_main_flow`):
- `contrato_versao=cont.s2.core.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `validation_profile`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts2coreevt-*`)
- `scaffold`

Saida service (`execute_s2_contract_validation_service`):
- `contrato_versao=cont.s2.service.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `validation_profile`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts2evt-*` + referencias do core)
- `scaffold`

## Observabilidade e logs
Validacao, scaffold e core:
- loggers: `npbb.core.contracts.s2.validation`, `npbb.core.contracts.s2`, `npbb.core.contracts.s2.core`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `conts2coreevt-`

Service e telemetria:
- logger: `app.services.contract_validation`
- ids: `event_id` com prefixo `conts2evt-`

Ferramenta operacional:
- logger: `npbb.contract_tools`
- eventos: `cont_s2_*`

Campos minimos para rastreio:
- `correlation_id`
- `contract_id`
- `dataset_name`
- `source_kind`
- `schema_required_fields`
- `domain_constraints`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/contract_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/contract_tools.py s2:validate-input \
  --contract-id CONT_STG_OPTIN_V2 \
  --dataset-name stg_optin_events \
  --source-kind csv \
  --schema-version v2 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --domain-constraint record_id=not_null \
  --domain-constraint source_id=crm|app
```

Saida esperada:
- `[OK] s2:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/contract_tools.py s2:simulate-core \
  --contract-id CONT_FCT_TICKET_SALES_V2 \
  --dataset-name fct_ticket_sales \
  --source-kind xlsx \
  --schema-version v2 \
  --strict-validation true \
  --lineage-required true \
  --owner-team analytics \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --domain-constraint source_id=pdv|online \
  --domain-constraint record_id=not_null
```

Saida esperada:
- `[OK] s2:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/contract_tools.py s2:simulate-service \
  --contract-id CONT_STG_API_EVENTS_V2 \
  --dataset-name stg_api_events \
  --source-kind api \
  --schema-version v2 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --domain-constraint source_id=api_gateway|backoffice \
  --domain-constraint record_id=not_null
```

Saida esperada:
- `[OK] s2:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/contract_tools.py s2:runbook-check
```

Saida esperada:
- `[OK] s2:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/contract_tools.py \
  --output-format json \
  s2:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s2:validate-input`.
2. Simular fluxo no core com `s2:simulate-core`.
3. Simular fluxo no service com `s2:simulate-service`.
4. Executar `s2:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_CONTRACT_ID`:
- Sintoma: `contract_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_SCHEMA_REQUIRED_FIELDS`:
- Sintoma: `schema_required_fields` vazio/invalido.
- Acao: informar campos obrigatorios minimos do schema.

`DOMAIN_FIELD_NOT_IN_SCHEMA`:
- Sintoma: regra de dominio para campo fora do schema.
- Acao: alinhar `domain_constraints` com `schema_required_fields`.

`INVALID_DOMAIN_CONSTRAINT_FORMAT`:
- Sintoma: regra de dominio mal formatada na CLI.
- Acao: usar `--domain-constraint campo=valor1|valor2`.

`CONT_S2_VALIDATION_FAILED`:
- Sintoma: validacao retornou status final de erro.
- Acao: revisar `execucao.status`, `validation_result_id` e regras de schema/dominio.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload de saida nao segue `cont.s2.core.v1` ou `cont.s2.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`CONT_S2_MAIN_FLOW_FAILED` ou `CONTRACT_VALIDATION_S2_FLOW_FAILED`:
- Sintoma: falha inesperada no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_contract_validation_s2.py
pytest -q tests/test_contrato_canonico_s2.py
python scripts/contract_tools.py s2:runbook-check
```

## Limites da Sprint 2
- Fluxo focado em validacao estrita de schema e dominio dentro do contrato canonico.
- Nao inclui evolucoes das sprints 3 e 4 do epico.
- Nao inclui persistencia final em storage externo.
