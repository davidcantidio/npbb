# Workbench Revisao Humana S3 - Documentacao e Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 3 do epico Workbench de Revisao Humana e Correspondencia de Faltantes, com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/revisao_humana/s3_scaffold.py`
- `frontend/src/features/revisao_humana/s3_core.py`
- `frontend/src/features/revisao_humana/s3_observability.py`
- `frontend/src/features/revisao_humana/s3_validation.py`
- `backend/app/routers/revisao_humana.py`
- `backend/app/services/workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry.py`
- `scripts/revisao_humana_tools.py`
- `tests/test_workbench_revisao_s3.py`

## Quando usar
- Validar rapidamente o contrato WORK S3 antes de integrar com camadas seguintes.
- Simular o fluxo principal de operacoes em lote e aprovacao (core e API interna).
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

## Contrato WORK S3 (resumo)
Entrada:
- `workflow_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `entity_kind` (`lead`, `evento`, `ingresso`, `generic`)
- `schema_version` (`vN`, ex: `v3`)
- `owner_team` (minimo de 2 caracteres)
- `batch_size` (`1..10000`)
- `max_pending_batches` (`1..10000`, deve ser `>= batch_size`)
- `approval_mode` (`single_reviewer`, `dual_control`, `committee`)
- `required_approvers` (`1..5`, consistente com `approval_mode`)
- `approver_roles` (opcional, usa defaults `supervisor`, `coordenador`)
- `approval_sla_hours` (`1..720`)
- `require_justification` (booleano)
- `allow_partial_approval` (booleano)
- `auto_lock_on_conflict` (booleano)
- `correlation_id` (opcional)

Saida scaffold (`build_s3_workbench_scaffold` e endpoint `/internal/revisao-humana/s3/prepare`):
- `contrato_versao=work.s3.v1`
- `correlation_id`
- `status=ready`
- `workflow_id`
- `dataset_name`
- `batch_approval_policy`
- `pontos_integracao`

Saida core (`execute_workbench_revisao_s3_main_flow`):
- `contrato_versao=work.s3.core.v1`
- `correlation_id`
- `status=completed`
- `workflow_id`
- `dataset_name`
- `batch_approval_policy`
- `execucao` (`status`, `batch_approval_result_id`, `batches_received`, `batches_approved`, etc)
- `pontos_integracao`
- `observabilidade` (`works3coreevt-*`)
- `scaffold`

Saida API execute (`/internal/revisao-humana/s3/execute`):
- mesmo contrato de saida do core (`work.s3.core.v1`)
- erros de validacao/execucao como `HTTP 422` com `code`, `message`, `action`, `correlation_id`, `stage`

## Observabilidade, telemetria e logs
Core e validacao:
- loggers: `npbb.frontend.revisao_humana.s3.core`, `npbb.frontend.revisao_humana.s3.validation`
- modulo de observabilidade: `frontend/src/features/revisao_humana/s3_observability.py`
- IDs: `observability_event_id` com prefixo `works3obsevt-`
- IDs do core: `flow_*_event_id` com prefixo `works3coreevt-`

API interna:
- logger: `app.routers.revisao_humana`
- eventos principais:
  - `workbench_revisao_s3_prepare_requested/completed/failed`
  - `workbench_revisao_s3_execute_requested/completed/failed`

Telemetria backend da sprint:
- modulo: `backend/app/services/workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry.py`
- ID: `telemetry_event_id` com prefixo `works3tmlevt-`

Ferramenta operacional:
- logger: `npbb.revisao_humana.tools`
- eventos: `work_s3_*`

Campos minimos para rastreio:
- `correlation_id`
- `workflow_id`
- `dataset_name`
- `entity_kind`
- `approval_mode`
- `required_approvers`
- `batches_received`
- `pending_batches`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/revisao_humana_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/revisao_humana_tools.py s3:validate-input \
  --workflow-id WORK_REVIEW_LEAD_S3 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v3 \
  --owner-team etl \
  --batch-size 200 \
  --max-pending-batches 2000 \
  --approval-mode dual_control \
  --required-approvers 2 \
  --approver-role supervisor \
  --approver-role coordenador \
  --approval-sla-hours 24 \
  --require-justification true \
  --allow-partial-approval false \
  --auto-lock-on-conflict true
```

Saida esperada:
- `[OK] s3:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/revisao_humana_tools.py s3:simulate-core \
  --workflow-id WORK_REVIEW_LEAD_S3 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v3 \
  --owner-team etl \
  --batch-size 200 \
  --max-pending-batches 2000 \
  --approval-mode dual_control \
  --required-approvers 2 \
  --approver-role supervisor \
  --approver-role coordenador \
  --approval-sla-hours 24 \
  --require-justification true \
  --allow-partial-approval false \
  --auto-lock-on-conflict true
```

Saida esperada:
- `[OK] s3:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular integracao de API interna
```bash
python scripts/revisao_humana_tools.py s3:simulate-api \
  --workflow-id WORK_REVIEW_LEAD_S3 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v3 \
  --owner-team etl \
  --batch-size 200 \
  --max-pending-batches 2000 \
  --approval-mode dual_control \
  --required-approvers 2 \
  --approver-role supervisor \
  --approver-role coordenador \
  --approval-sla-hours 24 \
  --require-justification true \
  --allow-partial-approval false \
  --auto-lock-on-conflict true
```

Saida esperada:
- `[OK] s3:simulate-api`
- `prepare_status: ready`
- `flow_status: completed`
- `output_layer: core`

### 4) Executar checklist de runbook
```bash
python scripts/revisao_humana_tools.py s3:runbook-check
```

Saida esperada:
- `[OK] s3:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `api_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/revisao_humana_tools.py \
  --output-format json \
  s3:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s3:validate-input`.
2. Simular fluxo no core com `s3:simulate-core`.
3. Simular integracao de API com `s3:simulate-api`.
4. Executar `s3:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_WORKFLOW_ID`:
- Sintoma: `workflow_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_APPROVAL_MODE`:
- Sintoma: `approval_mode` nao suportado.
- Acao: usar `single_reviewer`, `dual_control` ou `committee`.

`INVALID_REQUIRED_APPROVERS`:
- Sintoma: quantidade de aprovadores invalida para o modo de aprovacao.
- Acao: ajustar `required_approvers` conforme regras do `approval_mode`.

`INVALID_PENDING_BATCH_CAPACITY`:
- Sintoma: `max_pending_batches` menor que `batch_size`.
- Acao: ajustar para `max_pending_batches >= batch_size`.

`INVALID_PARTIAL_APPROVALS`:
- Sintoma: `partial_approvals` diferente de zero com `allow_partial_approval=false`.
- Acao: retornar `partial_approvals=0` ou habilitar parcial.

`MISSING_APPROVAL_JUSTIFICATIONS`:
- Sintoma: rejeicoes/escalonamentos sem justificativas obrigatorias.
- Acao: propagar justificativas para todos os casos exigidos.

`WORK_S3_BATCH_APPROVAL_FAILED`:
- Sintoma: falha no executor de aprovacao em lote.
- Acao: revisar logs por `correlation_id` e validar regras de aprovacao, conflito e capacidade.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato `work.s3.core.v1`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_workbench_revisao_s3.py
python scripts/revisao_humana_tools.py s3:runbook-check
python scripts/revisao_humana_tools.py --output-format json s3:simulate-api --workflow-id WORK_REVIEW_LEAD_S3 --dataset-name leads_capture
```

## Limites da Sprint 3
- Fluxo focado em operacoes em lote e aprovacao com regras de consistencia e rastreabilidade.
- Nao inclui persistencia transacional da fila de aprovacao em banco nesta sprint.
- Nao inclui motor de escalonamento externo assicrono ou governanca de SLA cross-service.
