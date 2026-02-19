# Motor de Confianca S2 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 2 do epico Motor de Confianca e Politica de Decisao, com foco em:
- politica de decisao `auto_approve/manual_review/gap/reject`;
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/confidence/s2_scaffold.py`
- `core/confidence/s2_core.py`
- `core/confidence/s2_observability.py`
- `core/confidence/s2_validation.py`
- `backend/app/services/confidence_policy_service.py`
- `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- `scripts/confidence_tools.py`
- `tests/test_motor_confianca_s2.py`
- `tests/test_motor_confianca_s2_observability.py`
- `tests/test_motor_confianca_s2_telemetry.py`

## Quando usar
- Validar politica CONF S2 antes de integrar com proximas sprints do motor de confianca.
- Simular o fluxo principal em nivel core e service para decisao `auto/review/gap`.
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

## Contrato CONF S2 (resumo)
Entrada:
- `policy_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `entity_kind` (`lead`, `evento`, `ingresso`, `generic`)
- `schema_version` (`vN`, ex: `v2`)
- `owner_team` (minimo de 2 caracteres)
- `field_weights` (opcional, formato `campo -> peso`)
- `default_weight` (0.0..1.0, maior que 0)
- `auto_approve_threshold` (0.0..1.0)
- `manual_review_threshold` (0.0..1.0)
- `gap_threshold` (0.0..1.0)
- `missing_field_penalty` (0.0..1.0)
- `decision_mode` (`auto_review_gap`, `weighted_auto_review_gap`)
- `gap_escalation_required` (bool)
- `max_manual_review_queue` (int >= 0)
- `correlation_id` (opcional)

Saida core (`execute_s2_confidence_policy_main_flow`):
- `contrato_versao=conf.s2.core.v1`
- `correlation_id`
- `status=completed`
- `policy_id`
- `dataset_name`
- `decision_policy`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`confs2coreevt-*`)
- `scaffold`

Saida service (`execute_s2_confidence_policy_service`):
- `contrato_versao=conf.s2.service.v1`
- `correlation_id`
- `status=completed`
- `policy_id`
- `dataset_name`
- `decision_policy`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`confs2evt-*` + referencias do core)
- `scaffold`

## Observabilidade, telemetria e logs
Validacao, scaffold, core e observabilidade:
- loggers: `npbb.core.confidence.s2.validation`, `npbb.core.confidence.s2`, `npbb.core.confidence.s2.core`
- modulo de observabilidade: `core/confidence/s2_observability.py`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `confs2coreevt-`

Service e telemetria:
- logger: `app.services.confidence_policy`
- modulo de telemetria: `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- ids: `event_id` com prefixo `confs2evt-`

Ferramenta operacional:
- logger: `npbb.confidence_tools`
- eventos: `conf_s2_*`

Campos minimos para rastreio:
- `correlation_id`
- `policy_id`
- `dataset_name`
- `entity_kind`
- `decision_mode`
- `confidence_score`
- `decision`
- `manual_review_queue_size`
- `gap_escalation_triggered`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/confidence_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/confidence_tools.py s2:validate-input \
  --policy-id CONF_LEAD_POLICY_V2 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v2 \
  --owner-team etl \
  --field-weight nome=0.2 \
  --field-weight email=0.3 \
  --field-weight telefone=0.2 \
  --field-weight documento=0.3 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --gap-threshold 0.40 \
  --missing-field-penalty 0.10 \
  --decision-mode auto_review_gap \
  --gap-escalation-required true \
  --max-manual-review-queue 500
```

Saida esperada:
- `[OK] s2:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/confidence_tools.py s2:simulate-core \
  --policy-id CONF_LEAD_POLICY_V2 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v2 \
  --owner-team analytics \
  --field-weight nome=0.2 \
  --field-weight email=0.3 \
  --field-weight telefone=0.2 \
  --field-weight documento=0.3 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --gap-threshold 0.40 \
  --missing-field-penalty 0.10 \
  --decision-mode auto_review_gap \
  --gap-escalation-required true \
  --max-manual-review-queue 500
```

Saida esperada:
- `[OK] s2:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/confidence_tools.py s2:simulate-service \
  --policy-id CONF_LEAD_POLICY_V2 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v2 \
  --owner-team etl \
  --field-weight nome=0.2 \
  --field-weight email=0.3 \
  --field-weight telefone=0.2 \
  --field-weight documento=0.3 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --gap-threshold 0.40 \
  --missing-field-penalty 0.10 \
  --decision-mode auto_review_gap \
  --gap-escalation-required true \
  --max-manual-review-queue 500
```

Saida esperada:
- `[OK] s2:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/confidence_tools.py s2:runbook-check
```

Saida esperada:
- `[OK] s2:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/confidence_tools.py \
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
`INVALID_POLICY_ID`:
- Sintoma: `policy_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_DECISION_THRESHOLDS`:
- Sintoma: ordem invalida de limiares.
- Acao: ajustar para `gap_threshold <= manual_review_threshold <= auto_approve_threshold`.

`INVALID_MAX_MANUAL_REVIEW_QUEUE`:
- Sintoma: fila maxima negativa/invalida.
- Acao: usar `max_manual_review_queue` inteiro >= 0.

`INVALID_MANUAL_REVIEW_QUEUE_SIZE`:
- Sintoma: executor retornou tamanho de fila invalido.
- Acao: retornar `manual_review_queue_size` como inteiro >= 0.

`CONF_S2_DECISION_EXECUTION_FAILED`:
- Sintoma: fluxo de decisao retornou status de falha.
- Acao: revisar `execucao.status`, `decision_reason` e politica operacional de escalonamento.

`INVALID_DECISION`:
- Sintoma: saida com decisao fora do contrato.
- Acao: retornar `auto_approve`, `manual_review`, `gap` ou `reject`.

`MISSING_DECISION_RESULT_ID`:
- Sintoma: saida sem identificador de resultado de decisao.
- Acao: propagar `decision_result_id` para rastreabilidade operacional.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload nao segue `conf.s2.core.v1` ou `conf.s2.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`CONF_S2_MAIN_FLOW_FAILED` ou `CONFIDENCE_POLICY_S2_FLOW_FAILED`:
- Sintoma: falha inesperada no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_motor_confianca_s2.py
pytest -q tests/test_motor_confianca_s2_observability.py tests/test_motor_confianca_s2_telemetry.py
python scripts/confidence_tools.py s2:runbook-check
```

## Limites da Sprint 2
- Fluxo focado em politica de decisao `auto/review/gap` com rastreabilidade operacional.
- Nao inclui calibracao estatistica automatizada dos limiares de decisao.
- Nao inclui persistencia externa do resultado final de decisao.
