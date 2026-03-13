---
doc_id: "F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "pending"
---

# Epicos - REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA / F1 - BASELINE E REAUDITORIA DO HOLD

## Objetivo da Fase

Consolidar um sibling de remediacao baseado no estado atual do repositorio para
demonstrar, com rastreabilidade objetiva, o que dos achados do hold da F1 ja
foi absorvido pelo codigo, o que permanece como risco residual e quais
evidencias uma nova auditoria independente deve receber.

## Gate de Saida da Fase

Existe baseline objetiva do estado atual, evidencia executavel para contrato,
paridade, metadata e thresholds da F1, e handoff claro para reauditoria
independente, sem alterar o gate da F1 original, sem simular auditoria formal e
sem ampliar o escopo para refactors novos fora do sibling aprovado.

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

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Baseline do Estado Atual | Classificar os achados originais do hold contra o estado real do repositorio. | intake, PRD, auditoria F1 | done | [EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md](./EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md) |
| EPIC-F1-02 | Evidencia Objetiva para Reauditoria | Transformar a aderencia atual em prova executavel e rastreavel. | EPIC-F1-01 | done | [EPIC-F1-02-EVIDENCIA-OBJETIVA-PARA-REAUDITORIA.md](./EPIC-F1-02-EVIDENCIA-OBJETIVA-PARA-REAUDITORIA.md) |
| EPIC-F1-03 | Handoff e Fechamento do Sibling | Preparar o pacote final de reauditoria sem tocar a F1 original. | EPIC-F1-02 | done | [EPIC-F1-03-HANDOFF-E-FECHAMENTO-DO-SIBLING.md](./EPIC-F1-03-HANDOFF-E-FECHAMENTO-DO-SIBLING.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: depende do [Intake Derivado](../../INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md), do [PRD Derivado](../../PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md), do [Audit Log](../../AUDIT-LOG.md) e da [Auditoria de Origem](../../auditoria_fluxo_ativacao.md)
- `EPIC-F1-02`: depende da baseline objetiva concluida em `EPIC-F1-01`
- `EPIC-F1-03`: depende das evidencias consolidadas em `EPIC-F1-02`

## Escopo desta Fase

### Dentro
- classificar os achados `F1-NAO01` a `F1-NAO08` contra o estado atual do repo
- consolidar evidencia executavel para contrato publico, wrapper legado, metadata e thresholds
- registrar `backend/app/routers/leads.py` como risco residual fora do sibling
- preparar handoff e checklist para reauditoria independente da F1 original

### Fora
- alterar o gate `hold` da F1 original
- reabrir implementacao funcional do fluxo landing/submit que ja esteja aderente
- absorver o refactor de `backend/app/routers/leads.py` neste sibling
- resolver LGPD de CPF em repouso
- atualizar `AUDIT-LOG.md` ou criar novo relatorio formal de auditoria

## Definition of Done da Fase

- [x] existe baseline objetiva dos achados originais vs estado atual do repositorio
- [x] as evidencias backend, frontend e metadata estao consolidadas com comandos reproduziveis
- [x] `models.py` e `ativacao.py` estao classificados contra `SPEC-ANTI-MONOLITO.md`
- [x] `backend/app/routers/leads.py` foi explicitado como risco fora do sibling
- [x] existe handoff claro para reauditoria independente sem tocar o gate da F1 original
