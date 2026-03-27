---
doc_id: "TASK-1.md"
user_story_id: "US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/types/dashboard.ts"
  - "frontend/src/config/dashboardManifest.ts"
  - "frontend/src/components/dashboard/DashboardSidebar.tsx"
  - "frontend/src/components/dashboard/dashboardIconMap.tsx"
  - "frontend/src/config/__tests__/dashboardManifest.test.ts"
tdd_aplicavel: false
---

# T1 - Domínio Ativos no manifesto e sidebar

## objetivo

Introduzir o domínio **ativos** no modelo tipado do dashboard, uma entrada no manifesto com rota canónica acordada (ex.: `/dashboard/ativos`), título de secção na sidebar e ícone mapeado, de forma que a navegação **Dashboard > Ativos** apareça agrupada como as secções Leads/Eventos/Publicidade. Manter `enabled: true` no manifesto; o filtro RBAC (quem vê o link) fica na T3 — manifesto estático + filtro em runtime.

## precondicoes

- [README.md](README.md) da US lido; rota canónica alinhada entre manifesto e T2 (`AppRoutes`).
- Nenhuma alteração ao manifesto da feature nem ao PRD.

## orquestracao

- `depends_on`: `[]`
- `parallel_safe`: false
- `write_scope`: ficheiros listados no frontmatter; não tocar em `AppRoutes` nem em guards (T2/T3).

## arquivos_a_ler_ou_tocar

- [README.md](README.md)
- `frontend/src/types/dashboard.ts`
- `frontend/src/config/dashboardManifest.ts`
- `frontend/src/components/dashboard/DashboardSidebar.tsx`
- `frontend/src/components/dashboard/dashboardIconMap.tsx`
- `frontend/src/components/dashboard/DashboardSidebarItem.tsx` *(se necessário para ícone ou acessibilidade)*
- `frontend/src/config/__tests__/dashboardManifest.test.ts`

## passos_atomicos

1. Estender `DashboardDomain` com valor `ativos` e `DashboardIconKey` com chave nova (ex.: `ativos-operacional`).
2. Registar em `DASHBOARD_ICON_MAP` um ícone MUI coerente com “ativos” (ex.: inventário ou confirmação), importando o componente no `dashboardIconMap.tsx`.
3. Adicionar `DOMAIN_TITLES` para `ativos` em `DashboardSidebar.tsx` (rótulo de secção **Ativos** ou equivalente fechado na implementação).
4. Incluir entrada em `DASHBOARD_MANIFEST` com `id`, `route`, `domain: "ativos"`, `name` alinhado à US (“Ativos”), `description`, `enabled: true` (filtro na T3).
5. Atualizar `dashboardManifest.test.ts`: contagem de entradas, presença da nova rota e domínio, e invariantes já testados (shape, rotas únicas).

## comandos_permitidos

- `cd frontend && npm run test -- dashboardManifest.test.ts --run`
- `cd frontend && npm run test -- --run` *(se necessário para regressão local)*
- `cd frontend && npm run lint` *(opcional, ficheiros tocados)*

## resultado_esperado

Sidebar do dashboard lista secção **Ativos** com link para `/dashboard/ativos` (ou rota definida de forma idêntica na T2), tipos e testes do manifesto consistentes.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- dashboardManifest.test.ts --run` em verde.
- Verificação manual rápida: após T2, rota e href coincidem com `entry.route` do manifesto.

## stop_conditions

- Parar se a rota escolhida divergir da implementada na T2 — alinhar texto desta task ou `AppRoutes` antes de merge.
- Parar se for necessário novo domínio de produto não mencionado na US (ex.: renomear módulo) — escalar PM.
