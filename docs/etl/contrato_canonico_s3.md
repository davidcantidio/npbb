# Contrato Canonico S3 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 3 do epico Contrato Canonico + Validacao Estrita + Linhagem Obrigatoria, com foco em:
- contrato estavel de entrada e saida;
- enforcement de linhagem por campo e por metrica;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/contracts/s3_scaffold.py`
- `core/contracts/s3_core.py`
- `core/contracts/s3_observability.py`
- `core/contracts/s3_validation.py`
- `backend/app/services/contract_validation_service.py`
- `backend/app/services/contrato-can-nico-valida-o-estrita-linhagem-obrigat-ria_telemetry.py`
- `scripts/contract_tools.py`

## Quando usar
- Validar contrato CONT S3 antes de integrar com consumidores que exigem linhagem obrigatoria.
- Simular o fluxo principal em nivel core e service para regras de linhagem por campo/metrica.
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

## Contrato CONT S3 (resumo)
Entrada:
- `contract_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `source_kind` (`pdf`, `docx`, `pptx`, `xlsx`, `csv`, `api`, `manual`, `other`)
- `schema_version` (`vN`, ex: `v3`)
- `strict_validation` (bool)
- `lineage_required` (bool)
- `owner_team` (minimo de 2 caracteres)
- `schema_required_fields` (lista de campos obrigatorios de schema)
- `lineage_field_requirements` (mapa campo -> refs de linhagem)
- `metric_lineage_requirements` (mapa metrica -> refs de linhagem)
- `correlation_id` (opcional)

Saida core (`execute_s3_contract_validation_main_flow`):
- `contrato_versao=cont.s3.core.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `lineage_profile`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts3coreevt-*`)
- `scaffold`

Saida service (`execute_s3_contract_validation_service`):
- `contrato_versao=cont.s3.service.v1`
- `correlation_id`
- `status=completed`
- `contract_id`
- `dataset_name`
- `lineage_profile`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`conts3evt-*` + referencias do core)
- `scaffold`

## Observabilidade e logs
Validacao, scaffold e core:
- loggers: `npbb.core.contracts.s3.validation`, `npbb.core.contracts.s3`, `npbb.core.contracts.s3.core`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `conts3coreevt-`

Service:
- logger: `app.services.contract_validation`
- ids: `event_id` com prefixo `conts3evt-`

Ferramenta operacional:
- logger: `npbb.contract_tools`
- eventos: `cont_s3_*`

Campos minimos para rastreio:
- `correlation_id`
- `contract_id`
- `dataset_name`
- `schema_required_fields`
- `lineage_field_requirements`
- `metric_lineage_requirements`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/contract_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/contract_tools.py s3:validate-input \
  --contract-id CONT_STG_OPTIN_V3 \
  --dataset-name stg_optin_events \
  --source-kind csv \
  --schema-version v3 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --lineage-field-requirement record_id=crm.orders.id \
  --lineage-field-requirement source_id=crm.sources.origin_system \
  --metric-lineage-requirement optin_total=crm.optin.total
```

Saida esperada:
- `[OK] s3:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/contract_tools.py s3:simulate-core \
  --contract-id CONT_FCT_TICKET_SALES_V3 \
  --dataset-name fct_ticket_sales \
  --source-kind xlsx \
  --schema-version v3 \
  --strict-validation true \
  --lineage-required true \
  --owner-team analytics \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --lineage-field-requirement record_id=erp.sales.id \
  --lineage-field-requirement source_id=erp.sales.channel \
  --metric-lineage-requirement ticket_count=erp.sales.qty \
  --metric-lineage-requirement gross_revenue=erp.sales.total_amount
```

Saida esperada:
- `[OK] s3:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/contract_tools.py s3:simulate-service \
  --contract-id CONT_STG_API_EVENTS_V3 \
  --dataset-name stg_api_events \
  --source-kind api \
  --schema-version v3 \
  --strict-validation true \
  --lineage-required true \
  --owner-team etl \
  --schema-required-fields record_id,event_ts,source_id,payload_checksum \
  --lineage-field-requirement record_id=api.events.id \
  --lineage-field-requirement source_id=api.events.origin \
  --metric-lineage-requirement event_count=api.events.count
```

Saida esperada:
- `[OK] s3:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/contract_tools.py s3:runbook-check
```

Saida esperada:
- `[OK] s3:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/contract_tools.py \
  --output-format json \
  s3:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s3:validate-input`.
2. Simular fluxo no core com `s3:simulate-core`.
3. Simular fluxo no service com `s3:simulate-service`.
4. Executar `s3:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_CONTRACT_ID`:
- Sintoma: `contract_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_REQUIRED_FIELDS`:
- Sintoma: `schema_required_fields` vazio/invalido.
- Acao: informar campos obrigatorios minimos do schema.

`INSUFFICIENT_LINEAGE_REQUIREMENTS`:
- Sintoma: `lineage_required=true` sem regras suficientes por campo/metrica.
- Acao: preencher `lineage_field_requirements` e `metric_lineage_requirements`.

`LINEAGE_FIELD_NOT_IN_SCHEMA`:
- Sintoma: regra de linhagem para campo fora de `schema_required_fields`.
- Acao: alinhar regras de linhagem com o schema obrigatorio.

`INVALID_LINEAGE_REFERENCE_FORMAT`:
- Sintoma: referencia de linhagem com formato invalido.
- Acao: usar padrao estavel, por exemplo `crm.orders.total_amount`.

`INVALID_LINEAGE_FIELD_REQUIREMENT_FORMAT` ou `INVALID_METRIC_LINEAGE_REQUIREMENT_FORMAT`:
- Sintoma: regra mal formatada na CLI.
- Acao: usar `chave=valor1|valor2` nas flags de linhagem.

`CONT_S3_LINEAGE_ENFORCEMENT_FAILED`:
- Sintoma: enforcement retornou status final de erro.
- Acao: revisar `execucao.status`, `validation_result_id` e regras de linhagem.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload de saida nao segue `cont.s3.core.v1` ou `cont.s3.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`CONT_S3_MAIN_FLOW_FAILED` ou `CONTRACT_VALIDATION_S3_FLOW_FAILED`:
- Sintoma: falha inesperada no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_contract_validation_s3.py
pytest -q tests/test_contrato_canonico_s3.py
python scripts/contract_tools.py s3:runbook-check
```

## Limites da Sprint 3
- Fluxo focado em enforcement de linhagem por campo/metrica dentro do contrato canonico.
- Nao inclui evolucoes da Sprint 4 do epico.
- Nao inclui persistencia final em storage externo.
