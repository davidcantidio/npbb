---
doc_id: "F2_SUPABASE_EPICS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
audit_gate: "pending"
---

# Epicos - SUPABASE / F2 - Migracao de Dados

## Objetivo da Fase

Substituir os dados atuais do Supabase pelos dados do PostgreSQL local com
backup previo, export reproduzivel, recarga controlada e validacao suficiente
para preservar a seguranca operacional da migracao.

## Gate de Saida da Fase

O backup do Supabase existe, o export do PostgreSQL local e reproduzivel, a
recarga de dados foi executada com ordem segura e a integridade pos-carga foi
validada com rollback operacionalmente viavel.

## Estado do Gate de Auditoria

- gate_atual: `pending`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [x] todos os epicos estao `done`
- [x] todas as issues filhas estao `done`
- [x] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Preparar backup e export do PostgreSQL local | Fechar o runbook de migracao e gerar os artefatos de seguranca e export | F1 concluida | done | [EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md](./EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md) |
| EPIC-F2-02 | Recarregar o Supabase com os dados locais | Executar a substituicao dos dados do Supabase e validar a integridade pos-carga | EPIC-F2-01 | done | [EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md](./EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende de F1 concluida, com schema do Supabase validado
- `EPIC-F2-02`: depende de `EPIC-F2-01` concluido e dos artefatos de backup/export disponiveis

## Escopo desta Fase

### Dentro
- formalizar a estrategia operacional de backup, export, import e rollback
- gerar backup do Supabase e export do PostgreSQL local
- executar a recarga de dados com ordem segura e validacao pos-carga

### Fora
- alterar schema alem do que ja foi validado em F1
- integrar Supabase Auth
- alterar frontend
- redefinir o modelo de dados do backend

## Definition of Done da Fase
- [x] `EPIC-F2-01` e `EPIC-F2-02` concluidos com issues filhas `done`
- [x] backup, export, recarga e validacao pos-carga executados conforme runbook
- [x] a fase libera F3 com o Supabase refletindo o estado atual dos dados locais
