---
doc_id: "EPIC-F2-02-ANALISE-ETARIA-NO-CAMINHO-CANONICO-E-COBERTURA-EXECUTAVEL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F2-02 - Analise etaria no caminho canonico e cobertura executavel

## Objetivo

Consolidar o endpoint de analise etaria e suas suites sobre a semantica canonica aprovada.

## Resultado de Negocio Mensuravel

A primeira superficie visivel priorizada volta a ser confiavel para o mesmo evento sem depender de correcoes locais.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: analise etaria operando no caminho canonico com cobertura executavel

## Contexto Arquitetural

Reagrupa cobertura executavel do legado `F1-04` com paridade do consumidor analitico `F3-01` dentro do recorte final da Feature 1.

## Definition of Done do Epico
- [ ] endpoint de analise etaria opera apenas sobre o caminho canonico aprovado
- [ ] suites e fixtures provam paridade e ausencia de falso vazio
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Alinhar fixtures e suites ao modelo canonico | Fixtures e suites alinhadas ao modelo canonico | 2 | todo | [README](./issues/ISSUE-F2-02-001-ALINHAR-FIXTURES-E-SUITES-AO-MODELO-CANONICO/README.md) | Feature 1 |
| ISSUE-F2-02-002 | Consolidar a analise etaria no caminho canonico | Reader da analise etaria consolidado no caminho canonico | 2 | todo | [README](./issues/ISSUE-F2-02-002-CONSOLIDAR-A-ANALISE-ETARIA-NO-CAMINHO-CANONICO/README.md) | Feature 1 |
| ISSUE-F2-02-003 | Validar paridade da analise etaria | Paridade da analise etaria validada sobre fixtures canonicas | 1 | todo | [README](./issues/ISSUE-F2-02-003-VALIDAR-PARIDADE-DA-ANALISE-ETARIA/README.md) | Feature 1 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 1 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F2_DL2_EPICS.md)
