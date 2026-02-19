# Workbench Revisao Humana S1 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 1 do epico Workbench de Revisao Humana e Correspondencia de Faltantes, com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/revisao_humana/s1_scaffold.py`
- `frontend/src/features/revisao_humana/s1_core.py`
- `frontend/src/features/revisao_humana/s1_observability.py`
- `frontend/src/features/revisao_humana/s1_validation.py`
- `backend/app/routers/revisao_humana.py`
- `backend/app/services/workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry.py`
- `scripts/revisao_humana_tools.py`
- `tests/test_workbench_revisao_s1.py`

## Quando usar
- Validar rapidamente o contrato WORK S1 antes de integrar com camadas seguintes.
- Simular o fluxo principal de fila de revisao por campo (core e API interna).
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

## Contrato WORK S1 (resumo)
Entrada:
- `workflow_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `dataset_name` (minimo de 3 caracteres)
- `entity_kind` (`lead`, `evento`, `ingresso`, `generic`)
- `schema_version` (`vN`, ex: `v1`)
- `owner_team` (minimo de 2 caracteres)
- `required_fields` (opcional, usa defaults por `entity_kind`)
- `evidence_sources` (opcional, usa defaults `crm`, `formulario`)
- `default_priority` (`baixa`, `media`, `alta`, `critica`)
- `sla_hours` (1..720)
- `max_queue_size` (1..100000)
- `auto_assignment_enabled` (booleano)
- `reviewer_roles` (opcional, usa defaults `operador`, `supervisor`)
- `correlation_id` (opcional)

Saida scaffold (`build_s1_workbench_scaffold` e endpoint `/internal/revisao-humana/s1/prepare`):
- `contrato_versao=work.s1.v1`
- `correlation_id`
- `status=ready`
- `workflow_id`
- `dataset_name`
- `review_queue_policy`
- `pontos_integracao`

Saida core (`execute_workbench_revisao_s1_main_flow`):
- `contrato_versao=work.s1.core.v1`
- `correlation_id`
- `status=completed`
- `workflow_id`
- `dataset_name`
- `review_queue_policy`
- `execucao` (`status`, `queue_build_result_id`, `generated_items`, `queue_size`, etc)
- `pontos_integracao`
- `observabilidade` (`works1coreevt-*`)
- `scaffold`

Saida API execute (`/internal/revisao-humana/s1/execute`):
- mesmo contrato de saida do core (`work.s1.core.v1`)
- erros de validacao/execucao como `HTTP 422` com `code`, `message`, `action`, `correlation_id`, `stage`

## Observabilidade, telemetria e logs
Core e validacao:
- loggers: `npbb.frontend.revisao_humana.s1.core`, `npbb.frontend.revisao_humana.s1.validation`
- modulo de observabilidade: `frontend/src/features/revisao_humana/s1_observability.py`
- IDs: `observability_event_id` com prefixo `works1obsevt-`
- IDs do core: `flow_*_event_id` com prefixo `works1coreevt-`

API interna:
- logger: `app.routers.revisao_humana`
- eventos principais:
  - `workbench_revisao_s1_prepare_requested/completed/failed`
  - `workbench_revisao_s1_execute_requested/completed/failed`

Telemetria backend da sprint:
- modulo: `backend/app/services/workbench-de-revis-o-humana-e-correspond-ncia-de-faltantes_telemetry.py`
- ID: `telemetry_event_id` com prefixo `works1tmlevt-`

Ferramenta operacional:
- logger: `npbb.revisao_humana.tools`
- eventos: `work_s1_*`

Campos minimos para rastreio:
- `correlation_id`
- `workflow_id`
- `dataset_name`
- `entity_kind`
- `default_priority`
- `max_queue_size`
- `generated_items`
- `queue_size`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/revisao_humana_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/revisao_humana_tools.py s1:validate-input \
  --workflow-id WORK_REVIEW_LEAD_V1 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v1 \
  --owner-team etl \
  --required-field nome \
  --required-field email \
  --required-field telefone \
  --evidence-source crm \
  --evidence-source formulario \
  --default-priority media \
  --sla-hours 24 \
  --max-queue-size 1000 \
  --auto-assignment-enabled true \
  --reviewer-role operador \
  --reviewer-role supervisor
```

Saida esperada:
- `[OK] s1:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/revisao_humana_tools.py s1:simulate-core \
  --workflow-id WORK_REVIEW_LEAD_V1 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v1 \
  --owner-team etl \
  --required-field nome \
  --required-field email \
  --required-field telefone \
  --evidence-source crm \
  --evidence-source formulario \
  --default-priority media \
  --sla-hours 24 \
  --max-queue-size 1000 \
  --auto-assignment-enabled true \
  --reviewer-role operador \
  --reviewer-role supervisor
```

Saida esperada:
- `[OK] s1:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular integracao de API interna
```bash
python scripts/revisao_humana_tools.py s1:simulate-api \
  --workflow-id WORK_REVIEW_LEAD_V1 \
  --dataset-name leads_capture \
  --entity-kind lead \
  --schema-version v1 \
  --owner-team etl \
  --required-field nome \
  --required-field email \
  --required-field telefone \
  --evidence-source crm \
  --evidence-source formulario \
  --default-priority media \
  --sla-hours 24 \
  --max-queue-size 1000 \
  --auto-assignment-enabled true \
  --reviewer-role operador \
  --reviewer-role supervisor
```

Saida esperada:
- `[OK] s1:simulate-api`
- `prepare_status: ready`
- `flow_status: completed`
- `output_layer: core`

### 4) Executar checklist de runbook
```bash
python scripts/revisao_humana_tools.py s1:runbook-check
```

Saida esperada:
- `[OK] s1:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `api_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/revisao_humana_tools.py \
  --output-format json \
  s1:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s1:validate-input`.
2. Simular fluxo no core com `s1:simulate-core`.
3. Simular integracao de API com `s1:simulate-api`.
4. Executar `s1:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_WORKFLOW_ID`:
- Sintoma: `workflow_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_ENTITY_KIND`:
- Sintoma: `entity_kind` nao suportado.
- Acao: usar `lead`, `evento`, `ingresso` ou `generic`.

`INVALID_DEFAULT_PRIORITY`:
- Sintoma: prioridade invalida.
- Acao: usar `baixa`, `media`, `alta` ou `critica`.

`INVALID_MAX_QUEUE_SIZE`:
- Sintoma: capacidade de fila fora do intervalo.
- Acao: usar `max_queue_size` entre `1` e `100000`.

`AUTO_ASSIGNMENT_WITHOUT_ASSIGNMENTS`:
- Sintoma: auto atribuicao ativa sem itens atribuidos.
- Acao: ajustar retorno do executor para `assigned_items > 0` ou desativar auto atribuicao.

`WORK_S1_QUEUE_BUILD_FAILED`:
- Sintoma: falha no executor da fila.
- Acao: revisar logs por `correlation_id` e validar regras de campos/evidencias.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato `work.s1.core.v1`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_workbench_revisao_s1.py
python scripts/revisao_humana_tools.py s1:runbook-check
python scripts/revisao_humana_tools.py --output-format json s1:simulate-api --workflow-id WORK_REVIEW_LEAD_V1 --dataset-name leads_capture
```

## Limites da Sprint 1
- Fluxo focado em preparacao e execucao de fila de revisao por campo com evidencias.
- Nao inclui persistencia transacional da fila em banco nesta sprint.
- Nao inclui mecanismo de distribuicao assicrona de tarefas de revisao.

