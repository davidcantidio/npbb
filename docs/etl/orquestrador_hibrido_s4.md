# Orquestrador Hibrido S4 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 4 do Orquestrador de Extracao Hibrida (telemetria de decisao, custo e latencia), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/orchestrator/s4_scaffold.py`
- `etl/orchestrator/s4_core.py`
- `etl/orchestrator/s4_observability.py`
- `etl/orchestrator/s4_validation.py`
- `backend/app/services/etl_orchestrator_service.py`
- `backend/app/services/orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry.py`
- `scripts/orquestrador_hibrido_tools.py`

## Quando usar
- Validar rapidamente contrato ORQ S4 antes de integrar com executores reais de rota.
- Simular fluxo principal com telemetria de decisao e governanca de custo/latencia (core e service) em ambiente local.
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

## Contrato ORQ S4 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf`, `xlsx`, `csv`, `pptx`, `docx`, `other`)
- `source_uri` (texto >= 3 chars)
- `rota_selecionada` (rotas deterministicas, hibridas, agent-first e manual)
- `decisao_telemetria_habilitada` (bool)
- `custo_estimado_usd` (float, 0..10000)
- `custo_orcamento_usd` (float, 0.01..10000)
- `latencia_estimada_ms` (int, 1..600000)
- `latencia_sla_ms` (int, 1..600000)
- `telemetria_amostragem` (float, 0..1)
- `correlation_id` (opcional)

Saida core (`execute_s4_orchestrator_main_flow`):
- `contrato_versao=orq.s4.core.v1`
- `correlation_id`
- `status=completed`
- `rota_selecionada`
- `plano_telemetria`
- `governanca_custo_latencia` (`custo_status`, `latencia_status`)
- `execucao` (`decision_reason`, `latency_ms`, `cost_usd`, `status`)
- `pontos_integracao`
- `observabilidade` (`orqs4coreevt-*`)

Saida service (`execute_s4_orchestrator_service`):
- `contrato_versao=orq.s4.service.v1`
- `correlation_id`
- `status=completed`
- `rota_selecionada`
- `plano_telemetria`
- `governanca_custo_latencia`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`orqs4evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.orchestrator.s4.core`, `npbb.etl.orchestrator.s4.validation`
- ids: `observability_event_id` (`orqs4coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_orchestrator`
- ids: `telemetry_event_id` (`orqs4evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `rota_selecionada` (quando disponivel)
- `decision_reason` e `attempt`
- `latency_ms`, `cost_usd`
- `custo_status`, `latencia_status`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/orquestrador_hibrido_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/orquestrador_hibrido_tools.py s4:validate-input \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --rota-selecionada agent_first_extract \
  --decisao-telemetria-habilitada true \
  --custo-estimado-usd 0.2 \
  --custo-orcamento-usd 1.0 \
  --latencia-estimada-ms 1200 \
  --latencia-sla-ms 3000 \
  --telemetria-amostragem 1.0
```

Saida esperada:
- `[OK] s4:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/orquestrador_hibrido_tools.py s4:simulate-core \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --rota-selecionada agent_first_extract \
  --decisao-telemetria-habilitada true \
  --custo-estimado-usd 0.2 \
  --custo-orcamento-usd 1.0 \
  --latencia-estimada-ms 1200 \
  --latencia-sla-ms 3000 \
  --telemetria-amostragem 1.0
```

Saida esperada:
- `[OK] s4:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/orquestrador_hibrido_tools.py s4:simulate-service \
  --source-id SRC_TMJ_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --rota-selecionada agent_tabular_extract \
  --decisao-telemetria-habilitada true \
  --custo-estimado-usd 0.15 \
  --custo-orcamento-usd 1.0 \
  --latencia-estimada-ms 900 \
  --latencia-sla-ms 3000 \
  --telemetria-amostragem 0.75
```

Saida esperada:
- `[OK] s4:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/orquestrador_hibrido_tools.py s4:runbook-check
```

Saida esperada:
- `[OK] s4:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/orquestrador_hibrido_tools.py \
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
`INVALID_ROUTE_SELECTION`:
- Sintoma: rota nao suportada no contrato.
- Acao: usar uma das rotas previstas para a sprint.

`INVALID_ROUTE_FOR_SOURCE_KIND`:
- Sintoma: rota incompativel com `source_kind`.
- Acao: ajustar `rota_selecionada` para combinacao suportada.

`COST_ESTIMATE_EXCEEDS_BUDGET`:
- Sintoma: custo estimado excede orcamento.
- Acao: ajustar rota/parametros para reduzir custo ou elevar orcamento.

`TELEMETRY_DISABLED_REQUIRES_ZERO_SAMPLING`:
- Sintoma: amostragem diferente de zero com telemetria desabilitada.
- Acao: definir `telemetria_amostragem=0` ou habilitar telemetria.

`INVALID_ROUTE_EXECUTION_STATUS`:
- Sintoma: executor retornou status invalido.
- Acao: retornar status suportado (`succeeded`, `failed`, `timeout`, etc.).

`ORQ_S4_ROUTE_EXECUTION_FAILED`:
- Sintoma: falha de execucao de rota no fluxo principal.
- Acao: revisar logs por `correlation_id` e validar decisao/parametros operacionais.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S4 (`core` ou `service`).

`ETL_ORCHESTRATOR_S4_FLOW_FAILED`:
- Sintoma: falha nao prevista no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_orquestrador_hibrido_s4.py
pytest -q tests/test_etl_orchestrator_s4.py tests/test_etl_orchestrator_s4_observability.py tests/test_etl_orchestrator_s4_telemetry.py
python scripts/orquestrador_hibrido_tools.py s4:runbook-check
```

## Limites da Sprint 4
- Fluxo focado em telemetria de decisao e governanca de custo/latencia com rastreabilidade operacional.
- Nao inclui billing real por provedor nem controle distribuido de budget compartilhado entre multiplos workers.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
