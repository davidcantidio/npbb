---
doc_id: "EPIC-F1-02-Coexistencia-Markdown-Banco-e-Rastreabilidade.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-02 - Coexistencia Markdown-Banco e Rastreabilidade

## Objetivo

Definir como o FRAMEWORK3 convive com o filesystem documental atual com bootstrap minimo e historico rastreavel.

## Resultado de Negocio Mensuravel

Projeto nasce com fonte de verdade declarada estado de sincronizacao observavel e trilha persistida de prompts aprovacoes e evidencias.

## Contexto Arquitetural

O framework atual depende de artefatos Markdown em `PROJETOS/` enquanto o produto alvo introduz persistencia em banco e historico estruturado. Este epic fecha precedencia bootstrap e rastreabilidade.

## Definition of Done do Epico
- [ ] fonte primaria e politica de sincronizacao aprovadas
- [ ] bootstrap minimo do projeto definido com paths e artefatos obrigatorios
- [ ] rastreabilidade de prompts aprovacoes e evidencias persistida sem ambiguidade

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Formalizar sincronizacao precedencia e bootstrap Markdown-banco | Projeto FRAMEWORK3 nasce com fonte de verdade declarada bootstrap minimo e estado de sincronizacao observavel. | 2 | todo | [ISSUE-F1-02-001-Formalizar-sincronizacao-precedencia-e-bootstrap-Markdown-banco](./issues/ISSUE-F1-02-001-Formalizar-sincronizacao-precedencia-e-bootstrap-Markdown-banco/) |
| ISSUE-F1-02-002 | Formalizar rastreabilidade de aprovacoes e artefatos | Rastreabilidade minima treinavel e auditavel persistida no dominio framework. | 1 | todo | [ISSUE-F1-02-002-Formalizar-rastreabilidade-de-aprovacoes-e-artefatos](./issues/ISSUE-F1-02-002-Formalizar-rastreabilidade-de-aprovacoes-e-artefatos/) |

## Artifact Minimo do Epico

Contrato de sincronizacao Markdown-banco e rastreabilidade operacional aprovado.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F1_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F1-01
