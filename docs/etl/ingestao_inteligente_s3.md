# Ingestao Inteligente S3 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 3 da Interface de Ingestao Inteligente (monitoramento de status + reprocessamento), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`, `lote_id` e `lote_upload_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/ingestao_inteligente/s3_scaffold.py`
- `frontend/src/features/ingestao_inteligente/s3_core.py`
- `frontend/src/features/ingestao_inteligente/s3_observability.py`
- `frontend/src/features/ingestao_inteligente/s3_validation.py`
- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/services/interface-de-ingest-o-inteligente-frontend-_telemetry.py`
- `scripts/ingestao_inteligente_tools.py`

## Quando usar
- Validar rapidamente contrato S3 antes de integrar frontend/backend.
- Simular fluxo principal de monitoramento e reprocessamento com backend controlado.
- Executar checklist operacional da sprint sem depender de dados reais.
- Investigar falhas com `correlation_id`, `lote_id`, `lote_upload_id`, `observability_event_id` e `telemetry_event_id`.

## Pre-requisitos
- Executar comandos a partir da raiz `npbb/`.
- Ambiente Python com dependencias instaladas.
- Para endpoints reais, backend em execucao com autenticacao ativa.

Comando minimo:
```bash
python scripts/ingestao_inteligente_tools.py --help
```

## Contrato S3 (resumo)
Entrada (frontend/backend):
- `evento_id` (int > 0)
- `lote_id` (3..80, regex `[a-zA-Z0-9._-]`)
- `lote_upload_id` (regex `lot-[a-z0-9]{6,64}`)
- `status_processamento` (`queued`, `processing`, `completed`, `failed`, `partial_success`, `cancelled`)
- `tentativas_reprocessamento` (0..5)
- `reprocessamento_habilitado` (bool)
- `motivo_reprocessamento` (opcional, recomendado para auditoria)
- `correlation_id` (opcional)

Saida status (`POST /internal/ingestao-inteligente/s3/status`):
- `contrato_versao`
- `correlation_id`
- `status=ready`
- `evento_id`
- `lote_id`
- `lote_upload_id`
- `status_processamento`
- `proxima_acao`
- `monitoramento_status`
- `pontos_integracao`
- `observabilidade`

Saida reprocessamento (`POST /internal/ingestao-inteligente/s3/reprocessar`):
- `contrato_versao`
- `correlation_id`
- `reprocessamento_id`
- `status=accepted`
- `evento_id`
- `lote_id`
- `lote_upload_id`
- `status_anterior`
- `status_reprocessamento`
- `tentativas_reprocessamento`
- `proxima_acao`
- `pontos_integracao`
- `observabilidade`

## Observabilidade e logs
Frontend:
- logger de validacao/contratos: `npbb.ingestao_inteligente.s3`
- ids de observabilidade: `observability_event_id` (`obs-*`)
- ids do core flow: `s3evt-*`

Backend:
- logger: `app.telemetry`
- ids: `telemetry_event_id` (`tel-*`)

Campos minimos para rastreio:
- `correlation_id`
- `evento_id`
- `lote_id`
- `lote_upload_id`
- `reprocessamento_id` (quando disponivel)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/ingestao_inteligente_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/ingestao_inteligente_tools.py s3:validate-input \
  --evento-id 2025 \
  --lote-id lote_tmj_2025_001 \
  --lote-upload-id lot-abc123def456 \
  --status-processamento processing \
  --tentativas-reprocessamento 1 \
  --reprocessamento-habilitado true
```

Saida esperada:
- `[OK] s3:validate-input`
- status `valid`

### 2) Simular fluxo principal
```bash
python scripts/ingestao_inteligente_tools.py s3:simulate-flow \
  --evento-id 2025 \
  --lote-id lote_tmj_2025_001 \
  --lote-upload-id lot-abc123def456 \
  --status-processamento failed \
  --tentativas-reprocessamento 1 \
  --reprocessamento-habilitado true \
  --motivo-reprocessamento "Falha de processamento detectada no lote" \
  --backend-mode ok
```

Modos de backend para diagnostico:
- `ok`: status valido e reprocessamento quando elegivel.
- `monitor-only`: resposta de status sem disparar reprocessamento.
- `incomplete-status`: resposta incompleta para testar validacao.
- `incomplete-reprocess`: resposta de reprocessamento incompleta.
- `invalid-next-action`: `proxima_acao` invalida para testar contrato.
- `raise-error`: falha de comunicacao simulada.

### 3) Executar checklist de runbook
```bash
python scripts/ingestao_inteligente_tools.py s3:runbook-check
```

Saida esperada:
- `[OK] s3:runbook-check`
- `input_status: valid`
- `flow_status: accepted` ou `ready` (dependendo da elegibilidade de reprocessamento)
- `output_status: valid`

### 4) Saida em JSON
```bash
python scripts/ingestao_inteligente_tools.py \
  --output-format json \
  s3:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s3:validate-input`.
2. Simular fluxo com `s3:simulate-flow --backend-mode ok`.
3. Simular erro (`incomplete-status`, `incomplete-reprocess` ou `raise-error`) para confirmar mensagens acionaveis.
4. Executar `s3:runbook-check`.
5. Confirmar presenca de `correlation_id`, `lote_id`, `lote_upload_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_LOTE_UPLOAD_ID`:
- Sintoma: identificador de upload fora do padrao esperado.
- Acao: usar id retornado pela Sprint 2 no formato `lot-...`.

`INVALID_STATUS_PROCESSAMENTO`:
- Sintoma: status fora do contrato da sprint.
- Acao: usar status aceitos definidos no contrato `s3.v1`.

`REPROCESS_ATTEMPTS_EXCEEDED`:
- Sintoma: tentativas acima do limite operacional.
- Acao: encaminhar para analise manual ou revisar politica de tentativas.

`INCOMPLETE_S3_STATUS_RESPONSE`:
- Sintoma: resposta do endpoint `/s3/status` sem campos obrigatorios.
- Acao: ajustar endpoint para respeitar contrato `s3.v1`.

`INCOMPLETE_S3_REPROCESS_RESPONSE`:
- Sintoma: resposta do endpoint `/s3/reprocessar` incompleta.
- Acao: ajustar endpoint para propagar todos os campos obrigatorios.

`INVALID_S3_NEXT_ACTION_RESPONSE`:
- Sintoma: `proxima_acao` inesperada.
- Acao: retornar uma acao prevista no fluxo da sprint.

`S3_MAIN_FLOW_FAILED` ou `INGESTAO_TOOL_UNEXPECTED_ERROR`:
- Sintoma: falha nao prevista no fluxo/ferramenta.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_ingestao_inteligente_s3.py tests/test_ingestao_inteligente_s3_observability.py
python scripts/ingestao_inteligente_tools.py s3:runbook-check
python scripts/ingestao_inteligente_tools.py s3:simulate-flow --backend-mode incomplete-status --evento-id 2025 --lote-id lote_tmj_2025_001 --lote-upload-id lot-abc123def456 --status-processamento processing
```

## Limites da Sprint 3
- Fluxo focado em monitoramento e orquestracao de reprocessamento por contrato.
- Nao executa processamento real do lote; integra com endpoints de controle/estado.
- Evolucoes de arquitetura e automacao de remediation fora do escopo ficam para tasks seguintes.
