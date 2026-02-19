# Extracao IA por Formatos S4 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 4 de Extracao IA por Formato Delimitado (calibracao de qualidade por formato e consolidacao), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/extract/ai/s4_scaffold.py`
- `etl/extract/ai/s4_core.py`
- `etl/extract/ai/s4_observability.py`
- `etl/extract/ai/s4_validation.py`
- `backend/app/services/etl_extract_ai_service.py`
- `backend/app/services/extra-o-ia-por-formato-delimitado_telemetry.py`
- `scripts/extracao_ia_tools.py`

## Quando usar
- Validar rapidamente o contrato XIA S4 antes de integrar com executor real de IA calibrada.
- Simular fluxo principal calibrado e consolidacao cross-formato (core e service) em ambiente local.
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

## Contrato XIA S4 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf`, `docx`, `pptx`, `xlsx`, `csv`, `pdf_scan`, `jpg`, `png`)
- `source_uri` (texto >= 3 chars)
- `quality_profile_hint` (`strict_textual`, `table_sensitive`, `ocr_resilient`, `multimodal_document`)
- `consolidation_scope` (`single_source`, `batch_session`, `cross_format_event`)
- `output_normalization_profile` (`canonical_fields_v1`, `canonical_fields_v2`)
- `ia_model_provider` (`openai`, `azure_openai`, `anthropic`, `local`)
- `ia_model_name` (texto >= 2 chars)
- `chunk_strategy` (dependente do formato)
- `max_tokens_output` (int, 128..8192)
- `temperature` (float, 0..1)
- `correlation_id` (opcional)

Saida core (`execute_s4_ai_extract_main_flow`):
- `contrato_versao=xia.s4.core.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao` (`status`, `chunk_count`, `decision_reason`, `provider_response_id`, `consolidation_group_id`)
- `pontos_integracao`
- `observabilidade` (`xias4coreevt-*`)

Saida service (`execute_s4_extract_ai_service`):
- `contrato_versao=xia.s4.service.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`xias4evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.extract.ai.s4.core`, `npbb.etl.extract.ai.s4.validation`
- ids: `observability_event_id` (`xias4coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_extract_ai`
- ids: `telemetry_event_id` (`xias4evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `model_provider`
- `model_name`
- `chunk_strategy`
- `quality_profile_hint`
- `consolidation_scope`
- `output_normalization_profile`
- `chunk_count`
- `decision_reason`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/extracao_ia_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/extracao_ia_tools.py s4:validate-input \
  --source-id SRC_TMJ_S4_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --quality-profile-hint strict_textual \
  --consolidation-scope cross_format_event \
  --output-normalization-profile canonical_fields_v1 \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy page \
  --max-tokens-output 4096 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s4:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/extracao_ia_tools.py s4:simulate-core \
  --source-id SRC_TMJ_S4_XLSX_2025 \
  --source-kind xlsx \
  --source-uri file:///tmp/tmj_2025.xlsx \
  --quality-profile-hint table_sensitive \
  --consolidation-scope batch_session \
  --output-normalization-profile canonical_fields_v2 \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy sheet \
  --max-tokens-output 3072 \
  --temperature 0.1
```

Saida esperada:
- `[OK] s4:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/extracao_ia_tools.py s4:simulate-service \
  --source-id SRC_TMJ_S4_PNG_2025 \
  --source-kind png \
  --source-uri file:///tmp/tmj_2025.png \
  --quality-profile-hint ocr_resilient \
  --consolidation-scope cross_format_event \
  --output-normalization-profile canonical_fields_v1 \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy image \
  --max-tokens-output 2048 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s4:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/extracao_ia_tools.py s4:runbook-check
```

Saida esperada:
- `[OK] s4:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/extracao_ia_tools.py \
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
`INVALID_SOURCE_KIND`:
- Sintoma: formato da fonte nao suportado.
- Acao: usar `pdf`, `docx`, `pptx`, `xlsx`, `csv`, `pdf_scan`, `jpg` ou `png`.

`INVALID_QUALITY_PROFILE_HINT`:
- Sintoma: perfil de qualidade nao reconhecido.
- Acao: usar `strict_textual`, `table_sensitive`, `ocr_resilient` ou `multimodal_document`.

`INVALID_CONSOLIDATION_SCOPE`:
- Sintoma: escopo de consolidacao invalido.
- Acao: usar `single_source`, `batch_session` ou `cross_format_event`.

`INVALID_OUTPUT_NORMALIZATION_PROFILE`:
- Sintoma: perfil de normalizacao nao suportado.
- Acao: usar `canonical_fields_v1` ou `canonical_fields_v2`.

`INVALID_CHUNK_STRATEGY_FOR_SOURCE_KIND`:
- Sintoma: estrategia de chunk incompativel com `source_kind`.
- Acao: ajustar `chunk_strategy` para combinacao valida do formato.

`XIA_S4_EXTRACTION_FAILED`:
- Sintoma: executor retornou falha no fluxo principal.
- Acao: revisar logs de execucao calibrada e validar quality/consolidation/chunk strategy.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S4 (`core` ou `service`).

`ETL_EXTRACT_AI_S4_FLOW_FAILED`:
- Sintoma: falha nao prevista no service.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_extracao_ia_formatos_s4.py
pytest -q tests/test_etl_extract_ai_s4.py tests/test_etl_extract_ai_s4_observability.py tests/test_etl_extract_ai_s4_telemetry.py
python scripts/extracao_ia_tools.py s4:runbook-check
```

## Limites da Sprint 4
- Fluxo focado em calibracao de qualidade por formato e consolidacao com rastreabilidade operacional.
- Nao inclui persistencia final em camada canonica de negocio nem politicas avancadas de priorizacao por custo/latencia.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
