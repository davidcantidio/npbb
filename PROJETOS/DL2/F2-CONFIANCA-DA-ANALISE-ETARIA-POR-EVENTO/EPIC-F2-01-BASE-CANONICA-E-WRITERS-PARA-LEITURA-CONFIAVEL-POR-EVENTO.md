---
doc_id: "EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F2-01 - Base canonica e writers para leitura confiavel por evento

## Objetivo

Fechar a baseline de `LeadEvento` e os caminhos minimos de escrita que sustentam a leitura confiavel por evento.

## Resultado de Negocio Mensuravel

A plataforma deixa de depender de relacoes implicitas para materializar o vinculo `lead-evento` necessario a analise etaria.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: baseline canonica de `LeadEvento` para writers e readers prioritarios

## Contexto Arquitetural

Reagrupa a fundacao do legado `F1-01`, `F1-02` e `F1-03` como habilitador direto da Feature 1, preservando o carry-over `done` apenas como evidencia rastreavel.

## Definition of Done do Epico
- [ ] migration e surface de modelos de `LeadEvento` estao estaveis
- [ ] submit publico, pipeline Gold e ETL deterministico asseguram o vinculo canonico necessario para a feature
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Estabilizar surface de modelo e boot da baseline canonica | Baseline canonica minima para surface e boot da aplicacao | 1 | done | [README](./issues/ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA/README.md) | Feature 1 |
| ISSUE-F2-01-002 | Versionar migration de lead_evento | Migration versionada e rastreavel de lead_evento | 2 | todo | [README](./issues/ISSUE-F2-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO/README.md) | Feature 1 |
| ISSUE-F2-01-003 | Garantir dual-write no submit publico | Dual-write canonico no submit publico | 2 | done | [README](./issues/ISSUE-F2-01-003-GARANTIR-DUAL-WRITE-NO-SUBMIT-PUBLICO/README.md) | Feature 1 |
| ISSUE-F2-01-004 | Cobrir duplicata de conversao e invariantes do submit | Invariantes do submit cobertos sobre o caminho canonico | 1 | done | [README](./issues/ISSUE-F2-01-004-COBRIR-DUPLICATA-DE-CONVERSAO-E-INVARIANTES-DO-SUBMIT/README.md) | Feature 1 |
| ISSUE-F2-01-005 | Garantir LeadEvento no pipeline Gold | Pipeline gold garantindo leadevento | 1 | done | [README](./issues/ISSUE-F2-01-005-GARANTIR-LEADEVENTO-NO-PIPELINE-GOLD/README.md) | Feature 1 |
| ISSUE-F2-01-006 | Garantir LeadEvento no ETL por evento_nome | Etl por evento_nome resolvendo leadevento de forma deterministica | 2 | todo | [README](./issues/ISSUE-F2-01-006-GARANTIR-LEADEVENTO-NO-ETL-POR-EVENTO-NOME/README.md) | Feature 1 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 1 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F2_DL2_EPICS.md)
