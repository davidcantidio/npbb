# Extracao IA por Formatos S2 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 2 de Extracao IA por Formato Delimitado (PPTX e XLSX/CSV nao padronizado), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/extract/ai/s2_scaffold.py`
- `etl/extract/ai/s2_core.py`
- `etl/extract/ai/s2_observability.py`
- `etl/extract/ai/s2_validation.py`
- `backend/app/services/etl_extract_ai_service.py`
- `backend/app/services/extra-o-ia-por-formato-delimitado_telemetry.py`
- `scripts/extracao_ia_tools.py`

## Quando usar
- Validar rapidamente o contrato XIA S2 antes de integrar com executor real de IA.
- Simular fluxo principal de extracao delimitada para PPTX/XLSX/CSV (core e service) em ambiente local.
- Executar checklist operacional da sprint sem depender de dados reais.
- Investigar falhas com `correlation_id`, `observability_event_id` e `telemetry_event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias instaladas.
- Para integracao completa, backend em execucao com configuracao de logs ativa.

Comando minimo:
```bash
python scripts/extracao_ia_tools.py --help
```

## Contrato XIA S2 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pptx`, `xlsx`, `csv`)
- `source_uri` (texto >= 3 chars)
- `document_profile_hint` (opcional: `pptx_social_metrics`, `pptx_slide_text`, `xlsx_non_standard`, `csv_non_standard`)
- `tabular_layout_hint` (opcional: `header_in_row_1`, `header_shifted`, `multi_header`, `unknown`)
- `ia_model_provider` (`openai`, `azure_openai`, `anthropic`, `local`)
- `ia_model_name` (texto >= 2 chars)
- `chunk_strategy` (`slide`, `sheet`, `row_block`)
- `max_tokens_output` (int, 128..8192)
- `temperature` (float, 0..1)
- `correlation_id` (opcional)

Saida core (`execute_s2_ai_extract_main_flow`):
- `contrato_versao=xia.s2.core.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao` (`status`, `chunk_count`, `decision_reason`, `provider_response_id`)
- `pontos_integracao`
- `observabilidade` (`xias2coreevt-*`)

Saida service (`execute_s2_extract_ai_service`):
- `contrato_versao=xia.s2.service.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`xias2evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.extract.ai.s2.core`, `npbb.etl.extract.ai.s2.validation`
- ids: `observability_event_id` (`xias2coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_extract_ai`
- ids: `telemetry_event_id` (`xias2evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `model_provider`
- `model_name`
- `chunk_strategy`
- `tabular_layout_hint`
- `chunk_count`
- `decision_reason`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/extracao_ia_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/extracao_ia_tools.py s2:validate-input \
  --source-id SRC_TMJ_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --document-profile-hint xlsx_non_standard \
  --tabular-layout-hint header_shifted \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy sheet \
  --max-tokens-output 3072 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s2:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/extracao_ia_tools.py s2:simulate-core \
  --source-id SRC_TMJ_PPTX_2025 \
  --source-kind pptx \
  --source-uri file:///tmp/tmj_2025.pptx \
  --document-profile-hint pptx_social_metrics \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy slide \
  --max-tokens-output 3072 \
  --temperature 0.1
```

Saida esperada:
- `[OK] s2:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/extracao_ia_tools.py s2:simulate-service \
  --source-id SRC_TMJ_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --document-profile-hint xlsx_non_standard \
  --tabular-layout-hint header_shifted \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy sheet \
  --max-tokens-output 2048 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s2:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/extracao_ia_tools.py s2:runbook-check
```

Saida esperada:
- `[OK] s2:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/extracao_ia_tools.py \
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
`INVALID_SOURCE_KIND`:
- Sintoma: formato da fonte nao suportado.
- Acao: usar `pptx`, `xlsx` ou `csv`.

`INVALID_CHUNK_STRATEGY_FOR_PPTX`:
- Sintoma: estrategia de chunk incompativel com PPTX.
- Acao: para `source_kind=pptx`, usar `chunk_strategy=slide`.

`INVALID_CHUNK_STRATEGY_FOR_TABULAR`:
- Sintoma: estrategia de chunk incompativel com XLSX/CSV.
- Acao: para `source_kind` tabular, usar `sheet` ou `row_block`.

`TABULAR_LAYOUT_HINT_NOT_APPLICABLE`:
- Sintoma: `tabular_layout_hint` enviado com `source_kind=pptx`.
- Acao: remover `tabular_layout_hint` para PPTX.

`INVALID_TABULAR_LAYOUT_HINT`:
- Sintoma: hint de layout nao reconhecido.
- Acao: usar `header_in_row_1`, `header_shifted`, `multi_header` ou `unknown`.

`XIA_S2_EXTRACTION_FAILED`:
- Sintoma: executor retornou falha no fluxo principal.
- Acao: revisar logs de execucao de IA e validar parametros de chunk/layout.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S2 (`core` ou `service`).

`ETL_EXTRACT_AI_S2_FLOW_FAILED`:
- Sintoma: falha nao prevista no service.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_extracao_ia_formatos_s2.py
pytest -q tests/test_etl_extract_ai_s2.py tests/test_etl_extract_ai_s2_observability.py tests/test_etl_extract_ai_s2_telemetry.py
python scripts/extracao_ia_tools.py s2:runbook-check
```

## Limites da Sprint 2
- Fluxo focado em extracao IA delimitada para PPTX e XLSX/CSV nao padronizado com rastreabilidade operacional.
- Nao inclui persistencia completa da resposta de modelo em armazenamento final nesta sprint.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
