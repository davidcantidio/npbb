---
doc_id: "ISSUE-F2-02-001-Remover-Redundancias-Aplicar-Preview-Mobile.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-001 - Remover Redundancias e Aplicar Preview Mobile

## User Story

Como operador, quero uma interface limpa sem dropdown duplicado, box informativo redundante e secoes desnecessarias, com preview da landing em frame mobile ~390px, para configurar com eficiencia.

## Contexto Tecnico

EventLeadFormConfigPage possui: TemaSection (redundante com LandingContextSection), box informativo azul, GovernanceSection, texto descritivo acima do preview. Remover todos e aplicar PreviewSection em frame mobile com largura ~390px. A F1 confirmou que "Contexto da landing" cobre os valores do "Tema".

## Plano TDD

- Red: Teste que valida ausencia dos elementos removidos e preview em frame
- Green: Redundancias removidas; preview em frame ~390px
- Refactor: Ajustar estilos do frame

## Criterios de Aceitacao

- Given a pagina Formulario de Lead, When visualizo, Then nao existe dropdown "Tema" duplicado (apenas "Contexto da landing")
- Given a pagina, When visualizo, Then nao existe box informativo azul redundante
- Given a pagina, When visualizo, Then nao existe secao "Governanca e performance"
- Given a pagina, When visualizo, Then nao existe texto descritivo acima do preview
- Given o preview, When visualizo, Then esta em frame mobile ~390px de largura
- Given alteracoes em campos, When edito, Then o preview atualiza em tempo real

## Definition of Done da Issue
- [ ] TemaSection removida (LandingContextSection permanece)
- [ ] Box informativo azul removido
- [ ] GovernanceSection removida
- [ ] Texto descritivo acima do preview removido
- [ ] Preview em frame mobile ~390px
- [ ] Reatividade preservada
- [ ] Testes passando

## Tasks Decupadas

- [ ] T1: Remover TemaSection e garantir que LandingContextSection seja o unico seletor
- [ ] T2: Remover box informativo azul e texto descritivo redundante
- [ ] T3: Remover GovernanceSection
- [ ] T4: Aplicar frame mobile ~390px ao PreviewSection
- [ ] T5: Validar reatividade e testes

## Instructions por Task

### T1

- objetivo: remover TemaSection e garantir que LandingContextSection seja o unico seletor de template
- precondicoes: F1 confirmou cobertura Tema/Contexto 100%
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/TemaSection.tsx`
  - `frontend/src/features/event-lead-form-config/components/LandingContextSection.tsx`
- passos_atomicos:
  1. Remover import e uso de TemaSection em EventLeadFormConfigPage
  2. Garantir que LandingContextSection receba templates e templateId corretamente
  3. Verificar que onTemplateChange ou equivalente esta conectado
  4. Remover arquivo TemaSection.tsx ou marcar como nao utilizado (conforme convencao do projeto)
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: apenas um seletor de template visivel; funcionalidade preservada
- testes_ou_validacoes_obrigatorias:
  - alterar template e verificar que preview atualiza
  - testes existentes passam
- stop_conditions:
  - parar se LandingContextSection nao cobrir todos os valores; reportar

### T2

- objetivo: remover box informativo azul e texto descritivo redundante
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
  - `frontend/src/features/event-lead-form-config/components/LandingContextSection.tsx`
- passos_atomicos:
  1. Localizar box informativo azul (Alert ou Box com bg azul) que repete informacao do seletor
  2. Remover o componente ou bloco
  3. Localizar texto descritivo acima do preview (ex: "O preview atualiza em tempo real...")
  4. Remover texto redundante; manter apenas o essencial se houver
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: interface sem box azul e texto redundante
- testes_ou_validacoes_obrigatorias:
  - inspecao visual
- stop_conditions:
  - parar se remover texto quebrar algum teste; ajustar teste

### T3

- objetivo: remover secao "Governanca e performance"
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/GovernanceSection.tsx`
- passos_atomicos:
  1. Remover import e uso de GovernanceSection em EventLeadFormConfigPage
  2. Verificar se GovernanceSection tem dados que precisam ser preservados em outro lugar; se nao, remover
  3. Remover ou deprecar arquivo GovernanceSection.tsx conforme convencao
  4. Garantir que nenhum hook ou estado dependa de GovernanceSection
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: secao Governanca e performance nao visivel
- testes_ou_validacoes_obrigatorias:
  - testes passam; nenhuma referencia quebrada
- stop_conditions:
  - parar se GovernanceSection tiver dados criticos; reportar ao PM

### T4

- objetivo: aplicar frame mobile ~390px ao PreviewSection
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Envolver o conteudo do preview (LandingPageView) em um container com largura fixa ~390px
  2. Aplicar estilos de "frame mobile" (borda, sombra, ou aparencia de dispositivo) se definido no design
  3. Garantir que o preview seja responsivo dentro do frame (scroll interno se necessario)
  4. Manter reatividade do useLandingPreview
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: preview exibido em frame ~390px
- testes_ou_validacoes_obrigatorias:
  - inspecao visual; preview atualiza ao editar campos
- stop_conditions:
  - parar se frame quebrar layout em coluna direita

### T5

- objetivo: validar reatividade e atualizar testes
- precondicoes: T4 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`
- passos_atomicos:
  1. Rodar suite de testes
  2. Atualizar expectativas que referenciem elementos removidos (TemaSection, GovernanceSection, etc.)
  3. Garantir que testes de reatividade do preview passem
  4. Verificar que seletores data-testid ainda funcionam
- comandos_permitidos:
  - `cd frontend && npm run test -- --run`
- resultado_esperado: todos os testes passando
- testes_ou_validacoes_obrigatorias:
  - `npm run test -- --run` passa
- stop_conditions:
  - parar se teste quebrar por remocao intencional; atualizar teste

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/features/event-lead-form-config/components/TemaSection.tsx`
- `frontend/src/features/event-lead-form-config/components/LandingContextSection.tsx`
- `frontend/src/features/event-lead-form-config/components/GovernanceSection.tsx`
- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`

## Artifact Minimo

Formulario de Lead sem redundancias; preview em frame mobile ~390px.

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F2-02-Formulario-Lead-Drag-and-Drop-Limpeza.md)
- [Fase](../F2_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [ISSUE-F2-01-001](./ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md) — layout concluido
- [F1](../../../F1-Discovery-Tecnico/F1_UX_EPICS.md) — concluida
