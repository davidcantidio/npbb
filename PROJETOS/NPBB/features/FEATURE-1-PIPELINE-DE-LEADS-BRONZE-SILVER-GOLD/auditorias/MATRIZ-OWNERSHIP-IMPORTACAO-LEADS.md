---
doc_id: "MATRIZ-OWNERSHIP-IMPORTACAO-LEADS"
version: "1.0"
status: "done"
owner: "Eng"
last_updated: "2026-04-15"
scope_ref: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
---

# Matriz de ownership da importacao de leads

## Objetivo

Mapear, por campo e por contexto, qual e a fonte de verdade esperada na
importacao de leads. O foco desta rodada e separar o que pertence ao **Evento**
do que pertence a **cada linha** do arquivo.

## Topologia observada

| Fluxo | Entrada | Ancora de contexto | Saida principal |
|---|---|---|---|
| Batch classico | `POST /leads/batches` + mapeamento Silver | `LeadBatch.evento_id` e `LeadSilver.evento_id` | CSV Gold + `Lead` + `LeadEvento` |
| Pipeline generico/multievento | `run_pipeline` sobre contrato `ALL_COLUMNS` | o proprio arquivo | CSV consolidado + relatorio DQ |
| ETL | `POST /leads/import/etl/preview` -> `commit` | `snapshot.evento_id` | `Lead` + `LeadEvento` |

## Matriz principal

| Campo | Fonte de verdade com `evento_id` fixo | Fonte de verdade no pipeline generico/multievento | Fonte de verdade no ETL | Camadas que leem | Camadas que validam / usam | Camadas que exibem | Observacao |
|---|---|---|---|---|---|---|---|
| `evento_id` | lote / Silver | n/a | `snapshot.evento_id` | `lead_mapping.py`, `preview_service.py`, `commit_service.py` | `commit_service.py` valida conflito de sessao | `ImportacaoPage.tsx` passa `fixedEventoId` | ancora correta ja existe nos dois fluxos |
| `evento` / `evento_nome` | deveria vir de `Evento.nome`; hoje o classico sobrescreve so na materializacao | arquivo / `source_adapter.py` | preview fixa `evento_nome` com `Evento.nome` | `materializar_silver_como_csv`, `_build_lead_payload`, `_normalize_payload` do ETL | dedupe e upsert ainda usam string de nome | `MapeamentoPage`, `LeadsListPage` | nome do evento ainda participa da identidade do lead |
| `tipo_evento` | deveria vir de `Evento.tipo_id -> TipoEvento.nome`; hoje ja e sobrescrito na materializacao | arquivo | n/a no contrato canonicamente reutilizado pelo ETL | `materializar_silver_como_csv`, `pipeline.py` | gate e taxonomia do pipeline classico | `MapeamentoPage` | ownership no classico ja aponta para Evento |
| `data_evento` | deveria vir de `Evento.data_inicio_realizada` ou `Evento.data_inicio_prevista`; hoje ainda vem de `dados_brutos` | arquivo | n/a no contrato ETL | `materializar_silver_como_csv`, `_normalize_row` | `pipeline.py` gera `DATA_EVENTO_INVALIDA` por linha | `MapeamentoPage`, `PipelineStatusPage` | achado P0 confirmado |
| `local` | ownership ambiguo; classico trata como localidade do evento / fallback de sessao, mas ainda le do arquivo | arquivo | linha do arquivo, quando existir | `_normalize_row`, `_build_lead_payload` | normalizacao de localidade no classico | `MapeamentoPage`, `PipelineStatusPage` | semantica misturada entre evento e lead |
| `cidade` | ownership ambiguo; classico normaliza como localidade e persiste no `Lead` | arquivo | campo do `LeadRow` | `_normalize_row`, `_build_lead_payload`, `LeadRow` | normalizacao de localidade so no classico | `MapeamentoPage`, `PipelineStatusPage`, `LeadsListPage` | no ETL e tratado como atributo do lead |
| `estado` | ownership ambiguo; classico normaliza como localidade e persiste no `Lead` | arquivo | campo do `LeadRow` | `_normalize_row`, `_build_lead_payload`, `LeadRow` | normalizacao de localidade so no classico | `MapeamentoPage`, `PipelineStatusPage`, `LeadsListPage` | mesma ambiguidade de `cidade` |
| `sessao` | linha do arquivo; hoje pode cair em fallback de `local` no classico | arquivo | linha do arquivo | `_build_lead_payload`, `LeadRow` | dedupe e upsert em ambos os fluxos | `MapeamentoPage` | deve permanecer field owned pela linha |
| chave de dedupe / identidade | hoje depende de `evento` ou `evento_nome` string | depende de string do evento no arquivo | depende de `evento_nome` string | `pipeline.py`, `etl_import/persistence.py`, `Lead` model | dedupe, upsert e unique constraint | nao aplicavel | risco estrutural de rename / nomes duplicados |

## Evidencias chave

- O mapeamento Silver grava `dados_brutos` e `evento_id`, sem enriquecer outros
  campos de evento:
  [backend/app/services/lead_mapping.py](../../../../../backend/app/services/lead_mapping.py)
  linhas `131-148`.
- A materializacao classica sobrescreve apenas `evento` e `tipo_evento`:
  [backend/app/services/lead_pipeline_service.py](../../../../../backend/app/services/lead_pipeline_service.py)
  linhas `62-90`.
- O Gold ainda valida `data_evento`, `cidade`, `estado` e `local` por linha:
  [lead_pipeline/pipeline.py](../../../../../lead_pipeline/pipeline.py)
  linhas `201-250`.
- O ETL preview ancora o contexto em `evento_id` e `evento_nome` do evento
  escolhido:
  [backend/app/modules/leads_publicidade/application/etl_import/preview_service.py](../../../../../backend/app/modules/leads_publicidade/application/etl_import/preview_service.py)
  linhas `93-124`.
- O commit do ETL confirma `snapshot.evento_id`, mas a persistencia ainda
  vincula o evento por nome:
  [backend/app/modules/leads_publicidade/application/etl_import/commit_service.py](../../../../../backend/app/modules/leads_publicidade/application/etl_import/commit_service.py)
  linhas `17-54`,
  [backend/app/modules/leads_publicidade/application/etl_import/persistence.py](../../../../../backend/app/modules/leads_publicidade/application/etl_import/persistence.py)
  linhas `53-124`.
- A UI de mapeamento continua oferecendo campos de evento mesmo quando o shell
  fixa `evento_id`:
  [frontend/src/pages/leads/ImportacaoPage.tsx](../../../../../frontend/src/pages/leads/ImportacaoPage.tsx)
  linhas `457-468`,
  [frontend/src/pages/leads/MapeamentoPage.tsx](../../../../../frontend/src/pages/leads/MapeamentoPage.tsx)
  linhas `42-77`.
- A UI de status continua renderizando o card `Datas de evento invalidas`
  incondicionalmente:
  [frontend/src/pages/leads/PipelineStatusPage.tsx](../../../../../frontend/src/pages/leads/PipelineStatusPage.tsx)
  linhas `201-217` e `296-303`.

## Conclusoes operacionais

- O fluxo classico ja carrega uma ancora correta (`LeadSilver.evento_id`), mas
  o contrato Gold ainda deixa passar campos de evento vindos do arquivo.
- O ETL ja nasce ancorado no evento correto, mas perde essa ancora na hora de
  criar o vinculo canonico porque volta para `evento_nome`.
- `local`, `cidade` e `estado` nao podem ser corrigidos por heuristica simples
  sem antes fechar qual semantica o produto quer preservar em cada fluxo.
