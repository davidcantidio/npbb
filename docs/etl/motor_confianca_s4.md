# Motor de Confianca S4 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 4 do epico Motor de Confianca e Politica de Decisao, com foco em:
- ajuste de thresholds com base em resultado real;
- guardrails de qualidade e congelamento de calibracao;
- contrato estavel de entrada/saida para core e service;
- logs e erros acionaveis para diagnostico rapido.

Arquivos principais da sprint:
- `core/confidence/s4_scaffold.py`
- `core/confidence/s4_core.py`
- `core/confidence/s4_validation.py`
- `core/confidence/s4_observability.py`
- `backend/app/services/confidence_policy_service.py`
- `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`
- `scripts/confidence_tools.py`
- `tests/test_motor_confianca_s4.py`
- `tests/test_motor_confianca_s4_observability.py`
- `tests/test_motor_confianca_s4_telemetry.py`

## Quando usar
- Validar o contrato S4 antes de integrar o motor de confianca com pipelines de feedback real.
- Simular o fluxo principal de ajuste de threshold no core e no service.
- Investigar falhas de qualidade (`quality_drop`) e tuning (`threshold_delta`).

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias do projeto instaladas.
- Logging ativo para rastrear eventos operacionais.

Comando minimo:
```bash
python scripts/confidence_tools.py --help
```

## Contrato CONF S4 (resumo)
Entrada principal:
- metadados da politica (`policy_id`, `dataset_name`, `entity_kind`, `schema_version`, `owner_team`)
- thresholds base (`auto_approve_threshold`, `manual_review_threshold`, `gap_threshold`)
- guardrails operacionais (`gap_escalation_required`, `max_manual_review_queue`)
- guardrails de campos criticos (`critical_fields`, `min_critical_fields_present`, `critical_violation_route`)
- calibracao por feedback real (`feedback_window_days`, `min_feedback_samples`, `auto_threshold_tuning_enabled`, `max_threshold_delta`, `quality_drop_tolerance`, `calibration_freeze_on_anomaly`)

Saida core (`execute_s4_confidence_policy_main_flow`):
- `contrato_versao=conf.s4.core.v1`
- `status=completed`
- `decision_policy`
- `execucao` com campos chave:
  - `status` (`succeeded|completed|success`)
  - `decision`
  - `confidence_score`
  - `threshold_delta_applied`
  - `tuned_thresholds`
  - `feedback_samples_count`
  - `quality_drop_value`
  - `quality_drop_detected`
  - `calibration_frozen`
- `observabilidade.flow_*_event_id` com prefixo `confs4coreevt-`

Saida service (`execute_s4_confidence_policy_service`):
- `contrato_versao=conf.s4.service.v1`
- `status=completed`
- `decision_policy`
- `execucao` (repasse do core)
- `observabilidade` com IDs do service (`confs4evt-*`) e do main flow (`confs4coreevt-*`)

## Guardrails e erros acionaveis
Codigos de erro relevantes do core:
- `CONF_S4_THRESHOLD_ADJUSTMENT_FAILED`
- `CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED`
- `INSUFFICIENT_FEEDBACK_FOR_THRESHOLD_TUNING`
- `THRESHOLD_DELTA_EXCEEDS_LIMIT`
- `INVALID_TUNED_THRESHOLDS`

Cada erro inclui:
- `code`
- `message`
- `action`
- `correlation_id`
- `stage`
- `event_id` (quando aplicavel)

## Pontos de integracao
Scaffold/Core:
- `conf_s4_prepare_endpoint`: `/internal/confidence/s4/prepare`
- `confidence_policy_s4_core_module`: `core.confidence.s4_core.execute_s4_confidence_policy_main_flow`
- `confidence_feedback_repository_module`: `core.confidence.feedback_repository`

Service:
- `confidence_policy_service_module`: `app.services.confidence_policy_service.execute_s4_confidence_policy_service`
- `confidence_policy_service_telemetry_module`: `app.services.confidence_policy_service`
- `confidence_policy_backend_telemetry_module`: `backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py`

Validacao:
- `confidence_policy_s4_validation_module`: `core.confidence.s4_validation.validate_s4_confidence_input_contract`
- `validate_s4_confidence_output_contract`: validacao de contrato de saida para `conf.s4.core.v1` e `conf.s4.service.v1`

## Ferramenta operacional
Arquivo:
- `scripts/confidence_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/confidence_tools.py s4:validate-input \
  --policy-id CONF_REPORT_POLICY_V4 \
  --dataset-name event_report_lines \
  --entity-kind evento \
  --schema-version v4 \
  --owner-team etl \
  --field-weight nome_evento=0.3 \
  --field-weight data_evento=0.3 \
  --field-weight local_evento=0.2 \
  --field-weight diretoria=0.2 \
  --decision-mode feedback_adjusted_thresholds \
  --feedback-window-days 30 \
  --min-feedback-samples 200 \
  --auto-threshold-tuning-enabled true \
  --max-threshold-delta 0.10 \
  --quality-drop-tolerance 0.05
```

Saida esperada:
- `[OK] s4:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/confidence_tools.py s4:simulate-core \
  --policy-id CONF_REPORT_POLICY_V4 \
  --dataset-name event_report_lines \
  --entity-kind evento \
  --schema-version v4 \
  --owner-team analytics \
  --field-weight nome_evento=0.3 \
  --field-weight data_evento=0.3 \
  --field-weight local_evento=0.2 \
  --field-weight diretoria=0.2 \
  --decision-mode feedback_adjusted_thresholds \
  --feedback-window-days 30 \
  --min-feedback-samples 200 \
  --auto-threshold-tuning-enabled true \
  --max-threshold-delta 0.10 \
  --quality-drop-tolerance 0.05
```

Saida esperada:
- `[OK] s4:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/confidence_tools.py s4:simulate-service \
  --policy-id CONF_REPORT_POLICY_V4 \
  --dataset-name event_report_lines \
  --entity-kind evento \
  --schema-version v4 \
  --owner-team etl \
  --field-weight nome_evento=0.3 \
  --field-weight data_evento=0.3 \
  --field-weight local_evento=0.2 \
  --field-weight diretoria=0.2 \
  --decision-mode feedback_adjusted_thresholds \
  --feedback-window-days 30 \
  --min-feedback-samples 200 \
  --auto-threshold-tuning-enabled true \
  --max-threshold-delta 0.10 \
  --quality-drop-tolerance 0.05
```

Saida esperada:
- `[OK] s4:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/confidence_tools.py s4:runbook-check
```

Saida esperada:
- `[OK] s4:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/confidence_tools.py \
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
`INVALID_DECISION_MODE`:
- Sintoma: `decision_mode` fora dos valores aceitos da Sprint 4.
- Acao: usar `feedback_adjusted_thresholds` ou `weighted_feedback_adjusted_thresholds`.

`INSUFFICIENT_FEEDBACK_FOR_THRESHOLD_TUNING`:
- Sintoma: amostra de feedback abaixo do minimo configurado.
- Acao: reduzir `min_feedback_samples` ou aguardar volume de feedback suficiente.

`THRESHOLD_DELTA_EXCEEDS_LIMIT`:
- Sintoma: ajuste de threshold acima de `max_threshold_delta`.
- Acao: reduzir delta aplicado ou aumentar limite dentro da politica aprovada.

`CONF_S4_QUALITY_DROP_GUARDRAIL_TRIGGERED`:
- Sintoma: queda de qualidade acima de `quality_drop_tolerance`.
- Acao: revisar calibracao e manter `calibration_freeze_on_anomaly=true` ate estabilizar.

## Validacao local
Executar testes da sprint:
```bash
pytest -q \
  tests/test_motor_confianca_s4.py \
  tests/test_motor_confianca_s4_observability.py \
  tests/test_motor_confianca_s4_telemetry.py
```

Validar sintaxe dos arquivos alterados:
```bash
python3 -m py_compile \
  core/confidence/s4_core.py \
  core/confidence/s4_validation.py \
  core/confidence/s4_observability.py \
  backend/app/services/confidence_policy_service.py \
  backend/app/services/motor-de-confian-a-e-pol-tica-de-decis-o_telemetry.py \
  scripts/confidence_tools.py \
  tests/test_motor_confianca_s4.py \
  tests/test_motor_confianca_s4_observability.py \
  tests/test_motor_confianca_s4_telemetry.py
```
