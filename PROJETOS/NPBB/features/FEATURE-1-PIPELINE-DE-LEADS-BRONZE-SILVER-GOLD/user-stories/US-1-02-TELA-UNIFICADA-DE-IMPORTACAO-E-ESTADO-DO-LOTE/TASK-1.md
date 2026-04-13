---
doc_id: "TASK-1.md"
user_story_id: "US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE"
task_id: "T1"
version: "2.1"
status: "done"
owner: "PM"
last_updated: "2026-04-13"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/app/AppRoutes.tsx"
  - "frontend/src/pages/leads/ImportacaoPage.tsx"
  - "frontend/src/pages/leads/MapeamentoPage.tsx"
  - "frontend/src/pages/leads/PipelineStatusPage.tsx"
  - "frontend/src/pages/leads/LegacyLeadStepRedirect.tsx"
tdd_aplicavel: false
---

# T1 - Implementar shell canonico e redirects de compatibilidade

## objetivo

Unificar Bronze, mapeamento, pipeline e ETL em `/leads/importar`, preservando
retomada por `batch_id` + `step` e compatibilidade com as rotas legadas.

## precondicoes

- `US-1-01` encerrada com os contratos de lote, mapeamento e ETL ja disponiveis
- rotas atuais de importacao, mapeamento e pipeline identificadas no frontend
- servicos existentes reutilizaveis sem novo endpoint backend

## orquestracao

- `depends_on`: nenhuma
- `parallel_safe`: `false`
- `write_scope`: `frontend/src/app/AppRoutes.tsx`, `frontend/src/pages/leads/*.tsx`

## arquivos_a_ler_ou_tocar

- `PROJETOS/NPBB/PRD-NPBB.md`
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/services/leads_import.ts`

## passos_atomicos

1. definir `/leads/importar` como rota canonica do shell com `step` e `batch_id`
2. compor o ramo Bronze para upload, preview, mapeamento e pipeline no mesmo fluxo
3. compor o ramo ETL para preview, warnings e commit inline
4. adaptar `MapeamentoPage` e `PipelineStatusPage` para operarem dentro do shell ou de forma autonoma
5. manter `/leads/mapeamento` e `/leads/pipeline` como redirects finos para a rota canonica

## comandos_permitidos

- `rg -n "/leads/importar|/leads/mapeamento|/leads/pipeline" frontend/src`
- `npm run typecheck`
- `npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx PipelineStatusPage.test.tsx --run`

## resultado_esperado

Fluxo unificado em `/leads/importar`, com retomada controlada por query params e
compatibilidade para deep links legados.

## testes_ou_validacoes_obrigatorias

- `npm run typecheck`
- validar que `/leads/mapeamento` e `/leads/pipeline` redirecionam para o shell canonico
- validar que Bronze e ETL continuam usando apenas contratos ja existentes

## stop_conditions

- parar se a unificacao exigir novo contrato backend nao previsto na user story
- parar se os deep links legados deixarem de funcionar para operadores ja ativos
