---
doc_id: "ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-001 - Checklist de Regressao e Validacao Multi-viewport

## User Story

Como PM ou QA, quero executar um checklist de regressao e validar o preview em diferentes viewports (desktop, tablet, mobile), para garantir que a refatoracao nao introduziu bugs e atende aos criterios de sucesso do PRD.

## Contexto Tecnico

A F2 entregou layout side-by-side, frame mobile 390px e breakpoints. E necessario validar manualmente em desktop (1920x1080, 1366x768), tablet (768x1024) e mobile (390x844). O checklist deve cobrir: layout, reatividade, frame, breakpoint, ambos os contextos (leads e landing page conforme F1).

## Plano TDD

- Red: N/A (validacao manual)
- Green: Checklist executado; zero bugs reportados
- Refactor: Documentar achados e ajustes realizados

## Criterios de Aceitacao

- Given desktop com viewport grande (>= 1024px), When acesso a pagina de configuracao, Then layout side-by-side; preview fixo a direita; frame 390px
- Given desktop com viewport menor (< breakpoint), When acesso, Then layout empilhado; preview abaixo do painel; reatividade preservada
- Given tablet ou mobile, When acesso, Then layout colapsa adequadamente; preview acessivel
- Given alteracoes em campos, When edito em qualquer viewport, Then preview atualiza em tempo real
- Given ambos os contextos (leads e landing page), When acesso cada um, Then comportamento consistente
- Given o checklist completo, When executo, Then zero bugs criticos reportados

## Definition of Done da Issue
- [ ] Checklist de regressao executado
- [ ] Validacao em desktop, tablet e mobile concluida
- [ ] Ambos os contextos validados
- [ ] Achados documentados (bugs corrigidos ou aceitos)
- [ ] Metricas de sucesso do PRD verificadas

## Tasks Decupadas

- [ ] T1: Criar ou preencher checklist de regressao (layout, reatividade, frame, breakpoint, contextos)
- [ ] T2: Executar validacao em desktop (1920x1080 e 1366x768)
- [ ] T3: Executar validacao em tablet (768x1024) e mobile (390x844)
- [ ] T4: Validar ambos os contextos (leads e landing page)
- [ ] T5: Documentar achados; corrigir bugs ou registrar como aceitos
- [ ] T6: Verificar metricas de sucesso do PRD (zero regressao, preview representativo)

## Arquivos Reais Envolvidos

- Nenhum codigo; documentacao em artefato ou issue
- Pagina de configuracao: `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`

## Artifact Minimo

- Checklist preenchido (em artefato ou na issue)
- Relatorio de validacao com viewports testados
- Lista de bugs (se houver) e status

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [Epic](../EPIC-F3-01-Validacao-Regressao.md)
- [Fase](../F3_LP-PREVIEW_EPICS.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [F2](../../F2-Implementacao/F2_LP-PREVIEW_EPICS.md) — concluida
