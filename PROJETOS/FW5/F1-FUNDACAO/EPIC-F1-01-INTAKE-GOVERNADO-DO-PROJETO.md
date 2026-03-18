---
doc_id: "EPIC-F1-01-INTAKE-GOVERNADO-DO-PROJETO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
---

# EPIC-F1-01 - Intake governado do projeto

## Objetivo

Estruturar validar revisar e aprovar o intake a partir de contexto bruto com historico de decisao consultavel.

## Resultado de Negocio Mensuravel

Reduzir o esforco manual do PM para abrir um projeto dentro da governanca canonica do FW5.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: intake estruturado com taxonomias, lacunas, checklist e gate `Intake -> PRD`

## Contexto Arquitetural

O backend ja possui um embriao do dominio `framework`; este epic fecha intake, versoes, lacunas e aprovacoes antes da derivacao do PRD.

## Definition of Done do Epico
- [ ] intake pode ser criado, validado, revisado e aprovado com trilha consultavel

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Estruturar intake inicial a partir de contexto bruto | Modelar gerar validar e expor intake inicial. | 5 | todo | [ISSUE-F1-01-001-ESTRUTURAR-INTAKE-INICIAL-A-PARTIR-DE-CONTEXTO-BRUTO](./issues/ISSUE-F1-01-001-ESTRUTURAR-INTAKE-INICIAL-A-PARTIR-DE-CONTEXTO-BRUTO/) | Feature 1 |
| ISSUE-F1-01-002 | Registrar revisao e aprovacao governada do intake | Persistir diff historico e gate `Intake -> PRD`. | 3 | todo | [ISSUE-F1-01-002-REGISTRAR-REVISAO-E-APROVACAO-GOVERNADA-DO-INTAKE](./issues/ISSUE-F1-01-002-REGISTRAR-REVISAO-E-APROVACAO-GOVERNADA-DO-INTAKE/) | Feature 1 |

## Artifact Minimo do Epico

Intake estruturado validavel e aprovavel com historico de revisao.

## Dependencias
- [Intake](../INTAKE-FW5.md)
- [PRD](../PRD-FW5.md)
- [Fase](./F1_FW5_EPICS.md)
