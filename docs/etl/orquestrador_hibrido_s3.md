# Orquestrador Hibrido S3 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 3 do Orquestrador de Extracao Hibrida (agent-first + retentativas + circuit breaker), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/orchestrator/s3_scaffold.py`
- `etl/orchestrator/s3_core.py`
- `etl/orchestrator/s3_observability.py`
- `etl/orchestrator/s3_validation.py`
- `backend/app/services/etl_orchestrator_service.py`
- `backend/app/services/orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry.py`
- `scripts/orquestrador_hibrido_tools.py`

## Quando usar
- Validar rapidamente contrato ORQ S3 antes de integrar com executores reais de rota.
- Simular fluxo principal agent-first com retries e circuit breaker (core e service) em ambiente local.
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

## Contrato ORQ S3 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf`, `xlsx`, `csv`, `pptx`, `docx`, `other`)
- `source_uri` (texto >= 3 chars)
- `rota_selecionada` (`agent_first_extract`, `agent_pdf_extract`, `agent_tabular_extract`, `agent_document_extract`, `manual_assistido_review`)
- `agent_habilitado` (bool)
- `permitir_fallback_deterministico` (bool)
- `permitir_fallback_manual` (bool)
- `retry_attempts` (int, 0..5)
- `timeout_seconds` (int, 30..900)
- `circuit_breaker_failure_threshold` (int, 1..10)
- `circuit_breaker_reset_timeout_seconds` (int, 30..3600)
- `correlation_id` (opcional)

Saida core (`execute_s3_orchestrator_main_flow`):
- `contrato_versao=orq.s3.core.v1`
- `correlation_id`
- `status=completed`
- `rota_selecionada` (rota final resolvida)
- `plano_execucao`
- `execucao` (`route_chain`, `attempts_trace`, `fallback_activated`, `final_route`)
- `circuit_breaker` (`state`, `failure_threshold`, `consecutive_failures`)
- `pontos_integracao`
- `observabilidade` (`orqs3coreevt-*`)

Saida service (`execute_s3_orchestrator_service`):
- `contrato_versao=orq.s3.service.v1`
- `correlation_id`
- `status=completed`
- `rota_selecionada`
- `plano_execucao`
- `circuit_breaker`
- `pontos_integracao`
- `observabilidade` (`orqs3evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.orchestrator.s3.core`, `npbb.etl.orchestrator.s3.validation`
- ids: `observability_event_id` (`orqs3coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_orchestrator`
- ids: `telemetry_event_id` (`orqs3evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `rota_selecionada` (quando disponivel)
- `route_name` e `attempt` (em tentativas)
- `circuit_state` e `failure_threshold` (circuit breaker)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/orquestrador_hibrido_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/orquestrador_hibrido_tools.py s3:validate-input \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --rota-selecionada agent_first_extract \
  --agent-habilitado true \
  --permitir-fallback-deterministico true \
  --permitir-fallback-manual true \
  --retry-attempts 1 \
  --timeout-seconds 240 \
  --circuit-breaker-failure-threshold 3 \
  --circuit-breaker-reset-timeout-seconds 180
```

Saida esperada:
- `[OK] s3:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/orquestrador_hibrido_tools.py s3:simulate-core \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --rota-selecionada agent_first_extract \
  --agent-habilitado true \
  --permitir-fallback-deterministico true \
  --permitir-fallback-manual true \
  --retry-attempts 1 \
  --timeout-seconds 240 \
  --circuit-breaker-failure-threshold 3 \
  --circuit-breaker-reset-timeout-seconds 180
```

Saida esperada:
- `[OK] s3:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/orquestrador_hibrido_tools.py s3:simulate-service \
  --source-id SRC_TMJ_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --rota-selecionada agent_first_extract \
  --agent-habilitado true \
  --permitir-fallback-deterministico true \
  --permitir-fallback-manual true \
  --retry-attempts 0 \
  --timeout-seconds 240 \
  --circuit-breaker-failure-threshold 3 \
  --circuit-breaker-reset-timeout-seconds 180
```

Saida esperada:
- `[OK] s3:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/orquestrador_hibrido_tools.py s3:runbook-check
```

Saida esperada:
- `[OK] s3:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/orquestrador_hibrido_tools.py \
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
`INVALID_ROUTE_SELECTION`:
- Sintoma: rota nao suportada no contrato.
- Acao: usar uma das rotas previstas para a sprint.

`INVALID_ROUTE_FOR_SOURCE_KIND`:
- Sintoma: rota incompativel com `source_kind`.
- Acao: ajustar `rota_selecionada` para combinacao suportada.

`INVALID_CIRCUIT_BREAKER_FAILURE_THRESHOLD`:
- Sintoma: limiar de falhas fora da politica.
- Acao: usar inteiro entre `1` e `10`.

`INVALID_CIRCUIT_BREAKER_RESET_TIMEOUT`:
- Sintoma: tempo de reset fora do limite operacional.
- Acao: usar inteiro entre `30` e `3600`.

`ORQ_S3_CIRCUIT_BREAKER_OPEN`:
- Sintoma: circuit breaker abriu por falhas consecutivas.
- Acao: aguardar janela de reset e revisar falhas por rota.

`ORQ_S3_ROUTE_CHAIN_EXHAUSTED`:
- Sintoma: todas as rotas falharam apos retries/fallback.
- Acao: revisar falhas por rota e ajustar politica agent-first/fallback.

`INVALID_ROUTE_EXECUTION_STATUS`:
- Sintoma: executor retornou status invalido.
- Acao: retornar status suportado (`success`, `failed`, `retryable_failure`, etc.).

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S3 (`core` ou `service`).

`ETL_ORCHESTRATOR_S3_FLOW_FAILED`:
- Sintoma: falha nao prevista no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_orquestrador_hibrido_s3.py
pytest -q tests/test_etl_orchestrator_s3.py tests/test_etl_orchestrator_s3_observability.py tests/test_etl_orchestrator_s3_telemetry.py
python scripts/orquestrador_hibrido_tools.py s3:runbook-check
```

## Limites da Sprint 3
- Fluxo focado em politica agent-first, retentativas, circuit breaker e rastreabilidade operacional.
- Nao inclui persistencia completa de estado distribuido de circuit breaker em ambiente multi-no.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
