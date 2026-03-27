---
doc_id: "F1_OC-MISSION-CONTROL_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
audit_gate: "approved"
---

# Epicos - OC-MISSION-CONTROL / F1 - Fundacao do projeto

## Objetivo da Fase

Consolidar o scaffold inicial do projeto com intake, PRD, wrappers de sessao e primeiro issue-first bootstrap.

## Gate de Saida da Fase

O projeto tem intake, PRD, wrappers locais preenchidos, fase F1, epico F1-01, issue granularizada com task e artefatos de auditoria prontos para uso.

## Estado do Gate de Auditoria

- gate_atual: `approved`
- ultima_auditoria: `F1-R01`
- veredito_atual: `go`
- relatorio_mais_recente: `PROJETOS/OC-MISSION-CONTROL/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- log_do_projeto: [PROJETOS/OC-MISSION-CONTROL/AUDIT-LOG.md](PROJETOS/OC-MISSION-CONTROL/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

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
| EPIC-F1-01 | Fundacao do projeto | Entregar o scaffold inicial e validar os artefatos de base. | Feature 1 | nenhuma | done | [EPIC-F1-01 - Fundacao do projeto](./EPIC-F1-01-FUNDACAO-DO-PROJETO.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- intake e PRD prefillados
- wrappers locais
- bootstrap F1 com issue granularizada

### Fora
- features de negocio reais
- implementacao de codigo de produto
- deploy ou integracoes externas

## Definition of Done da Fase
- [x] intake e PRD existem com frontmatter preenchido
- [x] wrappers de sessao estao completos
- [x] fase F1, epico, issue e task existem
- [x] audit log aponta para o bootstrap inicial
- [x] relatorio base de auditoria existe em `auditorias/`
