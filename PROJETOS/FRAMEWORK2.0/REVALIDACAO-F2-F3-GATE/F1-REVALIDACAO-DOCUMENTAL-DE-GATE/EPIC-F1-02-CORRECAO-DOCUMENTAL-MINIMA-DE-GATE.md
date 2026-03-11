---
doc_id: "EPIC-F1-02-CORRECAO-DOCUMENTAL-MINIMA-DE-GATE.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-10"
---

# EPIC-F1-02 - Correcao Documental Minima de Gate

## Objetivo

Aplicar apenas o patch minimo de checklist/gate em F2 e F3 quando a baseline
confirmar drift, ou registrar no-op controlado quando o manifesto ja estiver
aderente no momento da execucao.

## Resultado de Negocio Mensuravel

F2 e F3 ficam aderentes ao split canonico de gate sem alterar o restante dos
manifestos e sem reabrir escopo funcional das fases do projeto principal.

## Contexto Arquitetural

Este epic so pode tocar `F2_FRAMEWORK2_0_EPICS.md` e `F3_FRAMEWORK2_0_EPICS.md`
na faixa de checklist/gate permitida pela baseline. Quaisquer divergencias fora
desse envelope devem ser bloqueadas, nao absorvidas.

## Definition of Done do Epico

- [x] F2 foi tratada como patch minimo ou no-op controlado
- [x] F3 foi tratada como patch minimo ou no-op controlado
- [x] nenhum campo fora de checklist/gate foi alterado
- [x] a validacao final confirma preservacao de `status`, `audit_gate`, `gate_atual` e `ultima_auditoria`

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Ajustar manifesto F2 ao split canonico de gate | Aplicar o split do checklist em F2 ou registrar no-op controlado. | 2 | done | [ISSUE-F1-02-001-AJUSTAR-MANIFESTO-F2-AO-SPLIT-CANONICO-DE-GATE.md](./issues/ISSUE-F1-02-001-AJUSTAR-MANIFESTO-F2-AO-SPLIT-CANONICO-DE-GATE.md) |
| ISSUE-F1-02-002 | Ajustar manifesto F3 ao split canonico de gate | Aplicar o split do checklist em F3 ou registrar no-op controlado. | 2 | done | [ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md](./issues/ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md) |

## Artifact Minimo do Epico

Manifestos F2 e F3 tratados estritamente no trecho de checklist/gate, com cada
resultado rastreado nas issues filhas.

## Dependencias

- [Issue de Baseline](./issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md)
- [Epic de Baseline](./EPIC-F1-01-BASELINE-DE-ADERENCIA-F2-F3-VS-TEMPLATE-CANONICO.md)
- [Fase](./F1_REVALIDACAO_F2_F3_GATE_EPICS.md)
- [PRD Derivado](../../PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md)
