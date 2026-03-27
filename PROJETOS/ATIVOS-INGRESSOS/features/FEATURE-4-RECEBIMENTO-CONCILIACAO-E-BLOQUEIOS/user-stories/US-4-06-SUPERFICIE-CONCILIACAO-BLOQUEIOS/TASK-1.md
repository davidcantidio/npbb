---
doc_id: "TASK-1.md"
user_story_id: "US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/app/AppRoutes.tsx"
  - "frontend/src/components/layout/AppLayout.tsx"
  - "frontend/src/pages/ativos/AtivosRecebimentoLayout.tsx"
  - "frontend/src/pages/ativos/AtivosConciliacaoPage.tsx"
  - "frontend/src/pages/ativos/AtivosBloqueiosRecebimentoPage.tsx"
tdd_aplicavel: false
---

# TASK-1 - Rotas, submenu Ativos e shell operacional de recebimento

## objetivo

Expor rotas autenticadas sob o modulo Ativos para a superficie de recebimento (conciliacao e bloqueios), com layout partilhado (navegacao local, titulo, area para `Outlet`), entradas no drawer **Ativos** alinhadas a `AppLayout`, e placeholders minimos ate T2/T3 preencherem o conteudo.

## precondicoes

- Nenhuma task anterior nesta US.
- Leitura de `AppRoutes.tsx` e padrao `ProtectedRoute` + `AppLayout` existente.

## orquestracao

- `depends_on`: `[]`.
- `parallel_safe`: false.
- `write_scope`: rotas, submenu e ficheiros novos listados no frontmatter; nao alterar logica de negocio de `AtivosList.tsx` nesta task.

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/components/layout/AppLayout.tsx`
- `frontend/src/components/ProtectedRoute.tsx`
- `frontend/src/pages/AtivosList.tsx` *(referencia de UX / erros 403)*
- `frontend/src/services/auth.ts` *(tipo `LoginUser` / `tipo_usuario` para eventual condicao de menu)*

## passos_atomicos

1. Criar `frontend/src/pages/ativos/AtivosRecebimentoLayout.tsx` com `Outlet` do `react-router-dom`, cabecalho da area (titulo operacional) e navegacao local (tabs ou botoes) entre as duas vistas filhas.
2. Criar `AtivosConciliacaoPage.tsx` e `AtivosBloqueiosRecebimentoPage.tsx` com conteudo placeholder claro (ex.: titulo + texto a remover na T2/T3) e estados de loading/erro genericos reutilizando padroes MUI ja usados em `AtivosList.tsx`.
3. Em `AppRoutes.tsx`, registar rotas aninhadas, por exemplo `path="/ativos/recebimento"` com elemento `AtivosRecebimentoLayout` e filhos `conciliacao` e `bloqueios` (ajustar paths finais de forma consistente e documentar na T2/T3).
4. Em `AppLayout.tsx`, acrescentar entradas em `ATIVOS_SUBMENU` para **Conciliacao** e **Bloqueios por recebimento** (ou rotulos equivalentes) apontando para as novas rotas.
5. Garantir que apenas utilizadores autenticados acedem (rotas ja sob `ProtectedRoute`); se o projeto definir perfil operador via `tipo_usuario`, condicionar a visibilidade das novas entradas de menu a esse criterio **somente** se ja existir convencao identica noutras entradas Ativos — caso contrario, deixar visivel a qualquer sessao autenticada e confiar no 403 da API como em `AtivosList`.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Operador autenticado navega pelo menu Ativos para as novas rotas, ve layout coerente e placeholders; `/ativos` (lista existente) permanece inalterado em comportamento.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck` sem erros novos atribuiveis a esta alteracao.
- Verificacao manual: abrir cada rota nova, confirmar ausencia de regressao no drawer e na lista `/ativos`.

## stop_conditions

- Parar se for necessario alterar a arvore de rotas de forma a quebrar URLs publicas ou rotas de evento — escalar desenho de URL antes de prosseguir.
- Parar se `npm run typecheck` falhar por causas preexistentes nao relacionadas; registar e isolar apenas ficheiros desta task.
