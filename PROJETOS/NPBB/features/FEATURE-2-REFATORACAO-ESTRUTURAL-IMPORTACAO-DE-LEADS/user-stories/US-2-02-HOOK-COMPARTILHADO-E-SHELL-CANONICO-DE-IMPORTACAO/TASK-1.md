---
doc_id: "TASK-1.md"
user_story_id: "US-2-02-HOOK-COMPARTILHADO-E-SHELL-CANONICO-DE-IMPORTACAO"
task_id: "T1"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/hooks/useReferenciaEventos.ts"
  - "frontend/src/pages/leads/LeadsListPage.tsx"
  - "frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx"
  - "frontend/src/pages/__tests__/LeadsListPage.test.tsx"
tdd_aplicavel: false
---

# T1 - Centralizar o hook compartilhado de referencia de eventos

## objetivo

Mover `useReferenciaEventos` para `frontend/src/hooks` e fazer com que dashboard
e lista de leads consumam a mesma interface interna.

## passos_atomicos

1. criar o novo hook compartilhado
2. apontar `LeadsListPage` e `LeadsAgeAnalysisPage` para o novo caminho
3. ajustar testes afetados para mockarem o novo modulo

## comandos_permitidos

- `rg -n "useReferenciaEventos" frontend/src`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o move exigir mudar comportamento da API de eventos
