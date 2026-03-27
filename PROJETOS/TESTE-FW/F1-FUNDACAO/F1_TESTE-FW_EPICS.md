---
doc_id: "F1_TESTE-FW_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# Epicos - TESTE-FW / F1 - Fundacao do projeto

## Objetivo da Fase

Consolidar o scaffold inicial do projeto com intake, PRD, wrappers de sessao e primeiro issue-first bootstrap.

## Gate de Saida da Fase

O projeto tem intake, PRD, wrappers locais preenchidos, fase F1, epico F1-01, issue granularizada com task e artefatos de auditoria prontos para uso.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/TESTE-FW/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- log_do_projeto: [PROJETOS/TESTE-FW/AUDIT-LOG.md](../AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F1-01 | Fundacao do projeto | Entregar o scaffold inicial e validar os artefatos de base. | Feature 1 | nenhuma | todo | [EPIC-F1-01 - Fundacao do projeto](./EPIC-F1-01-FUNDACAO-DO-PROJETO.md) |

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
- [ ] intake e PRD existem com frontmatter preenchido
- [ ] wrappers de sessao estao completos
- [ ] fase F1, epico, issue e task existem
- [ ] audit log aponta para o bootstrap inicial
- [ ] relatorio base de auditoria existe em `auditorias/`
