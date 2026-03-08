---
doc_id: "ISSUE-F3-01-003-VALIDAR-GAMIFICACAO.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08T20:00:00Z"
---

# ISSUE-F3-01-003 - Validar Gamificacao no Novo Layout

## User Story

Como PO, quero garantir que o fluxo de gamificacao funciona sem regressao no novo layout form-only em todos os templates para que nenhuma ativacao com gamificacao seja prejudicada.

## Contexto Tecnico

O GamificacaoBlock foi reposicionado abaixo do FormCard (F1). Precisa ser validado que o fluxo completo de estados (PRESENTING → ACTIVE → COMPLETED) funciona em todos os 7 templates. O botao "Quero participar" deve habilitar apos submit do lead. O reset deve retornar ao estado PRESENTING.

## Plano TDD

- Red: sem teste sistematico do fluxo de gamificacao no novo layout.
- Green: executar fluxo completo em cada template; documentar resultado.
- Refactor: documentar desvios como bugs.

## Criterios de Aceitacao

- Given qualquer template com gamificacao, When o lead e submetido, Then o GamificacaoBlock transita de PRESENTING para ACTIVE
- Given o GamificacaoBlock em ACTIVE, When "Quero participar" e clicado, Then o fluxo de gamificacao executa
- Given o GamificacaoBlock em COMPLETED, When reset e acionado, Then o bloco volta a PRESENTING e o formulario e limpo
- Given o GamificacaoBlock no novo layout, When posicionado abaixo do FormCard, Then o fundo tematico e visivel por tras
- Given cada um dos 7 templates, When o fluxo completo e executado, Then nenhuma regressao visual ou funcional e detectada

## Definition of Done da Issue

- [x] fluxo PRESENTING → ACTIVE → COMPLETED validado em todos os 7 templates
- [x] fundo tematico visivel por tras do GamificacaoBlock em todos os templates
- [x] zero regressoes funcionais
- [x] relatorio de validacao documentado

## Tarefas Decupadas

- [x] T1: preparar dados de teste com gamificacoes ativas para cada template
- [x] T2: executar fluxo completo de gamificacao em cada template
- [x] T3: verificar transicoes de estado PRESENTING → ACTIVE → COMPLETED
- [x] T4: verificar que fundo tematico e visivel por tras do bloco
- [x] T5: documentar resultados e abrir issues de correcao se necessario

## Execução

- script: `backend/scripts/seed_playwright_smoke.py`
- spec e2e: `frontend/e2e/issue-f3-01-003-gamificacao-validation.spec.ts`
- matriz executada: `7 templates × 3 breakpoints = 21 cenários`
- evidencia estruturada: `artifacts/phase-f3/evidence/issue-f3-01-003-results.json`
- relatorio: `artifacts/phase-f3/issue-f3-01-003-validacao-gamificacao.md`

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/GamificacaoBlock.tsx`
- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/e2e/issue-f3-01-003-gamificacao-validation.spec.ts`
- `backend/scripts/seed_playwright_smoke.py`

## Artifact Minimo

- relatorio de validacao de gamificacao cross-template
- `artifacts/phase-f3/issue-f3-01-003-validacao-gamificacao.md`
- `artifacts/phase-f3/evidence/issue-f3-01-003-results.json`

## Dependencias

- [Epic](../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md)
- [Fase](../F3_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
