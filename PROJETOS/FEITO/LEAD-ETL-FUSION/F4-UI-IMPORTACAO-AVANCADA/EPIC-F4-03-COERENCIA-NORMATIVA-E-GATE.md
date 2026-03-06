---
doc_id: "EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F4-03 - Coerencia Normativa e Gate

## Objetivo

Fechar o projeto com evidencia auditavel de consistencia entre implementacao e contrato, cobertura cross-camada suficiente e decisao formal `promote | hold`.

## Resultado de Negocio Mensuravel

A promocao de fase deixa de depender de julgamento informal e passa a exigir evidencias objetivas sobre contrato, testes e prontidao operacional do fluxo ETL.

## Definition of Done

- `make eval-integrations` e `make ci-quality` possuem criterio de PASS ou FAIL rastreavel para o projeto.
- A fase tem um artifact unico de consolidacao com status de todos os epicos F1 a F4.
- Qualquer divergencia de contrato ou cobertura bloqueia a decisao de promote.
- A decisao final de fase fica registrada com justificativa explicita e auditavel.

## Issues

### ISSUE-F4-03-01 - Validar consistencia entre core/leads_etl e contratos documentados
Status: todo

**User story**
Como pessoa responsavel pela governanca tecnica, quero um gate automatizado de consistencia entre implementacao e contrato para impedir promocao de fase com drift entre codigo e modelo canonico.

**Plano TDD**
1. `Red`: ampliar `scripts/run_spec_checks.py`, `core/spec/tests/test_spec_gate.py` e `scripts/check_architecture_guards.sh` para falhar quando houver divergencia entre `core/leads_etl/` e o contrato documentado em `lead_row.py`.
2. `Green`: integrar a checagem contratual ao alvo planejado `make eval-integrations`, produzindo uma saida objetiva de PASS ou FAIL.
3. `Refactor`: consolidar a origem de verdade dos contratos e reduzir duplicacao entre spec checks, guards e evidencias do artifact final.

**Criterios de aceitacao**
- Given qualquer divergencia entre a implementacao e o modelo canonico `lead_row.py`, When `make eval-integrations` roda, Then o gate falha.
- Given ausencia de divergencia entre `core/leads_etl/` e os contratos documentados, When `make eval-integrations` roda, Then o resultado fica apto a PASS com evidencia consolidavel.

### ISSUE-F4-03-02 - Validar cobertura de testes cross-camada
Status: todo

**User story**
Como pessoa que aprova a entrega final, quero um gate de cobertura cross-camada para garantir que o fluxo ETL completo esta testado antes da promocao.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_import_preview_xlsx.py`, `backend/tests/test_leads_import_csv_smoke.py`, `frontend/src/features/leads-import/__tests__/LeadImportPage.validation.test.tsx` e `frontend/src/features/leads-import/hooks/__tests__/useLeadImportWorkflow.test.ts` para falhar quando nao houver cobertura fim a fim do fluxo ETL.
2. `Green`: integrar o criterio de cobertura ao alvo planejado `make ci-quality`, exigindo teste que cubra extract, transform, validate e persist.
3. `Refactor`: consolidar a matriz minima de cobertura cross-camada para facilitar manutencao dos gates e revisoes futuras.

**Criterios de aceitacao**
- Given ausencia de testes para o fluxo ETL end-to-end entre extract, transform, validate e persist, When `make ci-quality` roda, Then o gate falha.
- Given cobertura cross-camada presente, When `make ci-quality` roda, Then a fase pode prosseguir para a decisao final sem bloqueio por falta de teste.

### ISSUE-F4-03-03 - Consolidar evidencia de fase e decisao promote ou hold
Status: todo

**User story**
Como pessoa que conduz a revisao final da fase, quero um resumo unico com os gates e o status dos epicos para decidir `promote` ou `hold` de forma auditavel.

**Plano TDD**
1. `Red`: ampliar o fluxo de consolidacao em `lead_pipeline_MOVER/pipeline.py`, `lead_pipeline_MOVER/ppt_audit.py` e no proprio `EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md` para falhar quando a fase nao gerar um resumo unico de evidencias.
2. `Green`: produzir `artifacts/phase-f4/validation-summary.md` com status de `make eval-integrations`, `make ci-quality`, status de todos os epicos F1 a F4 e decisao `promote | hold`.
3. `Refactor`: padronizar o formato do resumo final para que auditoria, revisao humana e automacao usem a mesma estrutura de decisao.

**Criterios de aceitacao**
- Given evidencias dos epicos F1 a F4 e dos gates finais, When a revisao de fase ocorre, Then `artifacts/phase-f4/validation-summary.md` consolida o status de todos os epicos e a decisao `promote | hold`.
- Given evidencia incompleta, When a revisao ocorre, Then a decisao registrada e `hold` com justificativa explicita.

## Artifact Minimo do Epico

- `artifacts/phase-f4/validation-summary.md` com status de `make eval-integrations`, status de `make ci-quality`, estado dos epicos F1 a F4 e decisao final `promote | hold`.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
