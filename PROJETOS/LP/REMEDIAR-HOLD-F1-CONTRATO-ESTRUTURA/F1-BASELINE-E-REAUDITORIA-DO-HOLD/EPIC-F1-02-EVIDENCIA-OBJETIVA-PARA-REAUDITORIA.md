---
doc_id: "EPIC-F1-02-EVIDENCIA-OBJETIVA-PARA-REAUDITORIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F1-02 - Evidencia Objetiva para Reauditoria

## Objetivo

Transformar a aderencia ja existente do fluxo publico e da base de modelos em
evidencia executavel, repetivel e rastreavel para uma reauditoria independente
da F1, sem reimplementar o contrato nem reabrir escopo funcional.

## Resultado de Negocio Mensuravel

Um auditor futuro consegue rerodar os comandos definidos neste epic e validar,
sem inferencia vaga, que o contrato canônico, a paridade do wrapper legado, a
metadata critica e os thresholds estruturais observados estao compatíveis com a
remediacao esperada.

## Contexto Arquitetural

Este epic usa apenas superficies ja existentes no backend e frontend:
`test_leads_public_create_endpoint.py`,
`test_landing_public_endpoints.py`,
`src/services/__tests__/landing_public.test.ts`,
`src/pages/__tests__/EventLandingPage.test.tsx`,
`test_lp_ativacao_schema_contract.py`,
`c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py` e os arquivos
medidos por `SPEC-ANTI-MONOLITO.md`. O sibling continua proibido de alterar o
gate da F1 original ou absorver o refactor de `backend/app/routers/leads.py`.

## Definition of Done do Epico

- [x] a evidencia backend do contrato canônico e do wrapper legado esta consolidada
- [x] a evidencia frontend do submit via `/leads` esta consolidada
- [x] a evidencia de metadata, migration e thresholds esta consolidada
- [x] cada prova foi vinculada aos achados relevantes da auditoria F1

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Consolidar evidencia de contrato e paridade | Registrar prova executavel do contrato publico atual e da paridade do wrapper. | 3 | done | [ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md](./issues/ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md) |
| ISSUE-F1-02-002 | Consolidar evidencia de metadata e threshold | Registrar prova executavel de metadata critica, migration e thresholds originais do hold. | 2 | done | [ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md](./issues/ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md) |

## Artifact Minimo do Epico

Evidencia rastreavel consolidada nas issues `ISSUE-F1-02-001` e
`ISSUE-F1-02-002`, com comandos reproduziveis, leitura objetiva dos resultados
e mapeamento para os achados do hold.

## Dependencias

- [Epic de Baseline](./EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md)
- [PRD Derivado](../../PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md)
- [Auditoria de Origem](../../auditoria_fluxo_ativacao.md)
- [Fase](./F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)
