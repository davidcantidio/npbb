# Extracao IA por Formatos S3 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 3 de Extracao IA por Formato Delimitado (PDF scan e JPG/PNG de documento), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/extract/ai/s3_scaffold.py`
- `etl/extract/ai/s3_core.py`
- `etl/extract/ai/s3_observability.py`
- `etl/extract/ai/s3_validation.py`
- `backend/app/services/etl_extract_ai_service.py`
- `backend/app/services/extra-o-ia-por-formato-delimitado_telemetry.py`
- `scripts/extracao_ia_tools.py`

## Quando usar
- Validar rapidamente o contrato XIA S3 antes de integrar com executor real de IA.
- Simular fluxo principal de extracao delimitada para PDF scan/JPG/PNG (core e service) em ambiente local.
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

## Contrato XIA S3 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf_scan`, `jpg`, `png`)
- `source_uri` (texto >= 3 chars)
- `document_profile_hint` (opcional: `pdf_scan_document`, `image_document`, `image_id_document`)
- `image_preprocess_hint` (opcional: `none`, `deskew`, `denoise`, `ocr_enhanced`)
- `ia_model_provider` (`openai`, `azure_openai`, `anthropic`, `local`)
- `ia_model_name` (texto >= 2 chars)
- `chunk_strategy` (`page`, `image`, `region`)
- `max_tokens_output` (int, 128..8192)
- `temperature` (float, 0..1)
- `correlation_id` (opcional)

Saida core (`execute_s3_ai_extract_main_flow`):
- `contrato_versao=xia.s3.core.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao` (`status`, `chunk_count`, `decision_reason`, `provider_response_id`)
- `pontos_integracao`
- `observabilidade` (`xias3coreevt-*`)

Saida service (`execute_s3_extract_ai_service`):
- `contrato_versao=xia.s3.service.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`xias3evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.extract.ai.s3.core`, `npbb.etl.extract.ai.s3.validation`
- ids: `observability_event_id` (`xias3coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_extract_ai`
- ids: `telemetry_event_id` (`xias3evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `model_provider`
- `model_name`
- `chunk_strategy`
- `image_preprocess_hint`
- `chunk_count`
- `decision_reason`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/extracao_ia_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/extracao_ia_tools.py s3:validate-input \
  --source-id SRC_TMJ_PDFSCAN_2025 \
  --source-kind pdf_scan \
  --source-uri file:///tmp/tmj_2025_scan.pdf \
  --document-profile-hint pdf_scan_document \
  --image-preprocess-hint ocr_enhanced \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy page \
  --max-tokens-output 4096 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s3:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/extracao_ia_tools.py s3:simulate-core \
  --source-id SRC_TMJ_PNG_2025 \
  --source-kind png \
  --source-uri file:///tmp/tmj_2025.png \
  --document-profile-hint image_document \
  --image-preprocess-hint denoise \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy image \
  --max-tokens-output 3072 \
  --temperature 0.1
```

Saida esperada:
- `[OK] s3:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/extracao_ia_tools.py s3:simulate-service \
  --source-id SRC_TMJ_JPG_2025 \
  --source-kind jpg \
  --source-uri file:///tmp/tmj_2025.jpg \
  --document-profile-hint image_document \
  --image-preprocess-hint denoise \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy image \
  --max-tokens-output 2048 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s3:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/extracao_ia_tools.py s3:runbook-check
```

Saida esperada:
- `[OK] s3:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/extracao_ia_tools.py \
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
`INVALID_SOURCE_KIND`:
- Sintoma: formato da fonte nao suportado.
- Acao: usar `pdf_scan`, `jpg` ou `png`.

`INVALID_CHUNK_STRATEGY_FOR_PDF_SCAN`:
- Sintoma: estrategia de chunk incompativel com PDF scan.
- Acao: para `source_kind=pdf_scan`, usar `chunk_strategy=page`.

`INVALID_CHUNK_STRATEGY_FOR_IMAGE`:
- Sintoma: estrategia de chunk incompativel com JPG/PNG.
- Acao: para `source_kind` imagem, usar `image` ou `region`.

`INVALID_IMAGE_PREPROCESS_HINT`:
- Sintoma: hint de preprocessamento nao reconhecido.
- Acao: usar `none`, `deskew`, `denoise` ou `ocr_enhanced`.

`INVALID_IMAGE_PREPROCESS_HINT_FOR_PDF_SCAN`:
- Sintoma: `image_preprocess_hint=none` em PDF scan.
- Acao: para PDF scan usar `deskew`, `denoise` ou `ocr_enhanced`.

`XIA_S3_EXTRACTION_FAILED`:
- Sintoma: executor retornou falha no fluxo principal.
- Acao: revisar logs de execucao de IA e validar preprocessamento/chunk strategy.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S3 (`core` ou `service`).

`ETL_EXTRACT_AI_S3_FLOW_FAILED`:
- Sintoma: falha nao prevista no service.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_extracao_ia_formatos_s3.py
pytest -q tests/test_etl_extract_ai_s3.py tests/test_etl_extract_ai_s3_observability.py tests/test_etl_extract_ai_s3_telemetry.py
python scripts/extracao_ia_tools.py s3:runbook-check
```

## Limites da Sprint 3
- Fluxo focado em extracao IA delimitada para PDF scan/JPG/PNG com rastreabilidade operacional.
- Nao inclui pipeline de OCR persistente completo com tuning de imagem por tipo de fonte nesta sprint.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
