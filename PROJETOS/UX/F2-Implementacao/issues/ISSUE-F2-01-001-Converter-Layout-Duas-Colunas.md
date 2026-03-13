---
doc_id: "ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Converter Layout para Duas Colunas

## User Story

Como operador de configuracao, quero o painel de configuracao a esquerda e o conteudo contextual a direita em layout side-by-side em todas as 5 etapas do wizard, para correlacionar configuracao com resultado visual sem rolar a tela.

## Contexto Tecnico

As 5 paginas do wizard (EventWizardPage, EventLeadFormConfig, EventGamificacao, EventAtivacoes, EventQuestionario) usam hoje composicao vertical (Paper, Stack). O objetivo e converter para layout de duas colunas: painel esquerdo (scrollavel) e coluna direita (fixa com conteudo contextual). O resultado da F1 informa componentes e conteudo da coluna direita por etapa.

## Plano TDD

- Red: Teste que valida estrutura de duas colunas no DOM
- Green: Layout side-by-side implementado em todas as etapas
- Refactor: Extrair componente de layout compartilhado se necessario

## Criterios de Aceitacao

- Given qualquer etapa do wizard carregada, When visualizo, Then o painel de configuracao ocupa a coluna esquerda e o conteudo contextual a coluna direita
- Given o layout side-by-side, When rolo o painel esquerdo, Then a coluna direita permanece fixa e visivel
- Given alteracoes em campos do formulario (Formulario de Lead), When edito, Then o preview atualiza em tempo real (reatividade preservada)

## Definition of Done da Issue
- [ ] Layout de duas colunas em todas as 5 etapas
- [ ] Coluna direita fixa durante scroll
- [ ] Reatividade do preview preservada (Formulario de Lead)
- [ ] Testes de regressao passando

## Tasks Decupadas

- [ ] T1: Extrair ou criar componente de layout duas colunas compartilhado
- [ ] T2: Aplicar layout em EventLeadFormConfigPage (painel + PreviewSection a direita)
- [ ] T3: Aplicar layout em EventGamificacao (painel + lista gamificacoes a direita)
- [ ] T4: Aplicar layout em EventAtivacoes (painel + preview ativacao a direita)
- [ ] T5: Aplicar layout em EventWizardPage e EventQuestionario conforme F1
- [ ] T6: Validar reatividade e atualizar testes

## Instructions por Task

### T1

- objetivo: extrair ou criar componente de layout duas colunas reutilizavel (Grid ou Flexbox)
- precondicoes: F1 concluida; decisoes de layout documentadas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/components/eventos/EventWizardPageShell.tsx` (se existir)
- passos_atomicos:
  1. Identificar padrao comum entre as 5 paginas (Paper, Stack, etc.)
  2. Criar componente WizardTwoColumnLayout ou similar com props: leftContent, rightContent
  3. Usar CSS Grid (ex: grid-template-columns: 1fr 400px) ou Flexbox; painel esquerdo flexivel, direita com largura fixa
  4. Garantir que funcione em viewport desktop (min 1024px)
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: componente de layout criado e testavel
- testes_ou_validacoes_obrigatorias:
  - componente renderiza sem erro
- stop_conditions:
  - parar se houver conflito com estilos globais nao mapeados

### T2

- objetivo: aplicar layout duas colunas em EventLeadFormConfigPage
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Envolver conteudo em WizardTwoColumnLayout: secoes de config a esquerda, PreviewSection a direita
  2. Configurar coluna direita com position sticky para permanecer visivel ao rolar
  3. Garantir overflow-y no painel esquerdo
  4. Validar que useLandingPreview continua funcionando
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: Formulario de Lead exibe layout side-by-side; preview reativo
- testes_ou_validacoes_obrigatorias:
  - testes existentes de EventoPages.smoke.test passam
- stop_conditions:
  - parar se reatividade do preview quebrar

### T3

- objetivo: aplicar layout duas colunas em EventGamificacao
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/EventGamificacao.tsx`
- passos_atomicos:
  1. Identificar estrutura atual (formulario + lista de gamificacoes)
  2. Aplicar WizardTwoColumnLayout: formulario a esquerda, lista a direita
  3. Manter comportamento atual da lista
  4. Garantir scroll no painel esquerdo
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: Gamificacao exibe layout side-by-side
- testes_ou_validacoes_obrigatorias:
  - inspecao visual; nenhuma regressao funcional
- stop_conditions:
  - parar se lista de gamificacoes quebrar

### T4

- objetivo: aplicar layout duas colunas em EventAtivacoes com preview de ativacao a direita
- precondicoes: T3 concluida; F1 identificou componente de preview de ativacao
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/EventAtivacoes.tsx`
- passos_atomicos:
  1. Identificar componente de preview de ativacao (F1)
  2. Aplicar WizardTwoColumnLayout: formulario a esquerda, preview ativacao em frame mobile a direita
  3. Garantir que preview atualize conforme selecao/edicao
  4. Manter comportamento de criacao/edicao de ativacoes
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: Ativacoes exibe layout side-by-side com preview
- testes_ou_validacoes_obrigatorias:
  - inspecao visual; nenhuma regressao funcional
- stop_conditions:
  - parar se preview de ativacao nao existir; reportar e aguardar F1

### T5

- objetivo: aplicar layout duas colunas em EventWizardPage e EventQuestionario
- precondicoes: T4 concluida; F1 definiu conteudo da coluna direita
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-wizard/EventWizardPage.tsx`
  - `frontend/src/pages/EventQuestionario.tsx`
- passos_atomicos:
  1. Aplicar WizardTwoColumnLayout em EventWizardPage conforme conteudo definido na F1
  2. Aplicar WizardTwoColumnLayout em EventQuestionario conforme F1
  3. Garantir consistencia visual com demais etapas
  4. Validar navegacao entre etapas
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: Evento e Questionario exibem layout side-by-side
- testes_ou_validacoes_obrigatorias:
  - inspecao visual; fluxo do wizard funcional
- stop_conditions:
  - parar se conteudo da coluna direita nao estiver definido na F1; reportar

### T6

- objetivo: validar reatividade e atualizar testes
- precondicoes: T5 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`
- passos_atomicos:
  1. Rodar suite de testes completa
  2. Atualizar seletores/expectativas se necessario para nova estrutura
  3. Garantir que testes de reatividade do preview passem
  4. Adicionar teste de estrutura duas colunas se aplicavel
- comandos_permitidos:
  - `cd frontend && npm run test -- --run`
- resultado_esperado: todos os testes passando
- testes_ou_validacoes_obrigatorias:
  - `npm run test -- --run` passa
- stop_conditions:
  - parar se algum teste quebrar por mudanca nao intencional

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- `frontend/src/pages/EventGamificacao.tsx`
- `frontend/src/pages/EventAtivacoes.tsx`
- `frontend/src/pages/EventQuestionario.tsx`
- `frontend/src/features/event-wizard/EventWizardPage.tsx`
- `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`

## Artifact Minimo

Layout side-by-side funcional em todas as 5 etapas; testes passando.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F2-01-Layout-Side-by-Side.md)
- [Fase](../F2_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [F1](../../../F1-Discovery-Tecnico/F1_UX_EPICS.md) — concluida
