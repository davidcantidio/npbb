---
doc_id: "ISSUE-F3-01-002-VALIDAR-CONTRASTE-WCAG.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F3-01-002 - Validar Contraste WCAG AA

## User Story

Como PO, quero que o contraste de texto do card e do rodape atenda WCAG AA em todos os templates para garantir acessibilidade.

## Contexto Tecnico

Criterios de contraste:
- Titulo e campos do formulario contra background do card: minimo 4.5:1 (WCAG AA)
- Rodape minimo contra fundo tematico: minimo 3:1 (texto caption/grande)
- O fundo tematico e puramente decorativo e nao carrega informacao

A validacao deve usar ferramentas de medicao de contraste (Chrome DevTools, axe, ou similar) para cada template.

## Plano TDD

- Red: sem medicao sistematica de contraste — nao ha evidencia de conformidade WCAG.
- Green: medir contraste do card e rodape em cada template; documentar resultados.
- Refactor: ajustar tokens de cor se algum template nao atingir o minimo.

## Criterios de Aceitacao

- Given o template `corporativo`, When o contraste do titulo contra o card e medido, Then o ratio e >= 4.5:1
- Given o template `show_musical`, When o contraste do rodape contra o fundo e medido, Then o ratio e >= 3:1
- Given qualquer template, When os campos do formulario sao avaliados, Then o contraste e >= 4.5:1
- Given qualquer template com falha de contraste, When identificado, Then o desvio e documentado como bug

## Definition of Done da Issue

- [ ] contraste de titulo e campos medido em todos os 7 templates
- [ ] contraste do rodape medido contra fundo de todos os 7 templates
- [ ] zero falhas de contraste WCAG AA
- [ ] relatorio de contraste documentado

## Tarefas Decupadas

- [ ] T1: medir contraste de titulo/campos contra card em cada template
- [ ] T2: medir contraste do rodape contra fundo tematico em cada template
- [ ] T3: documentar resultados em tabela com ratio de contraste
- [ ] T4: abrir issues de correcao para templates com contraste insuficiente
- [ ] T5: validar que amarelo BB (#FCFC30) como CTA ou borda atende contraste

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/FormCard.tsx`
- `frontend/src/components/landing/MinimalFooter.tsx`
- `frontend/src/components/landing/landingThemeBuilder.ts`

## Artifact Minimo

- relatorio de contraste WCAG AA com ratios por template

## Dependencias

- [Epic](../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md)
- [Fase](../F3_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
