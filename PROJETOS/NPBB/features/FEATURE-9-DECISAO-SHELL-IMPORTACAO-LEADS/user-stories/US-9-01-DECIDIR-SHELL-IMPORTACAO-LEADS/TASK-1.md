---
doc_id: "TASK-1.md"
user_story_id: "US-9-01-DECIDIR-SHELL-IMPORTACAO-LEADS"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-23"
depends_on: []
parallel_safe: false
write_scope:
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md"
  - "PROJETOS/NPBB/PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md"
  - "PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/**"
tdd_aplicavel: false
---

# T1 - Registrar decisao do shell de importacao

## objetivo

Criar uma rodada documental para decidir a fronteira atual de
`/leads/importar`, mantendo comportamento funcional congelado.

## passos_atomicos

1. confirmar estado inicial do worktree e ultimo commit
2. executar busca de fronteira do shell de importacao
3. confirmar ausencia de consumidores ativos de `app.modules.leads_publicidade`
4. criar intake, PRD, feature, user story e task da `FEATURE-9`
5. atualizar `plano_organizacao_import.md`
6. registrar que nenhuma suite funcional foi exigida por ser rodada documental

## comandos_permitidos

- `git status --short`
- `git log -1 --oneline`
- `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests`

## stop_conditions

- parar se a rodada exigir mover `ImportacaoPage.tsx`
- parar se a rodada exigir alterar `frontend/src/pages/leads/importacao/**`
- parar se a rodada exigir alterar `MapeamentoPage`, `BatchMapeamentoPage` ou
  `PipelineStatusPage`
- parar se houver necessidade de alterar contratos HTTP, schemas, backend,
  ETL, `lead_pipeline/` ou `core/leads_etl/`
- parar se houver necessidade de tocar nas mudancas locais de dashboard fora
  do escopo

## resultado

- 2026-04-23: `git status --short` confirmou mudancas locais preexistentes em
  `frontend/src/components/dashboard/EventsAgeTable.tsx` e teste associado,
  preservadas fora desta rodada.
- 2026-04-23: `git log -1 --oneline` retornou
  `cb218ea docs: add lead import organization handoff 7`.
- 2026-04-23: busca de fronteira confirmou que `/leads/importar` lazy-loada
  `../pages/leads/ImportacaoPage` e que testes de importacao, mapeamento e
  pipeline ainda importam de `frontend/src/pages/leads`.
- 2026-04-23: busca backend por `app.modules.leads_publicidade` nao retornou
  consumidores ativos em `backend/app`, `backend/scripts` ou `backend/tests`.
- 2026-04-23: governanca documental da `FEATURE-9` criada e plano atualizado.
- 2026-04-23: nenhuma suite funcional foi exigida porque o diff desta rodada e
  documental.
