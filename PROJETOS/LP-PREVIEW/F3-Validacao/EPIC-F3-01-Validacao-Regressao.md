---
doc_id: "EPIC-F3-01-Validacao-Regressao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F3-01 - Validacao e Regressao

## Objetivo

Executar checklist de regressao manual, validar preview em multiplos viewports (desktop, tablet, mobile) e garantir zero bugs reportados relacionados ao preview apos implementacao da F2.

## Resultado de Negocio Mensuravel

Confianca na entrega: preview representativo, sem regressao, pronto para producao. Eliminacao de reclamacoes sobre preview nao representativo.

## Contexto Arquitetural

- F2 entregou layout side-by-side, frame mobile 390px e breakpoints
- Validacao deve cobrir EventLeadFormConfigPage e ambos os contextos (leads e landing page conforme F1)
- Viewports: desktop (1920x1080, 1366x768), tablet (768x1024), mobile (390x844)

## Definition of Done do Epico
- [ ] Checklist de regressao executado e documentado
- [ ] Validacao em desktop, tablet e mobile concluida
- [ ] Zero bugs reportados relacionados ao preview
- [ ] Metricas de sucesso do PRD validadas

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Checklist de Regressao e Validacao Multi-viewport | Executar checklist e validar em todos os viewports | 3 | todo | [ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md](./issues/ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md) |

## Artifact Minimo do Epico

- Checklist preenchido (markdown ou planilha)
- Relatorio de validacao com viewports testados e resultado
- Registro de bugs (se houver) e resolucao

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [Fase](./F3_LP-PREVIEW_EPICS.md)
- [F2](../../F2-Implementacao/F2_LP-PREVIEW_EPICS.md) — concluida
