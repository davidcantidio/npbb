---
doc_id: "TASK-2.md"
user_story_id: "US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE"
task_id: "T2"
version: "2.1"
status: "done"
owner: "PM"
last_updated: "2026-04-13"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/pages/__tests__/ImportacaoPage.test.tsx"
  - "frontend/src/pages/__tests__/LegacyLeadStepRedirect.test.tsx"
  - "frontend/src/pages/__tests__/MapeamentoPage.test.tsx"
  - "frontend/src/pages/__tests__/PipelineStatusPage.test.tsx"
tdd_aplicavel: false
---

# T2 - Cobrir o fluxo unificado com testes de rota e estados operacionais

## objetivo

Provar que o shell canonico, os redirects legados e os estados operacionais de
Bronze, mapeamento, pipeline e ETL permanecem estaveis apos a unificacao.

## precondicoes

- `T1` concluida
- paginas e redirects do shell canonico disponiveis no frontend
- suite Vitest configurada no projeto

## orquestracao

- `depends_on`: `T1`
- `parallel_safe`: `false`
- `write_scope`: `frontend/src/pages/__tests__/*.test.tsx`

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`
- `frontend/src/pages/__tests__/LegacyLeadStepRedirect.test.tsx`
- `frontend/src/pages/__tests__/MapeamentoPage.test.tsx`
- `frontend/src/pages/__tests__/PipelineStatusPage.test.tsx`
- `frontend/src/pages/leads/ImportacaoPage.tsx`

## passos_atomicos

1. reescrever a suite de `ImportacaoPage` para validar a rota canonica e a retomada por query params
2. adicionar cobertura dedicada para os redirects legados de mapeamento e pipeline
3. manter a cobertura das paginas filhas para carga minima, navegacao e status de pipeline
4. executar typecheck e a bateria focada de Vitest da trilha de leads
5. registrar os resultados no handoff da user story

## comandos_permitidos

- `npm run typecheck`
- `npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx PipelineStatusPage.test.tsx --run`

## resultado_esperado

Cobertura automatizada do shell unificado, dos redirects de compatibilidade e
dos estados operacionais mais sensiveis do fluxo de leads.

## testes_ou_validacoes_obrigatorias

- `npm run typecheck`
- `npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx PipelineStatusPage.test.tsx --run`

## stop_conditions

- parar se os testes precisarem mascarar um contrato de API inexistente no shell real
- parar se a cobertura nova remover a verificacao minima das paginas legadas ainda suportadas
