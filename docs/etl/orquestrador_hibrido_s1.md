# Orquestrador Hibrido S1 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 1 do Orquestrador de Extracao Hibrida (deterministico + IA), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/orchestrator/s1_scaffold.py`
- `etl/orchestrator/s1_core.py`
- `etl/orchestrator/s1_observability.py`
- `etl/orchestrator/s1_validation.py`
- `backend/app/services/etl_orchestrator_service.py`
- `backend/app/services/orquestrador-de-extra-o-h-brida-determin-stico-ia-_telemetry.py`
- `scripts/orquestrador_hibrido_tools.py`

## Quando usar
- Validar rapidamente contrato ORQ S1 antes de integrar com os proximos estagios do ETL.
- Simular roteamento no fluxo principal (core e service) em ambiente local.
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

## Contrato ORQ S1 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf`, `xlsx`, `csv`, `pptx`, `docx`, `other`)
- `source_uri` (texto >= 3 chars)
- `profile_strategy_hint` (opcional; para `pdf`: `text_table`, `ocr_or_assisted`, `hybrid`, `manual_assisted`, `empty_document`)
- `ia_habilitada` (bool)
- `permitir_fallback_manual` (bool)
- `correlation_id` (opcional)

Saida core (`execute_s1_orchestrator_main_flow`):
- `contrato_versao=orq.s1.core.v1`
- `correlation_id`
- `status=ready`
- `rota_selecionada`
- `politica_roteamento`
- `pontos_integracao`
- `observabilidade` (`orqs1coreevt-*`)

Saida service (`execute_s1_orchestrator_service`):
- `contrato_versao=orq.s1.service.v1`
- `correlation_id`
- `status=ready`
- `rota_selecionada`
- `politica_roteamento`
- `pontos_integracao`
- `observabilidade` (`orqs1evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.orchestrator.s1.core`, `npbb.etl.orchestrator.s1.validation`
- ids: `observability_event_id` (`orqs1coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_orchestrator`
- ids: `telemetry_event_id` (`orqs1evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `rota_selecionada` (quando disponivel)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/orquestrador_hibrido_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/orquestrador_hibrido_tools.py s1:validate-input \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --profile-strategy-hint hybrid \
  --ia-habilitada true \
  --permitir-fallback-manual true
```

Saida esperada:
- `[OK] s1:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/orquestrador_hibrido_tools.py s1:simulate-core \
  --source-id SRC_TMJ_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --ia-habilitada false \
  --permitir-fallback-manual true
```

Saida esperada:
- `[OK] s1:simulate-core`
- `flow_status: ready`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/orquestrador_hibrido_tools.py s1:simulate-service \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --profile-strategy-hint hybrid
```

Saida esperada:
- `[OK] s1:simulate-service`
- `flow_status: ready`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/orquestrador_hibrido_tools.py s1:runbook-check
```

Saida esperada:
- `[OK] s1:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/orquestrador_hibrido_tools.py \
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
`INVALID_SOURCE_ID`:
- Sintoma: `source_id` fora do padrao suportado.
- Acao: usar 3..160 chars com `A-Z`, `0-9` e `_`.

`INVALID_SOURCE_KIND`:
- Sintoma: tipo de fonte nao suportado.
- Acao: usar `pdf`, `xlsx`, `csv`, `pptx`, `docx` ou `other`.

`PROFILE_HINT_NOT_APPLICABLE`:
- Sintoma: `profile_strategy_hint` usado para fonte nao PDF.
- Acao: remover hint para `source_kind` diferente de `pdf`.

`ROUTE_UNAVAILABLE`:
- Sintoma: combinacao de flags sem rota valida.
- Acao: habilitar IA ou fallback manual para roteamento seguro.

`INVALID_OBSERVABILITY_OUTPUT`:
- Sintoma: IDs de observabilidade/telemetria fora do padrao esperado.
- Acao: validar propagacao de eventos `orqs1coreevt-*` e `orqs1evt-*`.

`ORQ_S1_MAIN_FLOW_FAILED` ou `ETL_ORCHESTRATOR_S1_FLOW_FAILED`:
- Sintoma: falha nao prevista no fluxo.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_orquestrador_hibrido_s1.py
pytest -q tests/test_etl_orchestrator_s1.py tests/test_etl_orchestrator_s1_observability.py tests/test_etl_orchestrator_s1_telemetry.py
python scripts/orquestrador_hibrido_tools.py s1:runbook-check
```

## Limites da Sprint 1
- Fluxo focado em contrato, politica de roteamento e rastreabilidade operacional.
- Nao inclui pipeline final de extracao persistente para todas as rotas.
- Evolucoes arquiteturais fora da sprint permanecem para tarefas seguintes.
