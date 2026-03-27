---
doc_id: "F1_OC-HOST-OPS_EPICS.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
audit_gate: "approved"
---

# Epicos - OC-HOST-OPS / F1 - Fundacao do projeto

## Objetivo da Fase

Consolidar o scaffold base do projeto e liberar o backlog real de host-side para planning.

## Gate de Saida da Fase

O projeto tem intake, PRD real, wrappers locais atualizados, issue bootstrap reconciliada e auditoria de F1 aprovada.

## Estado do Gate de Auditoria

- gate_atual: `approved`
- ultima_auditoria: `F1-R01`
- veredito_atual: `go`
- relatorio_mais_recente: `PROJETOS/OC-HOST-OPS/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- log_do_projeto: [PROJETOS/OC-HOST-OPS/AUDIT-LOG.md](PROJETOS/OC-HOST-OPS/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [x] todos os epicos estao `done`
- [x] todas as issues filhas estao `done`
- [x] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [x] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [x] `AUDIT-LOG.md` foi atualizado
- [x] o veredito da auditoria e `go`
- [x] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F1-01 | Fundacao do projeto | Validar o scaffold base e liberar planning do backlog host-side real. | Feature 1 | nenhuma | done | [EPIC-F1-01 - Fundacao do projeto](./EPIC-F1-01-FUNDACAO-DO-PROJETO.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- intake existente mantido como fonte real
- PRD placeholder substituido por backlog host-side real
- wrappers locais reconciliados com o estado atual do projeto

### Fora
- execucao das fases operacionais reais do host-side
- backlog de Mission Control ou Trading

## Definition of Done da Fase
- [x] intake e PRD estao coerentes com o worktree atual
- [x] wrappers de sessao estao completos e atuais
- [x] fase F1, epico, issue e task foram reconciliados
- [x] audit log aponta para o bootstrap aprovado
- [x] relatorio de auditoria existe em `auditorias/`
