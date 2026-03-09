---
doc_id: "EPIC-F2-02-METRICAS-NO-TEMPLATE-DE-AUDITORIA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F2-02 - Metricas no Template de Auditoria

## Objetivo

Levar `decision_refs`, tendencia entre rodadas e metricas de complexidade para
o template canonico de auditoria.

## Resultado de Negocio Mensuravel

Relatorios de auditoria passam a capturar complexidade estrutural de forma
comparavel entre rodadas.

## Contexto Arquitetural

- afeta `TEMPLATE-AUDITORIA-RELATORIO.md`
- depende do `SPEC-ANTI-MONOLITO.md`

## Definition of Done do Epico

- [ ] template de auditoria com secao de complexidade estrutural
- [ ] `decision_refs` disponivel no fluxo de auditoria
- [ ] tendencia entre rodadas documentavel

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Adicionar secao de complexidade estrutural ao template de auditoria | Levar thresholds e trend para o relatorio. | 3 | todo | [ISSUE-F2-02-001-ADICIONAR-SECAO-DE-COMPLEXIDADE-ESTRUTURAL-AO-TEMPLATE-DE-AUDITORIA.md](./issues/ISSUE-F2-02-001-ADICIONAR-SECAO-DE-COMPLEXIDADE-ESTRUTURAL-AO-TEMPLATE-DE-AUDITORIA.md) |
| ISSUE-F2-02-002 | Registrar decision refs e tendencia entre rodadas | Completar a camada de rastreabilidade do template. | 2 | todo | [ISSUE-F2-02-002-REGISTRAR-DECISION-REFS-E-TENDENCIA-ENTRE-RODADAS.md](./issues/ISSUE-F2-02-002-REGISTRAR-DECISION-REFS-E-TENDENCIA-ENTRE-RODADAS.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`

## Dependencias

- [Fase](./F2_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F2-01-SPEC-ANTI-MONOLITO.md)
