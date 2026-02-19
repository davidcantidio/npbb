# Workbench Revisao Humana S2 - Documentacao e Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 2 do epico Workbench de Revisao Humana e Correspondencia de Faltantes, com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/revisao_humana/s2_scaffold.py`
- `frontend/src/features/revisao_humana/s2_core.py`
- `frontend/src/features/revisao_humana/s2_observability.py`
- `frontend/src/features/revisao_humana/s2_validation.py`
- `backend/app/routers/revisao_humana.py`
- `backend/app/services/workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry.py`
- `scripts/revisao_humana_tools.py`
- `tests/test_workbench_revisao_s2.py`

## Quando usar
- Validar rapidamente o contrato WORK S2 antes de integrar com camadas seguintes.
- Simular o fluxo principal de correspondencia de campos faltantes (core e API interna).
- Executar checklist operacional da sprint em ambiente local.
- Investigar falhas com `correlation_id`, `observability_event_id` e `event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias instaladas.
- Para validacao de rotas internas, manter dependencias do backend disponiveis.

Comando minimo:
```bash
python scripts/revisao_humana_tools.py --help
```

## Contrato WORK S2 (resumo)
Entrada:
- `workflow_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `entity_kind` (`lead`, `evento`, `ingresso`, `generic`)
- `schema_version` (`vN`, ex: `v2`)
- `owner_team` (minimo de 2 caracteres)
- `missing_fields` (opcional, usa defaults por `entity_kind`)
- `candidate_sources` (opcional, usa defaults `crm`, `formulario`, `ocr`)
- `correspondence_mode` (`manual_confirm`, `suggest_only`, `semi_auto`)
- `match_strategy` (`exact`, `normalized`, `fuzzy`, `semantic`)
- `min_similarity_score` (`0.0..1.0`)
- `auto_apply_threshold` (`0.0..1.0`, deve ser `>= min_similarity_score`)
- `max_suggestions_per_field` (`1..50`)
- `require_evidence_for_suggestion` (booleano)
- `reviewer_roles` (opcional, usa defaults `operador`, `supervisor`)
- `correlation_id` (opcional)

Saida scaffold (`build_s2_workbench_scaffold` e endpoint `/internal/revisao-humana/s2/prepare`):
- `contrato_versao=work.s2.v1`
- `correlation_id`
- `status=ready`
- `workflow_id`
- `dataset_name`
- `correspondence_policy`
- `pontos_integracao`

Saida core (`execute_workbench_revisao_s2_main_flow`):
- `contrato_versao=work.s2.core.v1`
- `correlation_id`
- `status=completed`
- `workflow_id`
- `dataset_name`
- `correspondence_policy`
- `execucao` (`status`, `correspondence_result_id`, `suggested_matches`, `reviewed_matches`, etc)
- `pontos_integracao`
- `observabilidade` (`works2coreevt-*`)
- `scaffold`

Saida API execute (`/internal/revisao-humana/s2/execute`):
- mesmo contrato de saida do core (`work.s2.core.v1`)
- erros de validacao/execucao como `HTTP 422` com `code`, `message`, `action`, `correlation_id`, `stage`

## Observabilidade, telemetria e logs
Core e validacao:
- loggers: `npbb.frontend.revisao_humana.s2.core`, `npbb.frontend.revisao_humana.s2.validation`
- modulo de observabilidade: `frontend/src/features/revisao_humana/s2_observability.py`
- IDs: `observability_event_id` com prefixo `works2obsevt-`
- IDs do core: `flow_*_event_id` com prefixo `works2coreevt-`

API interna:
- logger: `app.routers.revisao_humana`
- eventos principais:
  - `workbench_revisao_s2_prepare_requested/completed/failed`
  - `workbench_revisao_s2_execute_requested/completed/failed`

Telemetria backend da sprint:
- modulo: `backend/app/services/workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry.py`
- ID: `telemetry_event_id` com prefixo `works2tmlevt-`

Ferramenta operacional:
- logger: `npbb.revisao_humana.tools`
- eventos: `work_s2_*`

Campos minimos para rastreio:
- `correlation_id`
- `workflow_id`
- `dataset_name`
- `entity_kind`
- `correspondence_mode`
- `match_strategy`
- `suggested_matches`
- `candidate_pairs_evaluated`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/revisao_humana_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/revisao_humana_tools.py s2:validate-input \
  --workflow-id WORK_REVIEW_LEAD_S2 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v2 \
  --owner-team etl \
  --missing-field nome \
  --missing-field email \
  --missing-field telefone \
  --candidate-source crm \
  --candidate-source formulario \
  --candidate-source ocr \
  --correspondence-mode manual_confirm \
  --match-strategy fuzzy \
  --min-similarity-score 0.70 \
  --auto-apply-threshold 0.95 \
  --max-suggestions-per-field 5 \
  --require-evidence-for-suggestion true \
  --reviewer-role operador \
  --reviewer-role supervisor
```

Saida esperada:
- `[OK] s2:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/revisao_humana_tools.py s2:simulate-core \
  --workflow-id WORK_REVIEW_LEAD_S2 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v2 \
  --owner-team etl \
  --missing-field nome \
  --missing-field email \
  --missing-field telefone \
  --candidate-source crm \
  --candidate-source formulario \
  --candidate-source ocr \
  --correspondence-mode manual_confirm \
  --match-strategy fuzzy \
  --min-similarity-score 0.70 \
  --auto-apply-threshold 0.95 \
  --max-suggestions-per-field 5 \
  --require-evidence-for-suggestion true \
  --reviewer-role operador \
  --reviewer-role supervisor
```

Saida esperada:
- `[OK] s2:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular integracao de API interna
```bash
python scripts/revisao_humana_tools.py s2:simulate-api \
  --workflow-id WORK_REVIEW_LEAD_S2 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v2 \
  --owner-team etl \
  --missing-field nome \
  --missing-field email \
  --missing-field telefone \
  --candidate-source crm \
  --candidate-source formulario \
  --candidate-source ocr \
  --correspondence-mode manual_confirm \
  --match-strategy fuzzy \
  --min-similarity-score 0.70 \
  --auto-apply-threshold 0.95 \
  --max-suggestions-per-field 5 \
  --require-evidence-for-suggestion true \
  --reviewer-role operador \
  --reviewer-role supervisor
```

Saida esperada:
- `[OK] s2:simulate-api`
- `prepare_status: ready`
- `flow_status: completed`
- `output_layer: core`

### 4) Executar checklist de runbook
```bash
python scripts/revisao_humana_tools.py s2:runbook-check
```

Saida esperada:
- `[OK] s2:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `api_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/revisao_humana_tools.py \
  --output-format json \
  s2:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s2:validate-input`.
2. Simular fluxo no core com `s2:simulate-core`.
3. Simular integracao de API com `s2:simulate-api`.
4. Executar `s2:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_WORKFLOW_ID`:
- Sintoma: `workflow_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_CORRESPONDENCE_MODE`:
- Sintoma: `correspondence_mode` nao suportado.
- Acao: usar `manual_confirm`, `suggest_only` ou `semi_auto`.

`INVALID_MATCH_STRATEGY`:
- Sintoma: `match_strategy` invalida.
- Acao: usar `exact`, `normalized`, `fuzzy` ou `semantic`.

`INVALID_CORRESPONDENCE_THRESHOLDS`:
- Sintoma: limiares inconsistentes (`auto_apply_threshold < min_similarity_score`).
- Acao: ajustar para `min_similarity_score <= auto_apply_threshold`.

`MISSING_EVIDENCE_LINKS`:
- Sintoma: sugestoes sem evidencias quando exigidas.
- Acao: retornar `evidence_links_count > 0` ou desativar exigencia de evidencia.

`WORK_S2_CORRESPONDENCE_FAILED`:
- Sintoma: falha no executor de correspondencia.
- Acao: revisar logs por `correlation_id` e validar regras de capacidade, modo e evidencia.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato `work.s2.core.v1`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_workbench_revisao_s2.py
python scripts/revisao_humana_tools.py s2:runbook-check
python scripts/revisao_humana_tools.py --output-format json s2:simulate-api --workflow-id WORK_REVIEW_LEAD_S2 --dataset-name leads_capture
```

## Limites da Sprint 2
- Fluxo focado na correspondencia de campos nao encontrados com politicas e metricas operacionais.
- Nao inclui persistencia transacional de sugestoes/decisoes em banco nesta sprint.
- Nao inclui consolidacao de feedback humano para recalibracao automatica de thresholds.
