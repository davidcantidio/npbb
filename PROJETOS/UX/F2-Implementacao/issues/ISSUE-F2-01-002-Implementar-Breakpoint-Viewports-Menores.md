---
doc_id: "ISSUE-F2-01-002-Implementar-Breakpoint-Viewports-Menores.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-14"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-002 - Implementar Breakpoint para Viewports Menores

## User Story

Como operador em tablet ou laptop pequeno, quero que o layout colapse para coluna unica quando a tela for estreita, para que eu consiga configurar sem perda de funcionalidade.

## Contexto Tecnico

O layout side-by-side deve colapsar para coluna unica abaixo do breakpoint definido na F1 (ex: 1024px ou 768px). O WizardTwoColumnLayout ou equivalente deve usar media queries ou MUI breakpoints para alternar entre duas colunas e coluna unica.

## Plano TDD

- Red: Teste que valida colapso em viewport estreito
- Green: Breakpoint implementado; layout colapsa adequadamente
- Refactor: Ajustar ordem de exibicao (config primeiro, contexto depois) na coluna unica

## Criterios de Aceitacao

- Given viewport menor que o breakpoint, When visualizo qualquer etapa, Then o layout exibe coluna unica (config acima, contexto abaixo)
- Given viewport maior que o breakpoint, When visualizo, Then o layout exibe duas colunas
- Given colapso, When rolo, Then todo o conteudo e acessivel

## Definition of Done da Issue
- [ ] Breakpoint implementado conforme F1
- [ ] Layout colapsa em viewports menores
- [ ] Ordem de exibicao em coluna unica definida (config primeiro)
- [ ] Testes em multiplos viewports passando

## Tasks Decupadas

- [ ] T1: Implementar breakpoint no componente de layout compartilhado
- [ ] T2: Validar colapso em todas as 5 etapas
- [ ] T3: Ajustar ordem e espacamento em coluna unica

## Instructions por Task

### T1

- objetivo: implementar breakpoint no WizardTwoColumnLayout para colapso em viewports menores
- precondicoes: ISSUE-F2-01-001 concluida; breakpoint definido na F1
- arquivos_a_ler_ou_tocar:
  - Componente de layout criado em ISSUE-F2-01-001
  - `frontend/src/theme` ou arquivo de breakpoints MUI (se existir)
- passos_atomicos:
  1. Obter valor do breakpoint da documentacao F1 (ex: 1024px, md, lg)
  2. Usar MUI useMediaQuery ou CSS media query para detectar viewport
  3. Abaixo do breakpoint: exibir Stack vertical (config primeiro, contexto depois)
  4. Acima do breakpoint: manter grid/flex duas colunas
  5. Garantir transicao suave
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: layout alterna entre duas colunas e coluna unica
- testes_ou_validacoes_obrigatorias:
  - inspecao visual em viewport estreito (DevTools)
- stop_conditions:
  - parar se breakpoint nao estiver definido na F1; usar 1024px como fallback e documentar

### T2

- objetivo: validar colapso em todas as 5 etapas do wizard
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - Todas as paginas do wizard
- passos_atomicos:
  1. Testar EventLeadFormConfig em viewport 768px e 375px
  2. Testar EventGamificacao, EventAtivacoes, EventQuestionario, EventWizardPage
  3. Verificar que nenhum conteudo fica cortado ou inacessivel
  4. Verificar que scroll funciona em coluna unica
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: todas as etapas colapsam corretamente
- testes_ou_validacoes_obrigatorias:
  - checklist manual por etapa
- stop_conditions:
  - parar se alguma etapa quebrar o layout

### T3

- objetivo: ajustar ordem e espacamento em coluna unica para UX consistente
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - Componente de layout
- passos_atomicos:
  1. Garantir que em coluna unica: painel de config apareca primeiro, contexto (preview/lista) depois
  2. Ajustar espacamento (Stack spacing) entre blocos
  3. Garantir que preview/contexto nao ocupe altura excessiva em mobile
  4. Validar em 390px (padrao mobile 2026)
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: ordem e espacamento consistentes
- testes_ou_validacoes_obrigatorias:
  - inspecao visual 390px
- stop_conditions:
  - parar se preview quebrar em mobile

## Arquivos Reais Envolvidos

- Componente de layout (criado em ISSUE-F2-01-001)
- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/pages/EventGamificacao.tsx`
- `frontend/src/pages/EventAtivacoes.tsx`
- `frontend/src/pages/EventQuestionario.tsx`
- `frontend/src/features/event-wizard/EventWizardPage.tsx`

## Artifact Minimo

Breakpoint funcional; layout colapsa em todas as etapas.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F2-01-Layout-Side-by-Side.md)
- [Fase](../F2_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [ISSUE-F2-01-001](./ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md) — concluida
- [F1](../../../F1-Discovery-Tecnico/F1_UX_EPICS.md) — concluida
