---
doc_id: "F3_LP-PREVIEW_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "not_ready"
---

# Epicos - LP-PREVIEW / F3 - Validacao

## Objetivo da Fase

Garantir ausencia de regressao e aderencia aos criterios de sucesso do PRD. Validar preview em diferentes viewports e em ambos os contextos (leads e landing page).

## Gate de Saida da Fase

- Zero bugs reportados relacionados ao preview
- Checklist de regressao concluido
- Metricas de sucesso atendidas

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
| EPIC-F3-01 | Validacao e Regressao | Checklist manual, multi-viewport, zero bugs | F2 done | todo | [EPIC-F3-01-Validacao-Regressao.md](./EPIC-F3-01-Validacao-Regressao.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: depende de F2 (Implementacao) concluida com auditoria aprovada

## Escopo desta Fase

### Dentro
- Testes manuais em ambos os contextos (leads e landing page)
- Checklist de regressao de funcionalidade do preview
- Validacao em diferentes viewports (desktop, tablet, mobile)
- Documentacao de achados e metricas

### Fora
- Novas funcionalidades
- Alteracoes de codigo alem de correcoes de bugs

## Definition of Done da Fase
- [ ] Checklist de regressao executado
- [ ] Zero bugs reportados relacionados ao preview
- [ ] Metricas de sucesso do PRD validadas
- [ ] Auditoria F3 aprovada com veredito `go`
