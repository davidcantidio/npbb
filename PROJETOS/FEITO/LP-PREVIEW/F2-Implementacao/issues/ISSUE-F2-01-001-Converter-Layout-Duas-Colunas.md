---
doc_id: "ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Converter Layout para Duas Colunas Painel + Preview

## User Story

Como operador de configuracao, quero o painel de configuracao a esquerda e o preview a direita em layout side-by-side, fixo e visivel durante toda a sessao, para correlacionar configuracao com resultado visual sem rolar a tela.

## Contexto Tecnico

A pagina `EventLeadFormConfigPage` usa hoje um `Paper` com `Stack` vertical; as secoes (TemaSection, LandingContextSection, PreviewSection, etc.) sao empilhadas. O preview esta intercalado como faixa horizontal. O objetivo e converter para layout de duas colunas: painel esquerdo (scrollavel) e preview direito (fixo). O resultado da F1 deve informar componentes exatos e estrutura atual.

## Plano TDD

- Red: Teste que valida estrutura de duas colunas no DOM
- Green: Layout side-by-side implementado; preview fixo a direita
- Refactor: Extrair componente de layout compartilhado se necessario

## Criterios de Aceitacao

- Given a pagina de configuracao carregada, When visualizo, Then o painel de configuracao ocupa a coluna esquerda e o preview a coluna direita
- Given o layout side-by-side, When rolo o painel esquerdo, Then o preview permanece fixo e visivel
- Given alteracoes em campos do formulario, When edito, Then o preview atualiza em tempo real (reatividade preservada)
- Given os dois contextos (leads e landing page conforme F1), When aplico, Then ambos exibem layout side-by-side

## Definition of Done da Issue
- [ ] Layout de duas colunas implementado
- [ ] Preview fixo a direita
- [ ] Reatividade preservada
- [ ] Testes de regressao passando

## Tasks Decupadas

- [ ] T1: Refatorar EventLeadFormConfigPage para container de duas colunas (Grid ou Flexbox)
- [ ] T2: Mover PreviewSection para coluna direita e fixar posicao (sticky ou grid)
- [ ] T3: Garantir que painel esquerdo seja scrollavel e preview direito permaneca visivel
- [ ] T4: Validar reatividade (useLandingPreview) apos mudanca de layout
- [ ] T5: Atualizar testes de smoke/E2E para nova estrutura

## Instructions por Task

### T1

- objetivo: refatorar EventLeadFormConfigPage para container de duas colunas usando CSS Grid ou Flexbox
- precondicoes: F1 concluida; componentes e estrutura mapeados
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Abrir EventLeadFormConfigPage e identificar o container principal (Paper com Stack)
  2. Substituir ou envolver em um container de duas colunas: coluna esquerda para as secoes de config (TemaSection, LandingContextSection, CamposSection, etc.) e coluna direita para PreviewSection
  3. Usar CSS Grid (ex: `grid-template-columns: 1fr 400px`) ou Flexbox com proporcoes adequadas; painel esquerdo flexivel, preview direito com largura fixa inicial
  4. Garantir que o layout nao quebre em viewports padrao desktop (min 1024px)
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: pagina exibe duas colunas lado a lado
- testes_ou_validacoes_obrigatorias:
  - layout renderiza sem erro
  - inspecao visual confirma duas colunas
- stop_conditions:
  - parar se a alteracao quebrar a reatividade do preview
  - parar se houver conflito com estilos globais nao mapeados

### T2

- objetivo: mover PreviewSection para coluna direita e configurar para ficar fixo (sticky) durante scroll do painel esquerdo
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`
- passos_atomicos:
  1. Garantir que PreviewSection esteja na coluna direita do grid/flex
  2. Aplicar `position: sticky` e `top` adequado ao container do preview para que permaneca visivel ao rolar a coluna esquerda
  3. Garantir que o preview tenha altura controlada (max-height + overflow se necessario) para nao ultrapassar viewport
  4. Manter o botao "Atualizar preview" e "Abrir landing publica" acessiveis
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: preview permanece visivel ao rolar o painel esquerdo
- testes_ou_validacoes_obrigatorias:
  - scroll no painel esquerdo nao oculta o preview
  - preview continua responsivo ao editar campos
- stop_conditions:
  - parar se sticky causar layout quebrado em algum viewport
  - parar se o preview sumir ao rolar

### T3

- objetivo: garantir que painel esquerdo seja scrollavel e preview direito permaneca visivel durante toda a sessao
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- passos_atomicos:
  1. Verificar overflow-y do container da coluna esquerda (overflow-auto ou scroll)
  2. Garantir que a coluna direita tenha altura adequada (100vh ou calc) para viewport inteiro
  3. Testar scroll em conteudo longo do painel esquerdo; preview deve permanecer fixo
  4. Ajustar z-index se houver sobreposicao
- comandos_permitidos:
  - `cd frontend && npm run dev`
- resultado_esperado: painel esquerdo rola independentemente; preview sempre visivel
- testes_ou_validacoes_obrigatorias:
  - testes manuais de scroll
  - nenhum overflow horizontal indesejado
- stop_conditions:
  - parar se preview nao permanecer visivel em todo o scroll

### T4

- objetivo: validar que a reatividade (useLandingPreview, atualizacao ao editar campos) permanece apos mudanca de layout
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
  - `frontend/src/features/event-lead-form-config/hooks/useLandingPreview.ts`
- passos_atomicos:
  1. Testar alteracao de template (TemaSection) e verificar se preview atualiza
  2. Testar alteracao de descricao curta, CTA, campos ativos (LandingContextSection, CamposSection) e verificar preview
  3. Garantir que o debounce/useEffect de useLandingPreview continue funcionando
  4. Verificar que previewLoading e previewError sao exibidos corretamente no novo layout
- comandos_permitidos:
  - `cd frontend && npm run dev`
  - `cd frontend && npm run test -- --run`
- resultado_esperado: preview atualiza em tempo real ao editar qualquer campo relevante
- testes_ou_validacoes_obrigatorias:
  - testes existentes de EventoPages.smoke.test passam
  - teste de auto-refresh do preview passa
- stop_conditions:
  - parar se reatividade quebrar; reverter e investigar acoplamento

### T5

- objetivo: atualizar testes de smoke/E2E para refletir nova estrutura de layout
- precondicoes: T4 concluida
- arquivos_a_ler_ou_tocar:
  - `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`
  - `frontend/src/components/landing/__tests__/LandingPageView.test.tsx` (se aplicavel)
- passos_atomicos:
  1. Revisar seletores e expectativas nos testes que verificam layout do preview (ex: `event-lead-preview-host`)
  2. Atualizar expectativas de estilo/estrutura se necessario (ex: verificar que preview esta em coluna direita)
  3. Garantir que testes de reatividade (auto-refresh, ultimo preview visivel) continuem passando
  4. Rodar suite de testes completa
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
- `frontend/src/features/event-lead-form-config/hooks/useLandingPreview.ts`
- `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx`

## Artifact Minimo

- Layout side-by-side funcional
- Testes passando

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [Epic](../EPIC-F2-01-Layout-Side-by-Side.md)
- [Fase](../F2_LP-PREVIEW_EPICS.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [F1](../../F1-Discovery-Tecnico/F1_LP-PREVIEW_EPICS.md) — concluida
