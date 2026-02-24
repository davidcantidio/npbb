# Ingestao Inteligente S1 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 1 da Interface de Ingestao Inteligente (upload + selecao de evento), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/ingestao_inteligente/s1_scaffold.py`
- `frontend/src/features/ingestao_inteligente/s1_core.py`
- `frontend/src/features/ingestao_inteligente/s1_observability.py`
- `frontend/src/features/ingestao_inteligente/s1_validation.py`
- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/services/interface-de-ingest-o-inteligente-frontend-_telemetry.py`
- `scripts/ingestao_inteligente_tools.py`

## Quando usar
- Validar rapidamente contrato S1 antes de integrar frontend/backend.
- Simular fluxo principal com backend controlado em ambiente local.
- Executar checklist operacional da sprint sem depender de dados reais.
- Investigar falhas com `correlation_id`, `observability_event_id` e `telemetry_event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias instaladas.
- Para endpoints reais, backend em execucao com autenticacao ativa.

Comando minimo:
```bash
python scripts/ingestao_inteligente_tools.py --help
```

## Contrato S1 (resumo)
Entrada (frontend/backend):
- `evento_id` (int > 0)
- `nome_arquivo` (`.pdf`, `.xlsx`, `.csv`)
- `tamanho_arquivo_bytes` (1..26214400)
- `content_type` coerente com extensao
- `checksum_sha256` (opcional, 64 hex)
- `correlation_id` (opcional)

Saida scaffold (`POST /internal/ingestao-inteligente/s1/scaffold`):
- `contrato_versao`
- `correlation_id`
- `status`
- `limites_upload`
- `pontos_integracao`
- `observabilidade`

Saida upload (`POST /internal/ingestao-inteligente/s1/upload`):
- `contrato_versao`
- `correlation_id`
- `upload_id`
- `status=accepted`
- `arquivo`
- `proxima_acao`
- `pontos_integracao`
- `observabilidade`

## Observabilidade e logs
Frontend:
- logger: `npbb.ingestao_inteligente.s1`
- ids: `observability_event_id` (`obs-*`)

Backend:
- logger: `app.telemetry`
- ids: `telemetry_event_id` (`tel-*`)

Campos minimos para rastreio:
- `correlation_id`
- `evento_id`
- `upload_id` (quando disponivel)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/ingestao_inteligente_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/ingestao_inteligente_tools.py s1:validate-input \
  --evento-id 2025 \
  --nome-arquivo tmj_eventos.xlsx \
  --tamanho-arquivo-bytes 2048 \
  --content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

Saida esperada:
- `[OK] s1:validate-input`
- status `valid`

### 2) Simular fluxo principal
```bash
python scripts/ingestao_inteligente_tools.py s1:simulate-flow \
  --evento-id 2025 \
  --nome-arquivo tmj_eventos.xlsx \
  --tamanho-arquivo-bytes 2048 \
  --content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet \
  --backend-mode ok
```

Modos de backend para diagnostico:
- `ok`: retorna contrato valido.
- `incomplete`: resposta incompleta para testar validacao de saida.
- `invalid-status`: status inesperado no upload.
- `raise-error`: falha de comunicacao simulada.

### 3) Executar checklist de runbook
```bash
python scripts/ingestao_inteligente_tools.py s1:runbook-check
```

Saida esperada:
- `[OK] s1:runbook-check`
- `input_status: valid`
- `flow_status: accepted`
- `output_status: valid`

### 4) Saida em JSON
```bash
python scripts/ingestao_inteligente_tools.py \
  --output-format json \
  s1:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s1:validate-input`.
2. Simular fluxo com `s1:simulate-flow --backend-mode ok`.
3. Simular erro (`incomplete` ou `raise-error`) para confirmar mensagens acionaveis.
4. Executar `s1:runbook-check`.
5. Confirmar presenca de `correlation_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`UNSUPPORTED_FILE_EXTENSION`:
- Sintoma: extensao invalida.
- Acao: usar `.pdf`, `.xlsx` ou `.csv`.

`FILE_EXTENSION_CONTENT_TYPE_MISMATCH`:
- Sintoma: `content_type` nao bate com extensao.
- Acao: alinhar `content_type` enviado pelo cliente.

`FILE_TOO_LARGE`:
- Sintoma: arquivo acima de `MAX_UPLOAD_BYTES`.
- Acao: reduzir tamanho ou dividir lote.

`INVALID_CHECKSUM_SHA256`:
- Sintoma: hash nao e hexadecimal de 64 caracteres.
- Acao: recalcular SHA-256 no cliente e reenviar.

`EVENTO_NOT_FOUND`:
- Sintoma: evento nao existe no backend.
- Acao: selecionar evento valido antes do upload.

`S1_MAIN_FLOW_FAILED` ou `S1_TOOL_UNEXPECTED_ERROR`:
- Sintoma: falha nao prevista no fluxo/ferramenta.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_ingestao_inteligente_s1.py
pytest -q backend/tests/test_ingestao_inteligente_endpoints.py backend/tests/test_ingestao_inteligente_telemetry_service.py
```

## Limites da Sprint 1
- Upload aceito em contrato, sem pipeline final de processamento em producao.
- Fluxo focado em validacao, rastreabilidade e integracao minima.
- Evolucoes de arquitetura e processamento completo ficam para tasks seguintes.
