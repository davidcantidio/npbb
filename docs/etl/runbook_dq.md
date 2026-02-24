# Runbook DQ e Observabilidade
Objetivo
Manter um fluxo simples de triagem para saude de ingestao, cobertura por sessao e alertas acionaveis antes do fechamento.

## Quando usar
- Quando o `dq:run` retornar alertas ou falha de gate.
- Quando o endpoint interno de saude indicar `partial`, `failed` ou `gap`.
- Quando houver suspeita de omissao de show por dia no relatorio.

## Fontes de diagnostico
- CLI local:
  `python -m etl.validate.cli_dq dq:run --ingestion-id <ingestion_id> --out-json out/dq.json --out-md out/dq.md`
- API interna de saude por fonte:
  `GET /internal/health/sources`
- API interna de cobertura por sessao:
  `GET /internal/health/coverage`
- API interna de catalogo:
  `GET /internal/catalog/sources`
  `GET /internal/catalog/ingestions`

## Leitura rapida dos alertas
- `ALERT_PARTIAL_INGESTION`
  Interpretacao: a ultima execucao da fonte nao concluiu todos os dados esperados.
  Acao: revisar notas e log da ingestao, corrigir extractor, rerodar carga.
- `ALERT_DRIFT_UNRESOLVED_SESSION`
  Interpretacao: registros foram carregados sem `session_id`.
  Acao: revisar `session_resolver` e o mapeamento de campos de sessao na fonte.
- `ALERT_DRIFT_METRIC_MISSING`
  Interpretacao: metrica esperada nao foi encontrada com evidencia valida.
  Acao: revisar layout da fonte e regras de extracao para evitar drift.
- `ALERT_MISSING_REQUIRED_DATASET`
  Interpretacao: sessao sem dataset obrigatorio para o fechamento.
  Acao: solicitar fonte faltante e rerodar pipeline antes de gerar Word final.

## Fluxo de triagem recomendado
- Confirmar escopo afetado:
  Filtrar por `event_id` em `GET /internal/health/coverage`.
- Identificar impacto por sessao:
  Verificar `sessions` e `matrix` no payload de coverage.
- Priorizar sessao de show:
  Se `session_type=NOTURNO_SHOW` com `gap`, tratar como bloqueador de fechamento.
- Validar fonte e execucao:
  Cruzar `source_id` nos endpoints de health e catalogo para localizar a ingestao.
- Reexecutar com evidencia:
  Rodar `dq:run` para confirmar queda dos alertas apos correcoes.

## Criterio de saida da triagem
- Nenhum alerta critico pendente para sessao de show.
- Sem gaps de datasets obrigatorios para sessoes previstas no fechamento.
- Evidencia de reprocessamento registrada em ingestion recente e health atualizado.

## Escalonamento
- Se o problema for de layout de arquivo, abrir ajuste de extractor e mapping.
- Se o problema for ausencia de fonte oficial, registrar GAP formal no relatorio.
- Se houver divergencia entre fontes, marcar como INCONSISTENTE e anexar evidencia.
