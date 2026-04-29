---
doc_id: "TASK-3.md"
user_story_id: "US-10-01-VALIDAR-INTEGRACAO-LOCAL-E-REMEDIAR-REGRESSOES"
task_id: "T3"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/main.tsx"
  - "frontend/src/hooks/useAgeAnalysis.ts"
  - "frontend/src/services/dashboard_age_analysis.ts"
  - "frontend/src/hooks/__tests__/useAgeAnalysis.test.tsx"
  - "frontend/src/services/__tests__/dashboard_age_analysis.test.ts"
  - "frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx"
tdd_aplicavel: false
---

# T3 - Validar frontend e smoke local full-stack

## objetivo

Provar que o cache compartilhado do frontend respeita escopo, filtros e dia de
referencia, e que a tela de analise etaria continua funcional na integracao
full-stack local.

## precondicoes

- `T1` concluida com API local respondendo
- ajustes de backend de `T2` conhecidos, quando existirem
- dependencias do frontend ja instaladas

## orquestracao

- `depends_on`: `T1`
- `parallel_safe`: `false`
- `write_scope`: frontend da trilha do cache etario

## arquivos_a_ler_ou_tocar

- `frontend/src/main.tsx`
- `frontend/src/hooks/useAgeAnalysis.ts`
- `frontend/src/services/dashboard_age_analysis.ts`
- `frontend/src/hooks/__tests__/useAgeAnalysis.test.tsx`
- `frontend/src/services/__tests__/dashboard_age_analysis.test.ts`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`

## passos_atomicos

1. rodar lint, typecheck, testes e build do frontend
2. confirmar por teste e leitura de codigo que a query key varia por escopo e
   por dia de referencia em `America/Sao_Paulo`
3. corrigir regressoes diretas de cache ou bootstrap, se aparecerem
4. executar smoke manual da rota `/dashboard/leads/analise-etaria`
5. validar refresh manual, reuse de cache e ausencia de vazamento entre escopos

## comandos_permitidos

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run test -- --run`
- `cd frontend && npm run build`
- `rg -n "QueryClientProvider|useAgeAnalysis|buildAgeAnalysisQueryKey|getAgeAnalysisReferenceDayKey" frontend/src`

## resultado_esperado

Frontend verde no recorte da trilha etaria, sem reaproveitamento indevido de
dados entre usuarios/agencias e com smoke local full-stack validado.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run test -- --run`
- `cd frontend && npm run build`
- smoke manual em `/dashboard/leads/analise-etaria`

## stop_conditions

- parar se a correcao exigir nova prop publica, nova rota ou mudanca de
  contrato da API
- parar se o problema for exclusivamente de ambiente local e registrar como
  `environment`
- parar se a falha vier de legados fora do diff e classificar como
  `legacy-known`
