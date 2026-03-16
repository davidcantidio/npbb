---
doc_id: "F1_SUPABASE_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
audit_gate: "not_ready"
---

# Epicos - SUPABASE / F1 - Schema no Supabase

## Objetivo da Fase

Garantir que o schema atual do projeto suba no Supabase via Alembic usando o
contrato de conexao ja previsto pelo backend, sem abrir escopo de dados,
frontend ou autenticacao.

## Gate de Saida da Fase

`alembic upgrade head` executa com `DIRECT_URL` no Supabase, o historico de
migrations permanece com um unico head e existe evidencia suficiente para
liberar a fase de migracao de dados.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Compatibilizar e validar migrations Alembic no Supabase | Alinhar a execucao de migrations e provar que o schema local sobe no Supabase | nenhuma | todo | [EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md](./EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- alinhar o fluxo de migrations ao uso de `DIRECT_URL` no Supabase
- validar que o historico Alembic atual sobe no ambiente alvo sem drift
- consolidar a evidencia tecnica minima para liberar a migracao de dados

### Fora
- exportacao e importacao de dados
- alteracoes no modelo de dados alem do historico Alembic existente
- integracao com Supabase Auth
- alteracoes no frontend

## Definition of Done da Fase
- [ ] `EPIC-F1-01` concluido com as issues filhas `done`
- [ ] `alembic upgrade head` validado contra o Supabase com evidencia tecnica
- [ ] a fase libera F2 sem dependencia do PostgreSQL local para aplicar schema
