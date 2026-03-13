---
doc_id: "F3_UX_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "not_ready"
---

# Epicos - UX / F3 - Validacao

## Objetivo da Fase

Garantir ausencia de regressao funcional nas 5 etapas do wizard e aderencia aos criterios de sucesso. Validacao em multiplos viewports e aprovacao interna pelo PM antes do deploy.

## Gate de Saida da Fase

- Zero regressao funcional nas 5 etapas
- PM aprova interface antes do deploy

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

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
| EPIC-F3-01 | Validacao e Regressao | Checklist de regressao por etapa e viewport; aprovacao PM | F2 | todo | [EPIC-F3-01-Validacao-Regressao.md](./EPIC-F3-01-Validacao-Regressao.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: F2 concluida

## Escopo desta Fase

### Dentro
- Checklist de regressao manual por etapa (Evento, Formulario, Gamificacao, Ativacoes, Questionario)
- Validacao em multiplos viewports (desktop, tablet, mobile)
- Validacao interna pelo PM de limpeza e harmonia visual

### Fora
- Correcoes de bugs (devem ser tratadas como issues em F2 ou follow-up)
- Novas funcionalidades

## Definition of Done da Fase
- [ ] Checklist de regressao executado
- [ ] Zero regressao funcional confirmada
- [ ] PM aprovou interface
