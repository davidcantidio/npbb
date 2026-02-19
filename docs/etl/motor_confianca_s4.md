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
- `backend/app/services/confidence_policy_service.py`
- `tests/test_motor_confianca_s4.py`

## Quando usar
- Validar o contrato S4 antes de integrar o motor de confianca com pipelines de feedback real.
- Simular o fluxo principal de ajuste de threshold no core e no service.
- Investigar falhas de qualidade (`quality_drop`) e tuning (`threshold_delta`).

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

## Validacao local
Executar testes da sprint:
```bash
pytest -q tests/test_motor_confianca_s4.py
```

Validar sintaxe dos arquivos alterados:
```bash
python3 -m py_compile \
  core/confidence/s4_core.py \
  backend/app/services/confidence_policy_service.py \
  tests/test_motor_confianca_s4.py
```
