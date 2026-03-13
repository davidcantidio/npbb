---
doc_id: "ISSUE-F2-02-001-Frame-Celular-390px.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-001 - Aplicar Frame Visual de Celular e Viewport 390px

## User Story

Como operador, quero o preview renderizado dentro de um frame que simule um dispositivo movel (largura ~390px, referencia iPhone 16), para validar a experiencia real do usuario final durante a configuracao.

## Contexto Tecnico

O PRD exige viewport de dispositivo movel com largura-alvo ~390px e frame visual de celular. O preview atual (PreviewSection + LandingPageView) renderiza em largura fluida. E necessario encapsular o conteudo em um container com largura fixa 390px e borda/estilo que sugira um dispositivo movel. A F1 deve ter validado 390px com design.

## Plano TDD

- Red: Teste que verifica largura do container do preview (390px ou variavel configuravel)
- Green: Frame aplicado; preview renderiza em 390px
- Refactor: Extrair componente MobileFrame reutilizavel se necessario

## Criterios de Aceitacao

- Given o preview carregado, When visualizo, Then o preview esta dentro de um frame com largura ~390px
- Given o frame, When inspeciono, Then ha indicacao visual de dispositivo movel (borda arredondada, sombra ou similar)
- Given a largura 390px, When o conteudo da landing e renderizado, Then ocupa a largura do frame (viewport simulado)
- Given o frame, When a landing tem scroll interno, Then o scroll ocorre dentro do frame

## Definition of Done da Issue
- [ ] Frame de celular aplicado com largura 390px
- [ ] Indicacao visual de dispositivo movel
- [ ] Reatividade preservada dentro do frame
- [ ] Testes atualizados

## Tasks Decupadas

- [ ] T1: Criar componente ou wrapper para frame de celular (390px)
- [ ] T2: Aplicar frame ao container do preview em PreviewSection
- [ ] T3: Estilizar frame com borda arredondada e/ou sombra (estetica de dispositivo)
- [ ] T4: Garantir que LandingPageView respeite a largura do frame
- [ ] T5: Atualizar testes para validar dimensoes do frame

## Instructions por Task

### T1

- objetivo: criar componente ou wrapper para frame de celular com largura 390px
- precondicoes: F2-01-001 concluida (layout side-by-side); F1 validou 390px
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
  - novo componente opcional: `frontend/src/components/landing/MobilePreviewFrame.tsx` ou inline em PreviewSection
- passos_atomicos:
  1. Decidir se o frame sera componente reutilizavel ou wrapper inline em PreviewSection
  2. Criar container com largura fixa 390px (ou variavel CSS `--preview-mobile-width: 390px`)
  3. Garantir que o container tenha overflow adequado (hidden ou auto) para conteudo interno
  4. Manter compatibilidade com data-testid existente (event-lead-preview-host)
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: container com 390px de largura criado
- testes_ou_validacoes_obrigatorias:
  - inspecao visual confirma largura
- stop_conditions:
  - parar se 390px nao foi validado na F1 e design solicitou ajuste

### T2

- objetivo: aplicar o frame ao container do preview em PreviewSection
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Envolver o Box que contem LandingPageView com o frame (componente ou div com estilo)
  2. Garantir que o frame seja o container imediato do preview
  3. Passar props necessarias (data, mode) para LandingPageView inalterado
  4. Verificar que o preview continua recebendo dados e atualizando
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: preview renderizado dentro do frame
- testes_ou_validacoes_obrigatorias:
  - preview carrega e atualiza normalmente
- stop_conditions:
  - parar se o preview deixar de atualizar

### T3

- objetivo: estilizar o frame com borda arredondada e/ou sombra para estetica de dispositivo movel
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
  - ou `frontend/src/components/landing/MobilePreviewFrame.tsx`
- passos_atomicos:
  1. Aplicar borderRadius (ex: 16px ou 24px) ao container do frame
  2. Aplicar boxShadow ou border para dar sensacao de profundidade (dispositivo)
  3. Opcional: adicionar "notch" ou barra superior decorativa se design aprovar
  4. Manter acessibilidade (contraste, foco)
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: frame com aparencia de dispositivo movel
- testes_ou_validacoes_obrigatorias:
  - inspecao visual
- stop_conditions:
  - parar se estilo conflitar com tema existente de forma inaceitavel

### T4

- objetivo: garantir que LandingPageView respeite a largura do frame e renderize corretamente
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/components/landing/LandingPageView.tsx`
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Verificar que LandingPageView recebe width do parent (390px) e nao expande alem
  2. Garantir que elementos internos (FullPageBackground, FormCard, etc.) respeitam o viewport
  3. Testar landing com conteudo longo (scroll vertical dentro do frame)
  4. Verificar que gamificacao e form card funcionam dentro do frame
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: landing renderiza corretamente dentro de 390px
- testes_ou_validacoes_obrigatorias:
  - testes de LandingPageView e LandingAccessibility passam
- stop_conditions:
  - parar se layout da landing quebrar dentro do frame

### T5

- objetivo: atualizar testes para validar dimensoes do frame
- precondicoes: T4 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`
  - `frontend/src/components/landing/__tests__/LandingPageView.test.tsx`
- passos_atomicos:
  1. Atualizar ou adicionar expectativa de largura do container (390px) no smoke test
  2. Garantir que getByTestId('event-lead-preview-host') ainda funciona
  3. Verificar testes de acessibilidade no modo preview
  4. Rodar suite completa
- comandos_permitidos:
  - `cd frontend && npm run test -- --run`
- resultado_esperado: todos os testes passando
- testes_ou_validacoes_obrigatorias:
  - `npm run test -- --run` passa
- stop_conditions:
  - parar se testes falharem por alteracao nao coberta

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/FullPageBackground.tsx` (se aplicavel)
- `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`

## Artifact Minimo

- Frame de celular 390px aplicado
- Testes passando

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [Epic](../EPIC-F2-02-Frame-Mobile-Breakpoints.md)
- [Fase](../F2_LP-PREVIEW_EPICS.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [EPIC-F2-01](../EPIC-F2-01-Layout-Side-by-Side.md) — layout side-by-side concluido
