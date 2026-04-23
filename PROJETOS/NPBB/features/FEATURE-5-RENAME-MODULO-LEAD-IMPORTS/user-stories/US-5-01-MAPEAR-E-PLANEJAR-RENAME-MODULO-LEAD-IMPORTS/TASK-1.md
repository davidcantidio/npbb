---
doc_id: "TASK-1.md"
user_story_id: "US-5-01-MAPEAR-E-PLANEJAR-RENAME-MODULO-LEAD-IMPORTS"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-23"
depends_on: []
parallel_safe: false
write_scope:
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-RENAME-MODULO-LEAD-IMPORTS.md"
  - "PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md"
  - "PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/**"
tdd_aplicavel: false
---

# T1 - Registrar mapa tecnico e estrategia de rename

## objetivo

Criar governanca e mapa tecnico para o rename futuro de
`app.modules.leads_publicidade` para `app.modules.lead_imports`, sem executar
rename fisico nem alterar imports de codigo.

## passos_atomicos

1. confirmar consumidores com `rg`
2. confirmar estrutura atual do pacote com `Get-ChildItem`
3. criar intake, PRD, feature, user story e task da FEATURE-5
4. registrar nome alvo `app.modules.lead_imports`
5. registrar estrategia de compatibilidade por alias/reexport temporario
6. atualizar `plano_organizacao_import.md`

## comandos_permitidos

- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`

## stop_conditions

- parar se a rodada exigir alteracao em imports Python, scripts, rotas, schemas,
  frontend, dashboard, `lead_pipeline/` ou `core/leads_etl/`
- parar se houver necessidade de executar o rename fisico nesta task

## resultado

- 2026-04-23: governanca da `FEATURE-5-RENAME-MODULO-LEAD-IMPORTS` criada.
- 2026-04-23: nome alvo registrado como `app.modules.lead_imports`.
- 2026-04-23: estrategia futura registrada: criar pacote real
  `backend/app/modules/lead_imports`, manter `leads_publicidade` como
  alias/reexport temporario, migrar consumidores incrementalmente e remover o
  alias apenas apos busca sem consumidores.
- `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
  executado antes/depois para mapear consumidores.
- `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
  executado para confirmar estrutura atual do pacote.
- Nenhum arquivo Python, script, rota, schema, frontend, dashboard,
  `lead_pipeline/` ou `core/leads_etl/` foi alterado nesta task.
