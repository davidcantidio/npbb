---
doc_id: "TASK-4.md"
user_story_id: "US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/e2e/ativos-categorias-config.smoke.spec.ts"
  - "frontend/e2e/support/"
tdd_aplicavel: false
---

# TASK-4 - Smoke E2E Playwright para UI de configuracao de categorias

## objetivo

Acrescentar **smoke E2E** (Playwright) que valide um **fluxo critico** da UI de
configuracao de categorias por evento entregue pela [US-3-03](../US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO/README.md),
reutilizando o padrao existente em `frontend/e2e/` (auth helpers, API context).

## precondicoes

- **TASK-2** (`T2`) em `done` (cobertura API/modos estabilizada).
- [US-3-03](../US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO/README.md) com UI
  navegavel e rotas estaveis.
- Se o projeto **nao** tiver rota/pagina de ativos configuravel em ambiente E2E
  (seed, base URL), tratar como **fora de escopo imediato** e cancelar a task
  com justificativa no `resultado_esperado` da execucao.

## orquestracao

- `depends_on`: `T2` (paralelo conceitual a T3, mas dependencia apenas de T2 para
  evitar conflito de ordem com a cadeia T1-T2-T3).
- `parallel_safe`: `false`.
- `write_scope`: um ficheiro spec sob `frontend/e2e/` e, se necessario,
  helpers minimos em `frontend/e2e/support/`.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) desta US
- `frontend/e2e/internal-architecture.api.smoke.spec.ts` *(referencia de estilo)*
- `frontend/e2e/support/auth-helpers.ts`
- `frontend/e2e/support/test-urls.ts`
- Rotas React da UI de ativos / configuracao *(descobrir em `frontend/src/` na execucao)*

## passos_atomicos

1. Confirmar URL de login, seed de utilizador e rota da tela de configuracao
   de categorias por evento.
2. Criar `frontend/e2e/ativos-categorias-config.smoke.spec.ts` com cenario
   minimo: autenticar, navegar ate a configuracao, acao de leitura ou alteracao
   nao destrutiva que prove que modos/categorias aparecem conforme contrato UI.
3. Rodar Playwright em modo headed/CI conforme script do `package.json` do
   frontend.
4. Se ambiente E2E nao suportar modulo ativos, documentar limitacao e marcar task
   `cancelled` com justificativa.

## comandos_permitidos

- `cd frontend && npx playwright test e2e/ativos-categorias-config.smoke.spec.ts`
- *(ajustar ao script canonico do repo, ex. `npm run test:e2e` se existir)*

## resultado_esperado

Spec E2E verde em CI local ou instrucao clara de cancelamento se o padrao E2E
atual nao cobrir ativos; reforco operacional do fluxo exposto pela UI apos
FEATURE-3.

## testes_ou_validacoes_obrigatorias

- Execucao bem-sucedida do ficheiro Playwright criado, ou registo escrito de
  cancelamento com razao objetiva.

## stop_conditions

- Parar e cancelar se nao existir forma suportada de subir API + frontend + DB
  para testes E2E de ativos.
- Parar se T2 nao estiver concluida.
