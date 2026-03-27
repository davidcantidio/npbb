---
doc_id: "TASK-5.md"
user_story_id: "US-4-06-SUPERFICIE-CONCILIACAO-BLOQUEIOS"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/pages/__tests__/AtivosRecebimentoPages.test.tsx"
  - "frontend/src/services/__tests__/ativos_recebimento.test.ts"
tdd_aplicavel: false
---

# TASK-5 - Validacao de aceite, testes e evidencias

## objetivo

Fechar a US com validacao objetiva dos tres criterios Given/When/Then: automatizar o que for razoavel (testes de componente ou de servico com mocks HTTP) e registar checklist manual + comandos no handoff do `README.md` da US.

## precondicoes

- [T2](./TASK-2.md) e [T3](./TASK-3.md) concluidas (`done`).
- [T4](./TASK-4.md) concluida (`done`) **ou** `cancelled` com justificativa aceite pelo fluxo do projeto.

## orquestracao

- `depends_on`: `["T2", "T3"]`.
- `parallel_safe`: false.
- `write_scope`: apenas ficheiros de teste listados no frontmatter (padrao `pages/__tests__` e `services/__tests__` do repo).

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/ativos/AtivosConciliacaoPage.tsx`
- `frontend/src/pages/ativos/AtivosBloqueiosRecebimentoPage.tsx`
- `frontend/src/services/ativos_recebimento.ts`
- [README.md](./README.md) *(secao Handoff para Revisao Pos-User Story)*

## passos_atomicos

1. Escrever testes focados: por exemplo mock de `fetch` para `ativos_recebimento.ts` cobrindo sucesso e erro, ou teste de render das paginas com dados mockados (seguir padrao de `MemoryRouter` de outras suites do repo).
2. Executar a suite alvo e corrigir falhas introduzidas por esta US.
3. Executar checklist manual: (1) conciliacao vs backend; (2) bloqueio com motivo e refresh; (3) se T4 nao cancelada, registo de recebimento; se T4 cancelada, confirmar que nao ha UI enganosa prometendo registo.
4. Preencher no `README.md` da US: `validacoes_executadas`, `commits_execucao` (ou referencia), `arquivos_de_codigo_relevantes`, `evidencia` resumida.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run test -- --run`
- `cd frontend && npm run build` *(smoke opcional)*

## resultado_esperado

Definition of Done documental da US avancada: criterios verificados, testes passando, handoff preenchido.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run` incluindo ficheiros novos desta task.
- `cd frontend && npm run typecheck`.
- Checklist manual dos tres criterios arquivado no README (campos de handoff).

## stop_conditions

- Parar se a cobertura minima exigida pelo revisor nao for atingida — acrescentar casos antes de promover a US.
- Parar se testes falharem por flakiness nao relacionada; isolar com mocks deterministicos.
