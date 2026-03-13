---
doc_id: "ISSUE-F2-02-002-Implementar-Campos-Drag-and-Drop.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-002 - Implementar Campos em 1 Coluna com Drag-and-drop

## User Story

Como operador, quero os campos possiveis em uma unica coluna, com CPF/Nome/Sobrenome/Data nascimento pre-selecionados por padrao, demais acessiveis via botao "+", e reordenacao por arrastar, para configurar de forma intuitiva.

## Contexto Tecnico

CamposSection usa hoje grid 2 colunas (xs: 1fr, md: 1fr 1fr) e indica ordem por texto. O PRD exige: 1 coluna, CPF obrigatorio e nao desmarcavel, Nome/Sobrenome/Data nascimento pre-selecionados, demais campos via botao "+", reordenacao por drag-and-drop. Biblioteca dnd aprovada na F1 (ex: @dnd-kit/core).

## Plano TDD

- Red: Teste que valida estrutura 1 coluna, campos pre-selecionados e dnd
- Green: CamposSection refatorado com dnd e visibilidade progressiva
- Refactor: Extrair logica de ordenacao

## Criterios de Aceitacao

- Given a secao de campos, When visualizo, Then os campos estao em 1 coluna
- Given CPF, When visualizo, Then esta pre-selecionado e nao desmarcavel
- Given Nome, Sobrenome, Data de nascimento, When visualizo, Then estao pre-selecionados por padrao
- Given demais campos, When visualizo, Then estao acessiveis via botao "+" (visibilidade progressiva)
- Given campos ativos, When arrasto, Then a ordem e alterada e persistida
- Given alteracao de ordem, When salvo, Then o preview reflete a nova ordem

## Definition of Done da Issue
- [ ] Campos em 1 coluna
- [ ] CPF obrigatorio e nao desmarcavel
- [ ] Nome, Sobrenome, Data nascimento pre-selecionados por padrao
- [ ] Botao "+" para adicionar demais campos
- [ ] Drag-and-drop funcional para reordenacao
- [ ] Ordem refletida no preview
- [ ] Testes passando

## Tasks Decupadas

- [ ] T1: Instalar e configurar biblioteca de drag-and-drop (se aprovada na F1)
- [ ] T2: Refatorar CamposSection para 1 coluna e visibilidade progressiva
- [ ] T3: Implementar estado de ordem e integracao com dnd
- [ ] T4: Garantir defaults (CPF, Nome, Sobrenome, Data nascimento) e CPF nao desmarcavel
- [ ] T5: Validar integracao com preview e testes

## Instructions por Task

### T1

- objetivo: instalar biblioteca de drag-and-drop aprovada na F1
- precondicoes: F1 documentou lib (ex: @dnd-kit/core, @dnd-kit/sortable)
- arquivos_a_ler_ou_tocar:
  - `frontend/package.json`
- passos_atomicos:
  1. Verificar documentacao F1 para lib aprovada
  2. Instalar pacotes: npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities (ou equivalente)
  3. Verificar que nao ha conflito com dependencias existentes
  4. Se F1 nao aprovou lib, parar e reportar; usar implementacao nativa HTML5 DnD como fallback temporario
- comandos_permitidos:
  - `cd frontend && npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities`
- resultado_esperado: lib instalada e importavel
- testes_ou_validacoes_obrigatorias:
  - build passa
- stop_conditions:
  - parar se PM nao aprovou nova dependencia; reportar

### T2

- objetivo: refatorar CamposSection para 1 coluna e visibilidade progressiva
- precondicoes: T1 concluida (ou fallback sem dnd)
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/CamposSection.tsx`
  - `frontend/src/features/event-lead-form-config/hooks/useCamposState.ts`
- passos_atomicos:
  1. Alterar grid de 2 colunas para 1 coluna (gridTemplateColumns: 1fr)
  2. Separar campos em dois grupos: pre-selecionados (CPF, Nome, Sobrenome, Data nascimento) e demais
  3. Implementar botao "+" que revela proximos campos nao selecionados
  4. Manter checkboxes e logica de toggle
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: campos em 1 coluna; botao "+" funcional
- testes_ou_validacoes_obrigatorias:
  - inspecao visual
- stop_conditions:
  - parar se useCamposState tiver contrato incompativel

### T3

- objetivo: implementar estado de ordem e integracao com drag-and-drop
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/CamposSection.tsx`
  - `frontend/src/features/event-lead-form-config/hooks/useCamposState.ts`
- passos_atomicos:
  1. Adicionar estado de ordem dos campos (array ordenado)
  2. Envolver lista de campos em DndContext e SortableContext
  3. Tornar cada item SortableItem com useSortable
  4. Implementar onDragEnd para atualizar ordem
  5. Sincronizar ordem com useCamposState e useLandingPreview
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: arrastar altera ordem; preview reflete
- testes_ou_validacoes_obrigatorias:
  - teste manual de drag-and-drop
- stop_conditions:
  - parar se ordem nao persistir ao salvar; verificar contrato API

### T4

- objetivo: garantir defaults (CPF, Nome, Sobrenome, Data nascimento) e CPF nao desmarcavel
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/CamposSection.tsx`
  - `frontend/src/features/event-lead-form-config/hooks/useCamposState.ts`
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- passos_atomicos:
  1. Garantir que em formulario novo, campos CPF, Nome, Sobrenome, Data de nascimento estejam em camposAtivos
  2. Desabilitar checkbox de CPF (nao desmarcavel)
  3. Garantir que CPF seja sempre obrigatorio quando ativo
  4. Validar que dados existentes (formulario edit) preservem configuracao salva
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: defaults corretos; CPF sempre ativo e nao desmarcavel
- testes_ou_validacoes_obrigatorias:
  - criar novo evento e verificar defaults
  - tentar desmarcar CPF e verificar que nao e possivel
- stop_conditions:
  - parar se nomes dos campos no codebase forem diferentes (ex: "Data de Nascimento" vs "Data nascimento")

### T5

- objetivo: validar integracao com preview e testes
- precondicoes: T4 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`
  - `frontend/src/features/event-lead-form-config/`
- passos_atomicos:
  1. Rodar suite de testes
  2. Atualizar testes que referenciem CamposSection ou ordem de campos
  3. Garantir que teste de reatividade do preview (alterar campos) passe
  4. Adicionar teste de drag-and-drop se aplicavel
- comandos_permitidos:
  - `cd frontend && npm run test -- --run`
- resultado_esperado: todos os testes passando
- testes_ou_validacoes_obrigatorias:
  - `npm run test -- --run` passa
- stop_conditions:
  - parar se teste quebrar; ajustar teste ou codigo

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/components/CamposSection.tsx`
- `frontend/src/features/event-lead-form-config/hooks/useCamposState.ts`
- `frontend/src/features/event-lead-form-config/hooks/useLandingPreview.ts`
- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`

## Artifact Minimo

CamposSection com 1 coluna, visibilidade progressiva, drag-and-drop e defaults corretos.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F2-02-Formulario-Lead-Drag-and-Drop-Limpeza.md)
- [Fase](../F2_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [ISSUE-F2-02-001](./ISSUE-F2-02-001-Remover-Redundancias-Aplicar-Preview-Mobile.md) — concluida
- [F1](../../../F1-Discovery-Tecnico/F1_UX_EPICS.md) — concluida (decisao dnd)
