---
doc_id: "EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F1-01 - Renomeacao para Convencao de Prefixo

## Objetivo

Renomear os artefatos de `PROJETOS/COMUM/` para prefixos funcionais e fechar as
referencias necessarias em entrypoints e projetos ativos.

## Resultado de Negocio Mensuravel

O PM identifica pelo nome do arquivo se deve ler, preencher, colar no chat ou
usar como referencia tecnica, sem depender de leitura exploratoria.

## Contexto Arquitetural

- altera `PROJETOS/COMUM/`
- altera `PROJETOS/boot-prompt.md`
- altera referencias em `FRAMEWORK2.0`, `PILOTO-ISSUE-FIRST` e `dashboard-leads-etaria`

## Definition of Done do Epico

- [x] artefatos comuns renomeados
- [x] entrypoints apontando para os nomes novos
- [x] projetos ativos sem referencias antigas obrigatorias

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Inventariar mapa de renomeacao e impacto em projetos ativos | Identificar o blast radius antes da renomeacao. | 3 | done | [ISSUE-F1-01-001-INVENTARIAR-MAPA-DE-RENOMEACAO-E-IMPACTO-EM-PROJETOS-ATIVOS.md](./issues/ISSUE-F1-01-001-INVENTARIAR-MAPA-DE-RENOMEACAO-E-IMPACTO-EM-PROJETOS-ATIVOS.md) |
| ISSUE-F1-01-002 | Renomear arquivos de COMUM e alinhar referencias internas | Executar a renomeacao central do framework comum. | 5 | done | [ISSUE-F1-01-002-RENOMEAR-ARQUIVOS-DE-COMUM-E-ALINHAR-REFERENCIAS-INTERNAS.md](./issues/ISSUE-F1-01-002-RENOMEAR-ARQUIVOS-DE-COMUM-E-ALINHAR-REFERENCIAS-INTERNAS.md) |
| ISSUE-F1-01-003 | Atualizar boot prompt e session mapa para a convencao nova | Corrigir os pontos de entrada do framework. | 3 | done | [ISSUE-F1-01-003-ATUALIZAR-BOOT-PROMPT-E-SESSION-MAPA.md](./issues/ISSUE-F1-01-003-ATUALIZAR-BOOT-PROMPT-E-SESSION-MAPA.md) |
| ISSUE-F1-01-004 | Corrigir referencias antigas nos projetos ativos | Fechar o impacto em projetos ativos. | 4 | done | [ISSUE-F1-01-004-CORRIGIR-REFERENCIAS-ANTIGAS-NOS-PROJETOS-ATIVOS.md](./issues/ISSUE-F1-01-004-CORRIGIR-REFERENCIAS-ANTIGAS-NOS-PROJETOS-ATIVOS.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/`

## Dependencias

- [Intake](../INTAKE-FRAMEWORK2.0.md)
- [PRD](../PRD-FRAMEWORK2.0.md)
- [Fase](./F1_FRAMEWORK2_0_EPICS.md)
