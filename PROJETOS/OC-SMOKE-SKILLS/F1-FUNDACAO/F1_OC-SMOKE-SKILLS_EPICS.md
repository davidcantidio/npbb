---
doc_id: "F1_OC-SMOKE-SKILLS_EPICS.md"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-23"
audit_gate: "not_ready"
---

# Epicos - OC-SMOKE-SKILLS / F1 - Fundacao do projeto

## Objetivo da Fase

Validar o projeto-canario do framework com intake, PRD, wrappers atualizados e uma issue bootstrap controlada.

## Gate de Saida da Fase

O canario prova que o framework atual consegue rotear, executar, revisar e auditar um backlog minimo sem drift documental.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- log_do_projeto: [PROJETOS/OC-SMOKE-SKILLS/AUDIT-LOG.md](PROJETOS/OC-SMOKE-SKILLS/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

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
| EPIC-F1-01 | Fundacao do projeto | Manter uma prova controlada de aderencia do framework. | Feature 1 | nenhuma | todo | [EPIC-F1-01 - Fundacao do projeto](./EPIC-F1-01-FUNDACAO-DO-PROJETO.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- intake, PRD e guia do canario alinhados
- wrappers locais alinhados ao framework atual
- bootstrap F1 com issue granularizada usada como prova controlada

### Fora
- backlog de produto
- implementacao fora do proprio framework OpenClaw
- deploy de runtime de produto

## Definition of Done da Fase
- [ ] intake, PRD e guia do canario estao coerentes
- [ ] wrappers de sessao estao completos e atuais
- [ ] fase F1, epico, issue e task continuam rastreaveis
- [ ] audit log aponta para a fase canario
- [ ] relatorio base de auditoria existe em `auditorias/`
