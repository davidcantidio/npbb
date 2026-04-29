---
doc_id: "FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
audit_gate: "not_ready"
---

# FEATURE-10 - Integracao do cache da analise etaria

## Objetivo de Negocio

Fechar a prontidao operacional da entrega de cache da analise etaria, provando
que migration, endpoint, UI, invalidacao por pipeline e gates de qualidade
funcionam juntos sem mudar o contrato publico.

## Resultado de Negocio Mensuravel

O time passa a ter uma trilha canonica para decidir staging do cache etario com
evidencias versionadas, classificacao clara de falhas e rollback simples.

## Dependencias da Feature

- `PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md`
- baseline funcional ja existente na trilha de leads e dashboard
- `FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD` como origem do bump por
  pipeline Gold

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- origem: follow-up operacional derivado de
  `PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md`
- contrato publico preservado: `sim`
- decisao escolhida: validar e remediar a entrega atual antes de staging, sem
  expandir para cache distribuido ou Fase D

## Criterios de Aceite

- [x] governanca propria da integracao criada
- [ ] pre-voo do workspace, migration e startup limpo registrados
- [ ] validacao backend executada com regressoes diretas corrigidas ou
      classificadas
- [ ] validacao frontend executada sem vazamento de cache entre escopos
- [ ] bump de `leads_age_analysis` comprovado apos pipeline Gold
- [ ] profiling e evidencias consolidados em `artifacts/phase-f4/evidence/`
- [ ] `make ci-quality` tentado antes da decisao de staging
- [ ] resumo final separa `regression`, `legacy-known` e `environment`

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-10-01 | Validar integracao local e remediar regressoes | 3 | nenhuma | active | [README](./user-stories/US-10-01-VALIDAR-INTEGRACAO-LOCAL-E-REMEDIAR-REGRESSOES/README.md) |
| US-10-02 | Consolidar evidencias e liberar staging | 2 | US-10-01 | active | [README](./user-stories/US-10-02-CONSOLIDAR-EVIDENCIAS-E-LIBERAR-STAGING/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- abrir cache distribuido
- executar Fase D de fact table ou MV
- redesenhar UX do dashboard
- reclassificar todo o legado historico do repo fora da trilha etaria

## Dependencias

- [PRD integracao cache analise etaria](../../PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md)
- [Intake integracao cache analise etaria](../../INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md)
- [Feature 1](../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
