---
doc_id: "ISSUE-F3-01-001-VALIDAR-FUNDO-TEMATICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F3-01-001 - Validar Fundo Tematico Cross-Template

## User Story

Como PO, quero que cada template exiba seu fundo tematico correto (gradiente + overlay) em todos os breakpoints para garantir que o Manual BB esta sendo respeitado.

## Contexto Tecnico

Sao 7 templates × 3 breakpoints = 21 combinacoes a validar. Cada template tem um gradiente CSS e um overlay SVG/React especificos conforme PRD secao 05. A validacao deve comparar visualmente o output renderizado com a especificacao do PRD.

Templates: corporativo, esporte_convencional, esporte_radical, evento_cultural, show_musical, tecnologia, generico.
Breakpoints: 375px (mobile), 768px (tablet), 1280px (desktop).

## Plano TDD

- Red: sem matriz de validacao — nao ha evidencia sistematica de que os 7 templates estao corretos.
- Green: criar checklist de 21 combinacoes; capturar screenshot de cada; comparar com especificacao do PRD.
- Refactor: documentar desvios encontrados como bugs ou propostas de decisao.

## Criterios de Aceitacao

- Given o template `corporativo` em 375px, When a landing carrega, Then o gradiente e `linear-gradient(135deg, #1A237E 0%, #3333BD 60%, #465EFF 100%)` e o overlay exibe linhas retas
- Given o template `esporte_radical` em 768px, When a landing carrega, Then o gradiente e `linear-gradient(145deg, #3333BD 0%, #FF6E91 55%, #FCFC30 100%)` e o overlay exibe formas anguladas
- Given o template `show_musical` em 1280px, When a landing carrega, Then o gradiente e `linear-gradient(160deg, #0D0D1A 0%, #2D1B4E 50%, #4A1942 100%)` e o overlay exibe particulas
- Given qualquer template em qualquer breakpoint, When a landing carrega, Then o fundo preenche 100% da viewport sem gap
- Given qualquer template, When inspecionado, Then nenhuma imagem externa e carregada para o fundo

## Definition of Done da Issue

- [ ] 21 combinacoes validadas com evidencia visual
- [ ] zero desvios de gradiente em relacao ao PRD
- [ ] zero gaps de fundo em qualquer combinacao
- [ ] nenhuma imagem externa carregada

## Tarefas Decupadas

- [ ] T1: criar matriz de validacao 7 × 3 com criterios esperados
- [ ] T2: capturar screenshots dos 7 templates em 375px
- [ ] T3: capturar screenshots dos 7 templates em 768px
- [ ] T4: capturar screenshots dos 7 templates em 1280px
- [ ] T5: comparar gradientes e overlays com especificacao do PRD secao 05
- [ ] T6: documentar desvios encontrados
- [ ] T7: gerar relatorio de validacao

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/FullPageBackground.tsx`
- `frontend/src/components/landing/landingThemeBuilder.ts`
- `frontend/src/components/landing/LandingPageView.tsx`

## Artifact Minimo

- relatorio de validacao de fundo tematico com screenshots

## Dependencias

- [Epic](../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md)
- [Fase](../F3_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
