# Ingestao Inteligente S2 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 2 da Interface de Ingestao Inteligente (recepcao de lote + metadados), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id` e `lote_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/ingestao_inteligente/s2_scaffold.py`
- `frontend/src/features/ingestao_inteligente/s2_core.py`
- `frontend/src/features/ingestao_inteligente/s2_observability.py`
- `frontend/src/features/ingestao_inteligente/s2_validation.py`
- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/services/interface-de-ingest-o-inteligente-frontend-_telemetry.py`
- `scripts/ingestao_inteligente_tools.py`

## Quando usar
- Validar rapidamente contrato S2 antes de integrar frontend/backend.
- Simular fluxo principal de recepcao de lote com backend controlado.
- Executar checklist operacional da sprint sem depender de dados reais.
- Investigar falhas com `correlation_id`, `lote_id`, `observability_event_id` e `telemetry_event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias instaladas.
- Para endpoints reais, backend em execucao com autenticacao ativa.

Comando minimo:
```bash
python scripts/ingestao_inteligente_tools.py --help
```

## Contrato S2 (resumo)
Entrada (frontend/backend):
- `evento_id` (int > 0)
- `lote_id` (3..80, regex `[a-zA-Z0-9._-]`)
- `lote_nome` (texto >= 3 chars)
- `origem_lote` (texto >= 3 chars)
- `total_registros_estimados` (int >= 0)
- `arquivos` (1..100 itens)
- arquivo: `nome_arquivo`, `tamanho_arquivo_bytes`, `content_type`, `checksum_sha256` (opcional)
- `correlation_id` (opcional)

Saida scaffold (`POST /internal/ingestao-inteligente/s2/scaffold`):
- `contrato_versao`
- `correlation_id`
- `status=ready`
- `lote_id`
- `limites_lote`
- `pontos_integracao`
- `recepcao_lote`
- `observabilidade`

Saida lote upload (`POST /internal/ingestao-inteligente/s2/lote/upload`):
- `contrato_versao`
- `correlation_id`
- `lote_upload_id`
- `status=accepted`
- `evento_id`
- `lote_id`
- `recepcao_lote`
- `proxima_acao`
- `pontos_integracao`
- `observabilidade`

## Observabilidade e logs
Frontend:
- logger de validacao/contratos: `npbb.ingestao_inteligente.s2`
- ids de observabilidade: `observability_event_id` (`obs-*`)
- ids do core flow: `s2evt-*`

Backend:
- logger: `app.telemetry`
- ids: `telemetry_event_id` (`tel-*`)

Campos minimos para rastreio:
- `correlation_id`
- `evento_id`
- `lote_id`
- `lote_upload_id` (quando disponivel)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/ingestao_inteligente_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/ingestao_inteligente_tools.py s2:validate-input \
  --evento-id 2025 \
  --lote-id lote_tmj_2025_001 \
  --lote-nome "Lote TMJ 2025 001" \
  --origem-lote upload_manual \
  --total-registros-estimados 500 \
  --arquivo "tmj_eventos.csv|1024|text/csv" \
  --arquivo "tmj_eventos.xlsx|2048|application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
```

Saida esperada:
- `[OK] s2:validate-input`
- status `valid`

### 2) Simular fluxo principal
```bash
python scripts/ingestao_inteligente_tools.py s2:simulate-flow \
  --evento-id 2025 \
  --lote-id lote_tmj_2025_001 \
  --lote-nome "Lote TMJ 2025 001" \
  --origem-lote upload_manual \
  --total-registros-estimados 500 \
  --arquivo "tmj_eventos.csv|1024|text/csv" \
  --arquivo "tmj_eventos.xlsx|2048|application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  --backend-mode ok
```

Modos de backend para diagnostico:
- `ok`: retorna contrato valido.
- `incomplete`: resposta incompleta para testar validacao de saida.
- `invalid-status`: status inesperado no lote upload.
- `raise-error`: falha de comunicacao simulada.

### 3) Executar checklist de runbook
```bash
python scripts/ingestao_inteligente_tools.py s2:runbook-check
```

Saida esperada:
- `[OK] s2:runbook-check`
- `input_status: valid`
- `flow_status: accepted`
- `output_status: valid`

### 4) Saida em JSON
```bash
python scripts/ingestao_inteligente_tools.py \
  --output-format json \
  s2:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s2:validate-input`.
2. Simular fluxo com `s2:simulate-flow --backend-mode ok`.
3. Simular erro (`incomplete` ou `raise-error`) para confirmar mensagens acionaveis.
4. Executar `s2:runbook-check`.
5. Confirmar presenca de `correlation_id`, `lote_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_LOTE_ID`:
- Sintoma: identificador de lote fora do padrao.
- Acao: usar 3..80 chars em `[a-zA-Z0-9._-]`.

`BATCH_FILE_COUNT_MISMATCH`:
- Sintoma: total informado nao bate com lista de arquivos.
- Acao: sincronizar quantidade de arquivos e metadados enviados.

`BATCH_TOTAL_BYTES_MISMATCH`:
- Sintoma: total de bytes do lote diverge da soma dos itens.
- Acao: recalcular total de bytes com base nos arquivos reais.

`INVALID_CHECKSUM_SHA256`:
- Sintoma: hash nao e hexadecimal de 64 caracteres.
- Acao: recalcular SHA-256 no cliente antes de reenviar.

`INCOMPLETE_S2_LOTE_UPLOAD_RESPONSE`:
- Sintoma: resposta do backend sem campos obrigatorios.
- Acao: ajustar endpoint para respeitar contrato `s2.v1`.

`S2_MAIN_FLOW_FAILED` ou `INGESTAO_TOOL_UNEXPECTED_ERROR`:
- Sintoma: falha nao prevista no fluxo/ferramenta.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_ingestao_inteligente_s2.py tests/test_ingestao_inteligente_s2_observability.py
pytest -q backend/tests/test_ingestao_inteligente_endpoints.py backend/tests/test_ingestao_inteligente_telemetry_service.py
```

## Limites da Sprint 2
- Fluxo de recepcao de lote focado em validacao de contrato, rastreabilidade e integracao minima.
- O processamento final dos arquivos segue para etapas posteriores do pipeline.
- Evolucoes de arquitetura fora do escopo permanecem para tasks seguintes.
