# Motor de Confianca S3 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 3 do epico Motor de Confianca e Politica de Decisao, com foco em:
- politica de decisao com guardrails para campos criticos;
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/confidence/s3_scaffold.py`
- `core/confidence/s3_core.py`
- `core/confidence/s3_observability.py`
- `core/confidence/s3_validation.py`
- `backend/app/services/confidence_policy_service.py`
- `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- `scripts/confidence_tools.py`
- `tests/test_motor_confianca_s3.py`
- `tests/test_motor_confianca_s3_observability.py`
- `tests/test_motor_confianca_s3_telemetry.py`

## Quando usar
- Validar politica CONF S3 antes de integrar com fluxos de relatorio de eventos.
- Simular fluxo principal em nivel core e service com regras de campos criticos.
- Executar checklist operacional local sem dependencia externa.
- Investigar falhas com `correlation_id`, `observability_event_id` e `event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias do projeto instaladas.
- Logging ativo para rastrear eventos operacionais.

Comando minimo:
```bash
python scripts/confidence_tools.py --help
```

## Contrato CONF S3 (resumo)
Entrada:
- `policy_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `entity_kind` (`lead`, `evento`, `ingresso`, `generic`)
- `schema_version` (`vN`, ex: `v3`)
- `owner_team` (minimo de 2 caracteres)
- `field_weights` (opcional, formato `campo -> peso`)
- `default_weight` (0.0..1.0, maior que 0)
- `auto_approve_threshold` (0.0..1.0)
- `manual_review_threshold` (0.0..1.0)
- `gap_threshold` (0.0..1.0)
- `missing_field_penalty` (0.0..1.0)
- `decision_mode` (`critical_fields_guardrails`, `weighted_critical_fields_guardrails`)
- `gap_escalation_required` (bool)
- `max_manual_review_queue` (int >= 0)
- `critical_fields` (lista/tupla de campos criticos)
- `min_critical_fields_present` (int >= 1)
- `critical_field_penalty` (0.0..1.0)
- `critical_violation_route` (`manual_review`, `gap`, `reject`)
- `critical_override_required` (bool)
- `correlation_id` (opcional)

Saida core (`execute_s3_confidence_policy_main_flow`):
- `contrato_versao=conf.s3.core.v1`
- `correlation_id`
- `status=completed`
- `policy_id`
- `dataset_name`
- `decision_policy`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`confs3coreevt-*`)
- `scaffold`

Saida service (`execute_s3_confidence_policy_service`):
- `contrato_versao=conf.s3.service.v1`
- `correlation_id`
- `status=completed`
- `policy_id`
- `dataset_name`
- `decision_policy`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`confs3evt-*` + referencias do core)
- `scaffold`

## Observabilidade, telemetria e logs
Validacao, scaffold, core e observabilidade:
- loggers: `npbb.core.confidence.s3.validation`, `npbb.core.confidence.s3`, `npbb.core.confidence.s3.core`
- modulo de observabilidade: `core/confidence/s3_observability.py`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `confs3coreevt-`

Service e telemetria:
- logger: `app.services.confidence_policy`
- modulo de telemetria: `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- ids: `event_id` com prefixo `confs3evt-`

Ferramenta operacional:
- logger: `npbb.confidence_tools`
- eventos: `conf_s3_*`

Campos minimos para rastreio:
- `correlation_id`
- `policy_id`
- `dataset_name`
- `entity_kind`
- `decision_mode`
- `critical_fields_present_count`
- `critical_violation_triggered`
- `critical_violation_route`
- `manual_review_queue_size`
- `gap_escalation_triggered`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/confidence_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/confidence_tools.py s3:validate-input \
  --policy-id CONF_REPORT_POLICY_V3 \
  --dataset-name event_report_lines \
  --entity-kind evento \
  --schema-version v3 \
  --owner-team etl \
  --field-weight nome_evento=0.3 \
  --field-weight data_evento=0.3 \
  --field-weight local_evento=0.2 \
  --field-weight diretoria=0.2 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --gap-threshold 0.40 \
  --missing-field-penalty 0.10 \
  --decision-mode critical_fields_guardrails \
  --gap-escalation-required true \
  --max-manual-review-queue 500 \
  --critical-field nome_evento \
  --critical-field data_evento \
  --critical-field local_evento \
  --min-critical-fields-present 2 \
  --critical-field-penalty 0.25 \
  --critical-violation-route manual_review \
  --critical-override-required true
```

Saida esperada:
- `[OK] s3:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/confidence_tools.py s3:simulate-core \
  --policy-id CONF_REPORT_POLICY_V3 \
  --dataset-name event_report_lines \
  --entity-kind evento \
  --schema-version v3 \
  --owner-team analytics \
  --field-weight nome_evento=0.3 \
  --field-weight data_evento=0.3 \
  --field-weight local_evento=0.2 \
  --field-weight diretoria=0.2 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --gap-threshold 0.40 \
  --missing-field-penalty 0.10 \
  --decision-mode critical_fields_guardrails \
  --gap-escalation-required true \
  --max-manual-review-queue 500 \
  --critical-field nome_evento \
  --critical-field data_evento \
  --critical-field local_evento \
  --min-critical-fields-present 2 \
  --critical-field-penalty 0.25 \
  --critical-violation-route manual_review \
  --critical-override-required true
```

Saida esperada:
- `[OK] s3:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/confidence_tools.py s3:simulate-service \
  --policy-id CONF_REPORT_POLICY_V3 \
  --dataset-name event_report_lines \
  --entity-kind evento \
  --schema-version v3 \
  --owner-team etl \
  --field-weight nome_evento=0.3 \
  --field-weight data_evento=0.3 \
  --field-weight local_evento=0.2 \
  --field-weight diretoria=0.2 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --gap-threshold 0.40 \
  --missing-field-penalty 0.10 \
  --decision-mode critical_fields_guardrails \
  --gap-escalation-required true \
  --max-manual-review-queue 500 \
  --critical-field nome_evento \
  --critical-field data_evento \
  --critical-field local_evento \
  --min-critical-fields-present 2 \
  --critical-field-penalty 0.25 \
  --critical-violation-route manual_review \
  --critical-override-required true
```

Saida esperada:
- `[OK] s3:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/confidence_tools.py s3:runbook-check
```

Saida esperada:
- `[OK] s3:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/confidence_tools.py \
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
`INVALID_POLICY_ID`:
- Sintoma: `policy_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_DECISION_THRESHOLDS`:
- Sintoma: ordem invalida de limiares.
- Acao: ajustar para `gap_threshold <= manual_review_threshold <= auto_approve_threshold`.

`INVALID_MIN_CRITICAL_FIELDS_PRESENT`:
- Sintoma: minimo de campos criticos maior que total de campos criticos disponiveis.
- Acao: ajustar `min_critical_fields_present` para valor entre `1` e total de `critical_fields`.

`INVALID_CRITICAL_VIOLATION_ROUTE`:
- Sintoma: rota de violacao critica fora do contrato.
- Acao: usar `manual_review`, `gap` ou `reject`.

`INVALID_CRITICAL_OVERRIDE_REQUIRED_TYPE`:
- Sintoma: `critical_override_required` nao foi informado como booleano.
- Acao: usar `true` ou `false`.

`INVALID_CRITICAL_FIELDS_PRESENT_COUNT`:
- Sintoma: saida com contagem de campos criticos invalida.
- Acao: retornar `critical_fields_present_count` como inteiro >= 0.

`INVALID_CRITICAL_VIOLATION_DECISION`:
- Sintoma: decisao final incompativel com regra de violacao critica.
- Acao: quando houver violacao critica, retornar decisao valida (`manual_review`, `gap`, `reject`).

`CONF_S3_DECISION_EXECUTION_FAILED`:
- Sintoma: fluxo de decisao retornou status de falha.
- Acao: revisar `execucao.status`, `decision_reason` e regras de campos criticos.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload de saida nao segue `conf.s3.core.v1` ou `conf.s3.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`CONF_S3_MAIN_FLOW_FAILED` ou `CONFIDENCE_POLICY_S3_FLOW_FAILED`:
- Sintoma: falha inesperada no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_motor_confianca_s3.py
pytest -q tests/test_motor_confianca_s3_observability.py tests/test_motor_confianca_s3_telemetry.py
python scripts/confidence_tools.py s3:runbook-check
```

## Limites da Sprint 3
- Fluxo focado em guardrails de campos criticos para politica de decisao de confianca.
- Nao inclui calibracao estatistica automatizada dos limiares.
- Nao inclui persistencia externa do resultado final de decisao.
