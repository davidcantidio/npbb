---
doc_id: "F3_SUPABASE_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
audit_gate: "not_ready"
---

# Epicos - SUPABASE / F3 - Validacao e Cutover

## Objetivo da Fase

Validar o backend em runtime contra o Supabase, confirmar os scripts criticos e
invariantes de teste, e consolidar a documentacao e a configuracao final para
que o banco unico do projeto passe a ser o Supabase.

## Gate de Saida da Fase

O backend sobe e responde usando o Supabase, os scripts criticos e o fallback de
testes permanecem coerentes, e a documentacao/configuracao deixam de tratar o
PostgreSQL local como requisito operacional padrao.

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
- [ ] existe `RELATORIO-AUDITORIA-F3-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F3-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Validar backend e scripts criticos contra Supabase | Confirmar runtime, scripts e invariantes minimos apos a migracao de dados | F2 concluida | todo | [EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md](./EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md) |
| EPIC-F3-02 | Consolidar configuracao final e remover dependencia do Postgres local | Atualizar setup, troubleshooting e deploy para Supabase como banco unico | EPIC-F3-01 | todo | [EPIC-F3-02-Consolidar-Configuracao-Final-e-Remover-Dependencia-do-Postgres-Local.md](./EPIC-F3-02-Consolidar-Configuracao-Final-e-Remover-Dependencia-do-Postgres-Local.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: depende de F2 concluida e Supabase ja recarregado com os dados locais
- `EPIC-F3-02`: depende de `EPIC-F3-01` para documentar o estado operacional validado

## Escopo desta Fase

### Dentro
- validar o backend contra o Supabase em ambiente de validacao
- confirmar scripts criticos e o fallback de testes com SQLite
- atualizar configuracao e documentacao para Supabase como banco unico

### Fora
- alterar o frontend
- integrar Supabase Auth
- mudar o modelo de dados
- criar fases adicionais de deploy fora do escopo do PRD

## Definition of Done da Fase
- [ ] `EPIC-F3-01` e `EPIC-F3-02` concluidos com issues filhas `done`
- [ ] backend validado contra o Supabase como banco de runtime
- [ ] documentacao e configuracao atualizadas para remover a dependencia operacional do PostgreSQL local
