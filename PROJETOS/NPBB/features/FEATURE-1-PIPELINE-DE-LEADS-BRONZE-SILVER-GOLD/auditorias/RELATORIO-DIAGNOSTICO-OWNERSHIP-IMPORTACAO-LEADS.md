---
doc_id: "RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS"
version: "1.0"
status: "done"
owner: "Eng"
last_updated: "2026-04-15"
scope_ref: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
evidence_base_commit: "3f1db72cebb0ac96cae8f7ad6fcdb33ef72370c8"
worktree_state: "dirty-preexisting"
formal_gate_update: "none"
---

# Relatorio diagnostico de ownership da importacao de leads

## Resumo executivo

O codigo atual confirma dois P0 de ownership:

1. no fluxo classico, `data_evento` ainda e tratado como input por linha mesmo
   quando o lote ja esta ancorado em `evento_id`;
2. no fluxo ETL, o vinculo canonico do evento ainda depende de
   `resolve_unique_evento_by_name`, apesar de o preview e o commit ja estarem
   ancorados em `snapshot.evento_id`.

Tambem apareceram dois P1 relevantes: a UI ainda expone campos owned pelo
evento no mapeamento/status de lote com evento fixo, e `local` / `cidade` /
`estado` carregam uma ambiguidade estrutural entre localidade do evento e
atributos do lead.

> Este documento e um diagnostico tecnico. Nao reabre o gate formal da feature,
> porque a worktree local ja estava suja antes desta sessao.

## Escopo e evidencias auditadas

- matriz detalhada:
  [MATRIZ-OWNERSHIP-IMPORTACAO-LEADS](./MATRIZ-OWNERSHIP-IMPORTACAO-LEADS.md)
- feature:
  [FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD](../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
- documentacao funcional:
  [docs/leads_importacao.md](../../../../../docs/leads_importacao.md)
- trilha classica:
  [backend/app/services/lead_mapping.py](../../../../../backend/app/services/lead_mapping.py),
  [backend/app/services/lead_pipeline_service.py](../../../../../backend/app/services/lead_pipeline_service.py),
  [lead_pipeline/pipeline.py](../../../../../lead_pipeline/pipeline.py)
- trilha ETL:
  [backend/app/modules/leads_publicidade/application/etl_import/preview_service.py](../../../../../backend/app/modules/leads_publicidade/application/etl_import/preview_service.py),
  [backend/app/modules/leads_publicidade/application/etl_import/commit_service.py](../../../../../backend/app/modules/leads_publicidade/application/etl_import/commit_service.py),
  [backend/app/modules/leads_publicidade/application/etl_import/persistence.py](../../../../../backend/app/modules/leads_publicidade/application/etl_import/persistence.py)
- frontend:
  [frontend/src/pages/leads/ImportacaoPage.tsx](../../../../../frontend/src/pages/leads/ImportacaoPage.tsx),
  [frontend/src/pages/leads/MapeamentoPage.tsx](../../../../../frontend/src/pages/leads/MapeamentoPage.tsx),
  [frontend/src/pages/leads/PipelineStatusPage.tsx](../../../../../frontend/src/pages/leads/PipelineStatusPage.tsx)

## Pontos positivos confirmados

- O batch classico ja propaga `evento_id` para `LeadSilver`, entao a ancora
  canonica do evento existe antes da fase Gold.
- O ETL preview ja fixa `evento_id` e `evento_nome` do evento selecionado.
- O commit do ETL ja rejeita `session_token` usado com `evento_id` divergente.

## Problemas priorizados

| Prioridade | Problema | Evidencia | Fluxo | Impacto | Correcao sugerida | Teste necessario |
|---|---|---|---|---|---|---|
| P0 | `data_evento` continua vindo de `dados_brutos` e gera `DATA_EVENTO_INVALIDA` por linha em lote com evento fixo | `lead_mapping.py` `131-148` persiste `dados_brutos`; `lead_pipeline_service.py` `62-90` sobrescreve so `evento` e `tipo_evento`; `pipeline.py` `216-245` valida `data_evento` da linha; `PipelineStatusPage.tsx` `201-217` e `296-303` mostra o card | batch classico | descarte indevido de linhas, DQ enganoso e culpa incorreta da planilha | derivar `data_evento` de `Evento` na materializacao; se faltar data no cadastro, emitir um unico problema de dados mestres ou configuracao do lote; tornar a UI contextual | pytest cobrindo materializacao + pipeline; vitest cobrindo ausencia do card em contexto derivado |
| P0 | ETL cria o vinculo canonico do evento por nome, nao por `snapshot.evento_id` | `preview_service.py` `93-124` ancora o snapshot; `commit_service.py` `17-54` valida conflito por `evento_id`; `etl_import/persistence.py` `105-124` volta para `resolve_unique_evento_by_name` | ETL | risco de vinculo ausente ou incorreto quando houver nome duplicado ou rename | passar `snapshot.evento_id` para a persistencia e usar `ensure_lead_event` diretamente por id; remover a dependencia de nome na trilha ETL | pytest com eventos homonimos e rename apos preview |
| P1 | A UI de mapeamento continua oferecendo campos owned pelo evento em lote com `fixedEventoId` | `ImportacaoPage.tsx` `457-468` injeta `fixedEventoId`; `MapeamentoPage.tsx` `42-77` continua listando `evento`, `tipo_evento`, `local`, `data_evento`, `cidade`, `estado` | batch classico / UI | induz o operador a mapear colunas que nao deveriam ser input do arquivo | ocultar, bloquear ou relabelar campos derived quando `fixedEventoId` existir | vitest garantindo que lote com evento fixo nao ofereca mapeamento ativo para campos derived |
| P1 | A UI de status continua atribuindo erro por linha a `data_evento` sem olhar o contexto do lote | `PipelineStatusPage.tsx` `201-217` indexa linhas por `DATA_EVENTO_INVALIDA`; `296-303` mostra o card sempre | batch classico / UI | amplifica um erro arquitetural como se fosse erro do operador | tornar metricas e cards context-aware; para campo derivado, esconder ou relabelar como problema de cadastro do evento | vitest cobrindo renderizacao contextual do card |
| P1 | `local`, `cidade` e `estado` estao semanticamente sobrecarregados entre localidade do evento e atributos do lead | `pipeline.py` `221-250` normaliza localidade; `lead_pipeline_service.py` `309-325` persiste `sessao` a partir de `local` e grava `cidade` / `estado` no lead; `LeadRow` `29-42` trata `cidade` e `estado` como campos do lead; `LeadsListPage.tsx` `271-274` exibe `cidade/estado` como local do lead | classico + ETL | risco de contaminar perfil do lead com localidade do evento e gerar validacoes contraditorias entre fluxos | fechar contrato: separar campos de evento de campos do lead, ou explicitar ownership por contexto antes de qualquer remediacao automatica | testes distinguindo cidade/estado do lead vs localidade do evento |
| P2 | Deduplicacao e identidade ainda dependem de strings de evento | `pipeline.py` `673-690` dedupe por `cpf + evento`; `etl_import/persistence.py` `53-85` usa `evento_nome`; `lead_public_models.py` `37-73` mantem unique constraint por `email + cpf + evento_nome + sessao` | classico + ETL | rename ou homonimos podem fragmentar identidade e dedupe | tratar como follow-up estrutural; avaliar migracao para chave canonica baseada em `evento_id` em novo intake, se o impacto for transversal | testes de rename / alias / homonimos; possivel migracao de schema |

## Lacunas de teste

| Area | Cobertura existente | Lacuna confirmada |
|---|---|---|
| materializacao Silver -> CSV | `backend/tests/test_lead_gold_pipeline.py` ja cobre override de `evento` e `tipo_evento` | nao existe teste equivalente para `data_evento` derivado de `Evento` |
| pipeline Gold em lote com evento fixo | `test_lead_gold_pipeline.py` so verifica `data_evento_invalid == 0` no caso feliz | nao existe caso com valor espurio em `data_evento` no arquivo e evento valido no cadastro |
| ETL preview / commit | `test_leads_import_etl_endpoint.py` cobre preview, commit, strict e conflito de `session_token` | nao existe caso com nomes de evento duplicados ou rename entre preview e commit |
| shell / mapeamento com evento fixo | `MapeamentoPage.test.tsx` ja cobre `fixedEventoId` basico | nao existe teste para esconder ou bloquear campos owned pelo evento |
| status page | `PipelineStatusPage.test.tsx` cobre renderizacao de metricas e progresso | nao existe teste para suprimir ou relabelar `data_evento_invalid` em contexto de campo derivado |

## Recomendacao de remediacao

### Same-feature, prioridade imediata

1. Corrigir `data_evento` no fluxo classico.
2. Corrigir o vinculo canonico do evento no ETL por `snapshot.evento_id`.
3. Ajustar a UI para refletir ownership por contexto.

### Avaliacao estrutural posterior

1. Fechar contrato de `local` / `cidade` / `estado`.
2. Decidir se a identidade do lead deve migrar de `evento_nome` para
   `evento_id`.

## Proximo passo recomendado

Abrir a remediacao em TDD com a seguinte ordem:

1. backend classico: `data_evento` derivado;
2. backend ETL: vinculo canonico por id;
3. frontend: mapeamento e status contextuais;
4. revisar se `local` / `cidade` / `estado` cabem na mesma US ou exigem um
   intake de remediacao estrutural.
