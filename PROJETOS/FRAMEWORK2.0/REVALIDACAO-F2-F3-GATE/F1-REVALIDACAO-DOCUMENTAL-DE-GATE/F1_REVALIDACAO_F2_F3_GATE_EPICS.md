---
doc_id: "F1_REVALIDACAO_F2_F3_GATE_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-10"
audit_gate: "not_ready"
---

# Epicos - REVALIDACAO-F2-F3-GATE / F1 - REVALIDACAO DOCUMENTAL DE GATE

## Objetivo da Fase

Revalidar os manifestos de fase `F2_FRAMEWORK2_0_EPICS.md` e
`F3_FRAMEWORK2_0_EPICS.md` contra o template canonico de gate para confirmar se
o unico delta relevante continua sendo o split do checklist
`pending -> hold` / `pending -> approved`, sem reabrir escopo funcional e sem
simular auditoria formal.

## Gate de Saida da Fase

Existe evidencia rastreavel de aderencia ou no-op controlado para F2 e F3, com
qualquer correcao limitada ao checklist/gate, sem alteracao de `status`,
`audit_gate`, `gate_atual`, `ultima_auditoria`, backlog funcional ou
`AUDIT-LOG.md`.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

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

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Baseline de Aderencia F2/F3 vs Template Canonico | Produzir o delta objetivo por manifesto e delimitar o escopo permitido de ajuste. | intake e PRD derivados | todo | [EPIC-F1-01-BASELINE-DE-ADERENCIA-F2-F3-VS-TEMPLATE-CANONICO.md](./EPIC-F1-01-BASELINE-DE-ADERENCIA-F2-F3-VS-TEMPLATE-CANONICO.md) |
| EPIC-F1-02 | Correcao Documental Minima de Gate | Aplicar apenas o patch minimo de checklist/gate ou registrar no-op controlado por manifesto. | EPIC-F1-01 | todo | [EPIC-F1-02-CORRECAO-DOCUMENTAL-MINIMA-DE-GATE.md](./EPIC-F1-02-CORRECAO-DOCUMENTAL-MINIMA-DE-GATE.md) |
| EPIC-F1-03 | Evidencia e Encerramento Rastreavel | Consolidar o resultado final sem criar auditoria formal nem atualizar `AUDIT-LOG.md`. | EPIC-F1-02 | todo | [EPIC-F1-03-EVIDENCIA-E-ENCERRAMENTO-RASTREAVEL.md](./EPIC-F1-03-EVIDENCIA-E-ENCERRAMENTO-RASTREAVEL.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: depende do [Intake Derivado](../../INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md), do [PRD Derivado](../../PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md) e do [Template Canonico](../../../COMUM/GOV-ISSUE-FIRST.md)
- `EPIC-F1-02`: depende da baseline concluida em `EPIC-F1-01`
- `EPIC-F1-03`: depende do fechamento de `EPIC-F1-02`, incluindo casos de no-op controlado

## Escopo desta Fase

### Dentro

- comparar F2 e F3 com o template canonico de fase
- confirmar se o delta permanece limitado ao checklist/gate
- corrigir apenas o split `pending -> hold` / `pending -> approved` quando houver drift comprovado
- consolidar evidencia final sem gerar auditoria formal

### Fora

- alterar objetivo, dependencias, DoD, epicos ou issues de F2/F3
- mudar `audit_gate`, `gate_atual`, `ultima_auditoria` ou `status` das fases F2/F3
- criar `RELATORIO-AUDITORIA-F2-R01.md`, `RELATORIO-AUDITORIA-F3-R01.md` ou nova linha em `AUDIT-LOG.md`
- revisar backlog funcional, escopo ou prontidao operacional alem de checklist/gate

## Definition of Done da Fase

- [ ] F2 e F3 foram comparadas ao template canonico com classificacao explicita de `drift confirmado` ou `no-op controlado`
- [ ] qualquer ajuste aplicado permaneceu restrito a checklist/gate
- [ ] nenhuma alteracao ocorreu em `status`, `audit_gate`, `gate_atual`, `ultima_auditoria` ou backlog funcional de F2/F3
- [ ] o encerramento explica por que esta trilha nao gera auditoria formal nem atualiza `AUDIT-LOG.md`
