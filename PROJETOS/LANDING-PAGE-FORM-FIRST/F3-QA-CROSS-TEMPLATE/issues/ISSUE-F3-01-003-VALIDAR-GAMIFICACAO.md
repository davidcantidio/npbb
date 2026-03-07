---
doc_id: "ISSUE-F3-01-003-VALIDAR-GAMIFICACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
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

- [ ] fluxo PRESENTING → ACTIVE → COMPLETED validado em todos os 7 templates
- [ ] fundo tematico visivel por tras do GamificacaoBlock em todos os templates
- [ ] zero regressoes funcionais
- [ ] relatorio de validacao documentado

## Tarefas Decupadas

- [ ] T1: preparar dados de teste com gamificacoes ativas para cada template
- [ ] T2: executar fluxo completo de gamificacao em cada template
- [ ] T3: verificar transicoes de estado PRESENTING → ACTIVE → COMPLETED
- [ ] T4: verificar que fundo tematico e visivel por tras do bloco
- [ ] T5: documentar resultados e abrir issues de correcao se necessario

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/GamificacaoBlock.tsx`
- `frontend/src/components/landing/LandingPageView.tsx`

## Artifact Minimo

- relatorio de validacao de gamificacao cross-template

## Dependencias

- [Epic](../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md)
- [Fase](../F3_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
