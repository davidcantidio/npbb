# Extracao IA por Formatos S1 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 1 de Extracao IA por Formato Delimitado (DOCX e PDF digital), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `etl/extract/ai/s1_scaffold.py`
- `etl/extract/ai/s1_core.py`
- `etl/extract/ai/s1_observability.py`
- `etl/extract/ai/s1_validation.py`
- `backend/app/services/etl_extract_ai_service.py`
- `backend/app/services/extra-o-ia-por-formato-delimitado_telemetry.py`
- `scripts/extracao_ia_tools.py`

## Quando usar
- Validar rapidamente o contrato XIA S1 antes de integrar com executor real de IA.
- Simular fluxo principal de extracao delimitada (core e service) em ambiente local.
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

## Contrato XIA S1 (resumo)
Entrada:
- `source_id` (normalizado para `A-Z`, `0-9`, `_`, 3..160)
- `source_kind` (`pdf`, `docx`)
- `source_uri` (texto >= 3 chars)
- `document_profile_hint` (opcional, compativel com formato)
- `ia_model_provider` (`openai`, `azure_openai`, `anthropic`, `local`)
- `ia_model_name` (texto >= 2 chars)
- `chunk_strategy` (`section`, `page`, `paragraph`)
- `max_tokens_output` (int, 128..8192)
- `temperature` (float, 0..1)
- `correlation_id` (opcional)

Saida core (`execute_s1_ai_extract_main_flow`):
- `contrato_versao=xia.s1.core.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao` (`status`, `chunk_count`, `decision_reason`, `provider_response_id`)
- `pontos_integracao`
- `observabilidade` (`xias1coreevt-*`)

Saida service (`execute_s1_extract_ai_service`):
- `contrato_versao=xia.s1.service.v1`
- `correlation_id`
- `status=completed`
- `extraction_plan`
- `execucao`
- `pontos_integracao`
- `observabilidade` (`xias1evt-*` + referencias do main flow)

## Observabilidade e logs
Core e validacao:
- loggers: `npbb.etl.extract.ai.s1.core`, `npbb.etl.extract.ai.s1.validation`
- ids: `observability_event_id` (`xias1coreevt-*`)

Service e telemetria:
- logger: `app.services.etl_extract_ai`
- ids: `telemetry_event_id` (`xias1evt-*`)

Campos minimos para rastreio:
- `correlation_id`
- `source_id`
- `source_kind`
- `model_provider`
- `model_name`
- `chunk_strategy`
- `chunk_count`
- `decision_reason`
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/extracao_ia_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/extracao_ia_tools.py s1:validate-input \
  --source-id SRC_TMJ_PDF_2025 \
  --source-kind pdf \
  --source-uri file:///tmp/tmj_2025.pdf \
  --document-profile-hint pdf_digital \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy section \
  --max-tokens-output 2048 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s1:validate-input`
- status `valid`

### 2) Simular fluxo principal (core)
```bash
python scripts/extracao_ia_tools.py s1:simulate-core \
  --source-id SRC_TMJ_DOCX_2025 \
  --source-kind docx \
  --source-uri file:///tmp/tmj_2025.docx \
  --document-profile-hint docx_textual \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy section \
  --max-tokens-output 2048 \
  --temperature 0.1
```

Saida esperada:
- `[OK] s1:simulate-core`
- `flow_status: completed`
- `output_layer: core`

### 3) Simular fluxo de service
```bash
python scripts/extracao_ia_tools.py s1:simulate-service \
  --source-id SRC_TMJ_DOCX_2025 \
  --source-kind docx \
  --source-uri file:///tmp/tmj_2025.docx \
  --document-profile-hint docx_textual \
  --ia-model-provider openai \
  --ia-model-name gpt-4.1-mini \
  --chunk-strategy section \
  --max-tokens-output 1536 \
  --temperature 0.0
```

Saida esperada:
- `[OK] s1:simulate-service`
- `flow_status: completed`
- `output_layer: service`

### 4) Executar checklist de runbook
```bash
python scripts/extracao_ia_tools.py s1:runbook-check
```

Saida esperada:
- `[OK] s1:runbook-check`
- `input_status: valid`
- `core_validation_status: valid`
- `service_validation_status: valid`

### 5) Saida em JSON
```bash
python scripts/extracao_ia_tools.py \
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
`INVALID_SOURCE_KIND`:
- Sintoma: formato da fonte nao suportado.
- Acao: usar `pdf` ou `docx`.

`INVALID_DOCUMENT_PROFILE_HINT`:
- Sintoma: profile hint incompativel com formato.
- Acao: ajustar `document_profile_hint` para hint suportado por `source_kind`.

`INVALID_MAX_TOKENS_OUTPUT`:
- Sintoma: limite de tokens fora da faixa suportada.
- Acao: usar `max_tokens_output` entre `128` e `8192`.

`INVALID_TEMPERATURE`:
- Sintoma: temperatura fora da faixa operacional.
- Acao: usar `temperature` entre `0` e `1`.

`XIA_S1_EXTRACTION_FAILED`:
- Sintoma: executor retornou falha no fluxo principal.
- Acao: revisar logs de execucao de IA e validar parametros do modelo.

`INCOMPLETE_FLOW_OUTPUT`:
- Sintoma: payload sem campos obrigatorios do contrato.
- Acao: garantir retorno completo do contrato S1 (`core` ou `service`).

`ETL_EXTRACT_AI_S1_FLOW_FAILED`:
- Sintoma: falha nao prevista no service.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_extracao_ia_formatos_s1.py
pytest -q tests/test_etl_extract_ai_s1.py tests/test_etl_extract_ai_s1_observability.py tests/test_etl_extract_ai_s1_telemetry.py
python scripts/extracao_ia_tools.py s1:runbook-check
```

## Limites da Sprint 1
- Fluxo focado em extracao IA delimitada para DOCX e PDF digital com rastreabilidade operacional.
- Nao inclui persistencia de prompts/versionamento detalhado em banco nesta sprint.
- Evolucoes arquiteturais fora do escopo permanecem para tasks seguintes.
