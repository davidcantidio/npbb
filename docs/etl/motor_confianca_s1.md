# Motor de Confianca S1 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 1 do epico Motor de Confianca e Politica de Decisao, com foco em:
- score de confianca por campo;
- regras de decisao por limiares;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `core/confidence/s1_scaffold.py`
- `core/confidence/s1_core.py`
- `core/confidence/s1_observability.py`
- `core/confidence/s1_validation.py`
- `backend/app/services/confidence_policy_service.py`
- `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- `scripts/confidence_tools.py`
- `tests/test_motor_confianca_s1.py`
- `tests/test_motor_confianca_s1_observability.py`
- `tests/test_motor_confianca_s1_telemetry.py`

## Quando usar
- Validar politica CONF S1 antes de integrar com as proximas sprints do motor de confianca.
- Simular o fluxo principal em nivel core e service.
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

## Contrato CONF S1 (resumo)
Entrada:
- `policy_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `entity_kind` (`lead`, `evento`, `ingresso`, `generic`)
- `schema_version` (`vN`, ex: `v1`)
- `owner_team` (minimo de 2 caracteres)
- `field_weights` (opcional, formato `campo -> peso`)
- `default_weight` (0.0..1.0, maior que 0)
- `auto_approve_threshold` (0.0..1.0)
- `manual_review_threshold` (0.0..1.0, menor ou igual ao auto approve)
- `missing_field_penalty` (0.0..1.0)
- `decision_mode` (`weighted_threshold`, `threshold`)
- `correlation_id` (opcional)

Saida core (`execute_s1_confidence_policy_main_flow`):
- `contrato_versao=conf.s1.core.v1`
- `correlation_id`
- `status=completed`
- `policy_id`
- `dataset_name`
- `confidence_policy`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`confs1coreevt-*`)
- `scaffold`

Saida service (`execute_s1_confidence_policy_service`):
- `contrato_versao=conf.s1.service.v1`
- `correlation_id`
- `status=completed`
- `policy_id`
- `dataset_name`
- `confidence_policy`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`confs1evt-*` + referencias do core)
- `scaffold`

## Observabilidade, telemetria e logs
Validacao, scaffold, core e observabilidade:
- loggers: `npbb.core.confidence.s1.validation`, `npbb.core.confidence.s1`, `npbb.core.confidence.s1.core`
- modulo de observabilidade: `core/confidence/s1_observability.py`
- ids: `observability_event_id` e `flow_*_event_id` com prefixo `confs1coreevt-`

Service e telemetria:
- logger: `app.services.confidence_policy`
- modulo de telemetria: `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- ids: `event_id` com prefixo `confs1evt-`

Ferramenta operacional:
- logger: `npbb.confidence_tools`
- eventos: `conf_s1_*`

Campos minimos para rastreio:
- `correlation_id`
- `policy_id`
- `dataset_name`
- `entity_kind`
- `decision_mode`
- `confidence_score`
- `decision`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/confidence_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/confidence_tools.py s1:validate-input \
  --policy-id CONF_LEAD_QUALITY_V1 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v1 \
  --owner-team etl \
  --field-weight nome=0.2 \
  --field-weight email=0.3 \
  --field-weight telefone=0.2 \
  --field-weight documento=0.3 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --missing-field-penalty 0.10 \
  --decision-mode weighted_threshold
```

Saida esperada:
- `[OK] s1:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/confidence_tools.py s1:simulate-core \
  --policy-id CONF_LEAD_QUALITY_V1 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v1 \
  --owner-team analytics \
  --field-weight nome=0.2 \
  --field-weight email=0.3 \
  --field-weight telefone=0.2 \
  --field-weight documento=0.3 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --missing-field-penalty 0.10 \
  --decision-mode weighted_threshold
```

Saida esperada:
- `[OK] s1:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/confidence_tools.py s1:simulate-service \
  --policy-id CONF_LEAD_QUALITY_V1 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v1 \
  --owner-team etl \
  --field-weight nome=0.2 \
  --field-weight email=0.3 \
  --field-weight telefone=0.2 \
  --field-weight documento=0.3 \
  --default-weight 0.1 \
  --auto-approve-threshold 0.85 \
  --manual-review-threshold 0.60 \
  --missing-field-penalty 0.10 \
  --decision-mode weighted_threshold
```

Saida esperada:
- `[OK] s1:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/confidence_tools.py s1:runbook-check
```

Saida esperada:
- `[OK] s1:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/confidence_tools.py \
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
`INVALID_POLICY_ID`:
- Sintoma: `policy_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_ENTITY_KIND`:
- Sintoma: `entity_kind` nao suportado.
- Acao: usar `lead`, `evento`, `ingresso` ou `generic`.

`INVALID_CONFIDENCE_THRESHOLDS`:
- Sintoma: `manual_review_threshold` maior que `auto_approve_threshold`.
- Acao: ajustar para `manual_review_threshold <= auto_approve_threshold`.

`INVALID_FIELD_WEIGHT` ou `INVALID_FIELD_WEIGHT_VALUE`:
- Sintoma: peso de campo invalido.
- Acao: usar pesos no intervalo `(0.0, 1.0]`.

`CONF_S1_SCORING_FAILED`:
- Sintoma: fluxo de score retornou status de falha.
- Acao: revisar `execucao.status`, `decision_reason` e regras de peso/limiar.

`INVALID_DECISION`:
- Sintoma: saida com decisao fora do contrato.
- Acao: retornar `auto_approve`, `manual_review` ou `reject`.

`MISSING_SCORE_RESULT_ID`:
- Sintoma: saida sem identificador de resultado de score.
- Acao: propagar `score_result_id` para rastreabilidade operacional.

`UNSUPPORTED_OUTPUT_CONTRACT_VERSION`:
- Sintoma: payload nao segue `conf.s1.core.v1` ou `conf.s1.service.v1`.
- Acao: corrigir camada emissora para contrato da sprint.

`CONF_S1_MAIN_FLOW_FAILED` ou `CONFIDENCE_POLICY_S1_FLOW_FAILED`:
- Sintoma: falha inesperada no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_motor_confianca_s1.py
pytest -q tests/test_motor_confianca_s1_observability.py
pytest -q tests/test_motor_confianca_s1_telemetry.py
python scripts/confidence_tools.py s1:runbook-check
```

## Limites da Sprint 1
- Fluxo focado em score por campo e politica de decisao base.
- Nao inclui calibracao estatistica automatizada do modelo.
- Nao inclui persistencia externa do score final.
