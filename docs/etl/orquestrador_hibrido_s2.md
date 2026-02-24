# Orquestrador Hibrido S2 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 2 do Orquestrador de Extracao Hibrida (deterministico-first + fallback controlado), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/orchestrator/s2_scaffold.py`
- `etl/orchestrator/s2_core.py`
- `etl/orchestrator/s2_observability.py`
- `etl/orchestrator/s2_validation.py`
- `backend/app/services/etl_orchestrator_service.py`
- `backend/app/services/orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry.py`
- `scripts/orquestrador_hibrido_tools.py`

## Quando usar
- Validar rapidamente contrato ORQ S2 antes de integrar com extratores e etapas seguintes do ETL.
- Simular fluxo principal deterministic-first com fallback controlado (core e service) em ambiente local.
- Executar checklist operacional da sprint sem depender de dados reais.
- Investigar falhas com `correlation_id`, `observability_event_id` e `telemetry_event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias instaladas.
- Para integracao completa, backend em execucao com configuracao de logs ativa.

Comando minimo:
```bash
python scripts/orquestrador_hibrido_tools.py --help
```

## Contrato ORQ S2 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf`, `xlsx`, `csv`, `pptx`, `docx`, `other`)
- `source_uri` (texto >= 3 chars)
- `rota_selecionada` (`deterministic_tabular_extract`, `deterministic_pdf_extract`, `ia_assisted_pdf_extract`, `hybrid_pdf_extract`, `hybrid_document_extract`, `manual_assistido_review`)
- `ia_habilitada` (bool)
- `permitir_fallback_manual` (bool)
- `retry_attempts` (int, 0..3)
- `timeout_seconds` (int, 30..900)
- `correlation_id` (opcional)

Saida core (`execute_s2_orchestrator_main_flow`):
- `contrato_versao=orq.s2.core.v1`
- `correlation_id`
- `status=completed`
- `rota_selecionada` (rota final resolvida)
- `plano_execucao`
- `execucao` (`route_chain`, `attempts_trace`, `fallback_activated`, `final_route`)
- `pontos_integracao`
- `observabilidade` (`orqs2coreevt-*`)

Saida service (`execute_s2_orchestrator_service`):
- `contrato_versao=orq.s2.service.v1`
- `correlation_id`
- `status=completed`
- `rota_selecionada`
- `plano_execucao`
- `pontos_integracao`
- `observabilidade` (`orqs2evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.orchestrator.s2.core`, `npbb.etl.orchestrator.s2.validation`
- ids: `observability_event_id` (`orqs2coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_orchestrator`
- ids: `telemetry_event_id` (`orqs2evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `rota_selecionada` (quando disponivel)
- `route_name` e `attempt` (em tentativas)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/orquestrador_hibrido_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/orquestrador_hibrido_tools.py s2:validate-input \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --rota-selecionada hybrid_pdf_extract \
  --ia-habilitada true \
  --permitir-fallback-manual true \
  --retry-attempts 1 \
  --timeout-seconds 240
```

Saida esperada:
- `[OK] s2:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/orquestrador_hibrido_tools.py s2:simulate-core \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --rota-selecionada hybrid_pdf_extract \
  --ia-habilitada true \
  --permitir-fallback-manual true \
  --retry-attempts 1 \
  --timeout-seconds 240
```

Saida esperada:
- `[OK] s2:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/orquestrador_hibrido_tools.py s2:simulate-service \
  --source-id SRC_TMJ_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --rota-selecionada deterministic_tabular_extract \
  --ia-habilitada false \
  --permitir-fallback-manual true \
  --retry-attempts 0 \
  --timeout-seconds 180
```

Saida esperada:
- `[OK] s2:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/orquestrador_hibrido_tools.py s2:runbook-check
```

Saida esperada:
- `[OK] s2:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/orquestrador_hibrido_tools.py \
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
`INVALID_ROUTE_SELECTION`:
- Sintoma: rota nao suportada no contrato.
- Acao: usar uma das rotas previstas para a sprint.

`INVALID_ROUTE_FOR_SOURCE_KIND`:
- Sintoma: rota incompativel com `source_kind`.
- Acao: ajustar `rota_selecionada` para combinacao suportada.

`INVALID_RETRY_ATTEMPTS`:
- Sintoma: `retry_attempts` fora da politica.
- Acao: usar inteiro entre `0` e `3`.

`INVALID_TIMEOUT_SECONDS`:
- Sintoma: `timeout_seconds` fora do limite operacional.
- Acao: usar inteiro entre `30` e `900`.

`INVALID_ROUTE_EXECUTION_STATUS`:
- Sintoma: executor retornou status invalido.
- Acao: retornar status suportado (`success`, `failed`, `retryable_failure`, etc.).

`ORQ_S2_ROUTE_CHAIN_EXHAUSTED`:
- Sintoma: todas as rotas falharam apos retries/fallback.
- Acao: revisar falhas por rota e ajustar politica de fallback/retry.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S2 (`core` ou `service`).

`ORQ_S2_MAIN_FLOW_FAILED` ou `ETL_ORCHESTRATOR_S2_SCAFFOLD_FAILED`:
- Sintoma: falha nao prevista no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_orquestrador_hibrido_s2.py
pytest -q tests/test_etl_orchestrator_s2.py tests/test_etl_orchestrator_s2_observability.py tests/test_etl_orchestrator_s2_telemetry.py
python scripts/orquestrador_hibrido_tools.py s2:runbook-check
```

## Limites da Sprint 2
- Fluxo focado em politica deterministic-first, fallback controlado e rastreabilidade operacional.
- Nao inclui persistencia completa de todas as rotas de extracao no destino final.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
