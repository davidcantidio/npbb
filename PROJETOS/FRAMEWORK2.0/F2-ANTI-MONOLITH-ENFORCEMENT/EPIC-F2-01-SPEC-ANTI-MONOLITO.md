---
doc_id: "EPIC-F2-01-SPEC-ANTI-MONOLITO.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# EPIC-F2-01 - SPEC-ANTI-MONOLITO

## Objetivo

Definir thresholds objetivos para `monolithic-file` e `monolithic-function` e
calibrar a primeira versao com base em projeto ativo.

## Resultado de Negocio Mensuravel

Auditorias passam a justificar o achado de monolito com metricas verificaveis,
nao apenas por percepcao subjetiva.

## Contexto Arquitetural

- cria `SPEC-ANTI-MONOLITO.md`
- usa `dashboard-leads-etaria` como referencia de calibracao
- integra o spec a `GOV-AUDITORIA.md`

## Definition of Done do Epico

- [ ] thresholds por linguagem documentados
- [ ] calibracao minima registrada
- [ ] governanca de auditoria apontando para o spec

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Definir thresholds anti-monolito por linguagem | Fixar thresholds objetivos para TS/React e Python. | 2 | done | [ISSUE-F2-01-001-DEFINIR-THRESHOLDS-ANTI-MONOLITO-POR-LINGUAGEM.md](./issues/ISSUE-F2-01-001-DEFINIR-THRESHOLDS-ANTI-MONOLITO-POR-LINGUAGEM.md) |
| ISSUE-F2-01-002 | Calibrar thresholds usando dashboard leads etaria | Validar os valores com um projeto ativo de referencia. | 3 | todo | [ISSUE-F2-01-002-CALIBRAR-THRESHOLDS-USANDO-DASHBOARD-LEADS-ETARIA.md](./issues/ISSUE-F2-01-002-CALIBRAR-THRESHOLDS-USANDO-DASHBOARD-LEADS-ETARIA.md) |
| ISSUE-F2-01-003 | Integrar spec anti-monolito a governanca de auditoria | Fazer a auditoria consumir o spec como fonte de threshold. | 2 | todo | [ISSUE-F2-01-003-INTEGRAR-SPEC-ANTI-MONOLITO-A-GOVERNANCA-DE-AUDITORIA.md](./issues/ISSUE-F2-01-003-INTEGRAR-SPEC-ANTI-MONOLITO-A-GOVERNANCA-DE-AUDITORIA.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## Dependencias

- [Fase](./F2_FRAMEWORK2_0_EPICS.md)
- [Fase Dependente](../F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md)
