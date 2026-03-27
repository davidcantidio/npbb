---
doc_id: "TASK-2.md"
user_story_id: "US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC"
task_id: "T2"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/app/AppRoutes.tsx"
  - "frontend/src/pages/dashboard/AtivosOperacionalPage.tsx"
tdd_aplicavel: false
---

# T2 - Rotas aninhadas e página shell do dashboard de ativos

## objetivo

Montar rota(s) filha(s) de `/dashboard` (já servidas por `DashboardLayout` + `Outlet`) que correspondam **exatamente** ao `route` definido no manifesto na T1, com página **shell** (placeholder, estados de carregamento leves se já existir padrão nas outras páginas do dashboard) **sem** widgets de dados agregados (escopo da US-8-03). Garantir que utilizador autorizado vê conteúdo dentro do mesmo layout estrutural que o dashboard de leads (sidebar + área principal).

## precondicoes

- T1 `done`: manifesto contém entrada de ativos com `route` final.
- Revisar `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx` ou `DashboardHome.tsx` como referência de estrutura visual mínima (Paper, Typography, espaçamento).

## orquestracao

- `depends_on`: `["T1"]`
- `parallel_safe`: false
- `write_scope`: apenas rotas e nova página shell listadas no frontmatter.

## arquivos_a_ler_ou_tocar

- [TASK-1.md](./TASK-1.md)
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/components/dashboard/DashboardLayout.tsx` *(leitura — não alterar salvo acordo com T3)*
- Novo: `frontend/src/pages/dashboard/AtivosOperacionalPage.tsx` (nome fixo sugerido; ajustar imports em `AppRoutes`)

## passos_atomicos

1. Criar `AtivosOperacionalPage.tsx` exportando componente default com layout MUI alinhado às páginas do dashboard (título, texto de placeholder indicando que os widgets virão na US-8-03, sem chamadas a API de agregados).
2. Em `AppRoutes.tsx`, lazy-import da página e registo de `Route` como filho de `<Route path="/dashboard" element={<DashboardLayout />}>` — espelhar padrão `leads`/`leads/analise-etaria` se usar redirect intermédio, ou rota única se a T1 fixou `/dashboard/ativos` simples.
3. Garantir que URL profunda não cai no catch-all `<Route path="*" element={<Navigate to="/dashboard" replace />} />` antes das rotas de ativos (ordem das `Route` relevante).
4. Smoke manual: autenticado, navegar pelo link da sidebar para a shell e confirmar ausência de erros de consola.

## comandos_permitidos

- `cd frontend && npm run build` *(valida lazy boundaries e tipos)*
- `cd frontend && npm run test -- DashboardModule.test --run` *(se existir impacto; ajustar caminho)*

## resultado_esperado

Rota dedicada do dashboard de ativos renderiza shell dentro do `Outlet` do `DashboardLayout`, com path idêntico ao manifesto.

## testes_ou_validacoes_obrigatorias

- `npm run build` do frontend sem erros.
- Navegação manual: `/dashboard` → link Ativos → shell visível.

## stop_conditions

- Parar se for necessário alterar `DashboardLayout` de forma acoplada ao RBAC — coordenar com T3 ou mover ajuste para T3.
- Parar se a rota exigir dados da US-8-01 para renderizar — fora de escopo; manter apenas placeholder.
