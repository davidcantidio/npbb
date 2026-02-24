# Ingestao Inteligente S4 - Runbook Operacional

## Objetivo
Documentar o fluxo operacional da Sprint 4 da Interface de Ingestao Inteligente (UX final + mensagens acionaveis + acessibilidade), com foco em:
- contrato estavel de entrada e saida;
- rastreabilidade por `correlation_id`, `lote_id` e `lote_upload_id`;
- diagnostico com logs e erros acionaveis;
- validacao local rapida por ferramenta CLI.

Arquivos principais da sprint:
- `frontend/src/features/ingestao_inteligente/s4_scaffold.py`
- `frontend/src/features/ingestao_inteligente/s4_core.py`
- `frontend/src/features/ingestao_inteligente/s4_observability.py`
- `frontend/src/features/ingestao_inteligente/s4_validation.py`
- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/services/interface-de-ingest-o-inteligente-frontend-_telemetry.py`
- `scripts/ingestao_inteligente_tools.py`

## Quando usar
- Validar rapidamente contrato S4 antes de integrar frontend/backend.
- Simular fluxo principal de UX final com backend controlado.
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

## Contrato S4 (resumo)
Entrada (frontend/backend):
- `evento_id` (int > 0)
- `lote_id` (3..80, regex `[a-zA-Z0-9._-]`)
- `lote_upload_id` (regex `lot-[a-z0-9]{6,64}`)
- `status_processamento` (`queued`, `processing`, `completed`, `failed`, `partial_success`, `cancelled`)
- `proxima_acao` (`monitorar_status_lote`, `avaliar_reprocessamento_lote`, `consultar_resultado_final_lote`)
- `leitor_tela_ativo` (bool)
- `alto_contraste_ativo` (bool)
- `reduzir_movimento` (bool)
- `correlation_id` (opcional)

Saida UX final (`POST /internal/ingestao-inteligente/s4/ux`):
- `contrato_versao`
- `correlation_id`
- `status` (`ready` ou `ok`)
- `evento_id`
- `lote_id`
- `lote_upload_id`
- `status_processamento`
- `proxima_acao`
- `mensagem_acionavel`
- `acessibilidade`
- `experiencia_usuario`
- `pontos_integracao`
- `observabilidade`

## Observabilidade e logs
Frontend:
- logger de validacao/contratos: `npbb.ingestao_inteligente.s4`
- ids de observabilidade: `observability_event_id` (`obs-*`)
- ids do core flow: `s4evt-*`

Backend:
- logger: `app.telemetry`
- ids: `telemetry_event_id` (`tel-*`)

Campos minimos para rastreio:
- `correlation_id`
- `evento_id`
- `lote_id`
- `lote_upload_id`
- `codigo_mensagem` (quando disponivel)
- `error_code` (em falhas)
- `action` (orientacao de correcao)

## Ferramenta operacional
Arquivo:
- `scripts/ingestao_inteligente_tools.py`

### 1) Validar contrato de entrada
```bash
python scripts/ingestao_inteligente_tools.py s4:validate-input \
  --evento-id 2025 \
  --lote-id lote_tmj_2025_001 \
  --lote-upload-id lot-abc123def456 \
  --status-processamento processing \
  --proxima-acao monitorar_status_lote \
  --leitor-tela-ativo true \
  --alto-contraste-ativo false \
  --reduzir-movimento true
```

Saida esperada:
- `[OK] s4:validate-input`
- status `valid`

### 2) Simular fluxo principal
```bash
python scripts/ingestao_inteligente_tools.py s4:simulate-flow \
  --evento-id 2025 \
  --lote-id lote_tmj_2025_001 \
  --lote-upload-id lot-abc123def456 \
  --status-processamento processing \
  --proxima-acao monitorar_status_lote \
  --leitor-tela-ativo true \
  --alto-contraste-ativo false \
  --reduzir-movimento true \
  --backend-mode ok
```

Modos de backend para diagnostico:
- `ok`: retorna contrato valido da UX final.
- `incomplete`: resposta incompleta para testar validacao de saida.
- `invalid-status`: status inesperado no bloco UX.
- `invalid-next-action`: `proxima_acao` inesperada para testar contrato.
- `invalid-ux-priority`: prioridade de UX fora do contrato.
- `raise-error`: falha de comunicacao simulada.

### 3) Executar checklist de runbook
```bash
python scripts/ingestao_inteligente_tools.py s4:runbook-check
```

Saida esperada:
- `[OK] s4:runbook-check`
- `input_status: valid`
- `flow_status: ok` ou `ready`
- `output_status: valid`

### 4) Saida em JSON
```bash
python scripts/ingestao_inteligente_tools.py \
  --output-format json \
  s4:runbook-check
```

## Checklist operacional da sprint
1. Validar entrada com `s4:validate-input`.
2. Simular fluxo com `s4:simulate-flow --backend-mode ok`.
3. Simular erro (`incomplete`, `invalid-next-action`, `invalid-ux-priority` ou `raise-error`) para confirmar mensagens acionaveis.
4. Executar `s4:runbook-check`.
5. Confirmar presenca de `correlation_id`, `lote_id`, `lote_upload_id` e IDs de observabilidade/telemetria.

## Troubleshooting
`INVALID_PROXIMA_ACAO`:
- Sintoma: acao nao suportada para UX final.
- Acao: usar uma acao prevista no contrato da Sprint 4.

`INVALID_STATUS_FOR_REPROCESS_ACTION`:
- Sintoma: reprocessamento solicitado com status nao reprocessavel.
- Acao: alinhar `status_processamento` com a acao escolhida.

`INCOMPLETE_S4_UX_RESPONSE`:
- Sintoma: resposta do endpoint `/s4/ux` sem campos obrigatorios.
- Acao: ajustar endpoint para respeitar contrato `s4.v1`.

`INVALID_S4_UX_STATUS`:
- Sintoma: status final diferente de `ready` ou `ok`.
- Acao: retornar status previsto pelo contrato.

`INVALID_S4_MESSAGE_SEVERITY`:
- Sintoma: severidade de mensagem fora de `info`, `warning`, `success`, `error`.
- Acao: ajustar severidade no payload da UX.

`INVALID_S4_UX_PRIORITY`:
- Sintoma: prioridade de UX fora de `high`, `medium`, `low`.
- Acao: corrigir `prioridade_exibicao` no bloco `experiencia_usuario`.

`S4_MAIN_FLOW_FAILED` ou `INGESTAO_TOOL_UNEXPECTED_ERROR`:
- Sintoma: falha nao prevista no fluxo/ferramenta.
- Acao: reexecutar com `--log-level DEBUG` e investigar logs por `correlation_id`.

## Validacao tecnica local
Comandos recomendados:
```bash
pytest -q tests/test_ingestao_inteligente_s4.py tests/test_ingestao_inteligente_s4_observability.py
python scripts/ingestao_inteligente_tools.py s4:runbook-check
python scripts/ingestao_inteligente_tools.py s4:simulate-flow --backend-mode incomplete --evento-id 2025 --lote-id lote_tmj_2025_001 --lote-upload-id lot-abc123def456 --status-processamento processing --proxima-acao monitorar_status_lote --leitor-tela-ativo true --alto-contraste-ativo false --reduzir-movimento true
```

## Limites da Sprint 4
- Fluxo focado em contrato final de UX, mensagens acionaveis e acessibilidade.
- Nao substitui governanca de conteudo nem politicas de comunicacao de negocio.
- Evolucoes de arquitetura fora do escopo ficam para tasks seguintes.
