---
doc_id: "ISSUE-F2-02-003-Remover-Redundancias-Restantes.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-14"
task_instruction_mode: "required"
decision_refs: []
audit_id_origem: "F3-VALID-2026-03-14"
---

# ISSUE-F2-02-003 - Remover Redundancias Restantes no Formulario de Lead

## User Story

Como operador, quero uma interface limpa sem box informativo azul, secao "Governanca e performance" e texto descritivo acima do preview, para que a etapa Formulario de Lead atenda ao escopo do PRD e seja aprovada para deploy.

## Contexto Tecnico

A validacao F3 (ISSUE-F3-01-001) identificou que, apesar do layout side-by-side e drag-and-drop implementados, tres elementos redundantes permanecem visiveis no Formulario de Lead:

1. Box azul de "Customizacao controlada"
2. Secao "Governanca e performance"
3. Texto descritivo acima do preview ("O painel abaixo renderiza...")

Estes itens faziam parte do escopo da ISSUE-F2-02-001 e do PRD. Esta issue consolida o trabalho restante como follow-up rastreavel.

## Plano TDD

- Red: Teste que valida ausencia dos elementos removidos
- Green: Box azul, GovernanceSection e texto descritivo removidos
- Refactor: Ajustar imports e estrutura do componente

## Criterios de Aceitacao

- Given a pagina Formulario de Lead, When visualizo, Then nao existe box informativo azul de "Customizacao controlada"
- Given a pagina, When visualizo, Then nao existe secao "Governanca e performance"
- Given a pagina, When visualizo, Then nao existe texto descritivo acima do preview
- Given alteracoes em campos, When edito, Then o preview atualiza em tempo real (reatividade preservada)

## Definition of Done da Issue
- [ ] Box azul removido
- [ ] GovernanceSection removida
- [ ] Texto descritivo acima do preview removido
- [ ] Reatividade preservada
- [ ] Testes passando

## Tasks Decupadas

- [ ] T1: Remover box informativo azul (Customizacao controlada)
- [ ] T2: Remover GovernanceSection e seus imports
- [ ] T3: Remover texto descritivo acima do PreviewSection
- [ ] T4: Validar reatividade e testes

## Instructions por Task

### T1

- objetivo: remover box informativo azul de "Customizacao controlada"
- precondicoes: EventLeadFormConfigPage carregada
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/`
- passos_atomicos:
  1. Localizar o componente ou JSX que renderiza o box azul
  2. Remover o bloco e imports associados
  3. Verificar que nao ha referencias quebradas
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: box azul nao visivel na etapa Formulario de Lead
- testes_ou_validacoes_obrigatorias:
  - visualizar pagina e confirmar ausencia do box
  - testes existentes passam
- stop_conditions:
  - parar se a remocao quebrar funcionalidade critica; reportar

### T2

- objetivo: remover GovernanceSection
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/GovernanceSection.tsx`
- passos_atomicos:
  1. Remover import e uso de GovernanceSection em EventLeadFormConfigPage
  2. Verificar se GovernanceSection pode ser removido ou apenas nao utilizado nesta pagina
  3. Atualizar exports se necessario
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: secao "Governanca e performance" nao visivel
- testes_ou_validacoes_obrigatorias:
  - visualizar pagina e confirmar ausencia da secao
  - testes existentes passam
- stop_conditions:
  - parar se GovernanceSection for usado em outro lugar; avaliar remocao condicional

### T3

- objetivo: remover texto descritivo acima do preview
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Localizar o texto "O painel abaixo renderiza..." ou equivalente
  2. Remover o bloco Typography/Box que contem o texto
  3. Manter PreviewSection e frame mobile intactos
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: preview visivel sem texto descritivo acima
- testes_ou_validacoes_obrigatorias:
  - visualizar pagina e confirmar ausencia do texto
  - preview continua reativo
- stop_conditions:
  - parar se a remocao afetar o preview; reportar

### T4

- objetivo: validar reatividade e testes
- precondicoes: T1, T2, T3 concluidas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/`
- passos_atomicos:
  1. Executar suite de testes do modulo
  2. Validar manualmente que editar campos atualiza o preview
  3. Verificar que salvar persiste corretamente
- comandos_permitidos:
  - `cd frontend && npm run test -- --run`
- resultado_esperado: todos os testes passando; reatividade preservada
- testes_ou_validacoes_obrigatorias:
  - `npm run test -- --run` sem falhas
- stop_conditions:
  - parar e corrigir se algum teste falhar

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/features/event-lead-form-config/components/GovernanceSection.tsx`
- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`

## Artifact Minimo

Formulario de Lead sem box azul, GovernanceSection e texto descritivo; reatividade preservada.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F2-02-Formulario-Lead-Drag-and-Drop-Limpeza.md)
- [Fase](../F2_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [ISSUE-F2-02-001](./ISSUE-F2-02-001-Remover-Redundancias-Aplicar-Preview-Mobile.md) — escopo parcial; esta issue completa o restante
- [ISSUE-F3-01-001](../../F3-Validacao/issues/ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md) — origem dos follow-ups
