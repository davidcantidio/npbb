---
doc_id: "ISSUE-F3-01-001-Checklist-Regressao-Multiviewport.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-14"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-001 - Checklist de Regressao Multiviewport

## User Story

Como PM, quero um checklist de regressao executado em todas as etapas e viewports, para garantir que a refatoracao nao introduziu bugs antes do deploy.

## Contexto Tecnico

A F2 alterou layout, removiu redundancias e implementou drag-and-drop. A validacao manual deve cobrir: Evento, Formulario de Lead, Gamificacao, Ativacoes, Questionario; viewports desktop (1024px+), tablet (768px), mobile (390px); fluxo de criacao e edicao; reatividade do preview; persistencia ao salvar.

## Plano TDD

- Red: N/A (issue de validacao manual)
- Green: Checklist executado; resultados documentados
- Refactor: Consolidar achados em relatorio

## Criterios de Aceitacao

- Given cada etapa do wizard, When executo fluxo de configuracao, Then nao ha regressao funcional
- Given viewports desktop, tablet e mobile, When visualizo cada etapa, Then layout se comporta corretamente
- Given Formulario de Lead, When edito campos e arrasto ordem, Then preview atualiza e persistencia funciona
- Given o checklist completo, When PM revisa, Then aprova ou identifica itens bloqueantes

## Definition of Done da Issue
- [x] Checklist por etapa executado
- [x] Validacao multiviewport executada
- [x] Resultados documentados na issue ou artefato
- [x] PM aprovou ou follow-ups identificados

## Tasks Decupadas

- [x] T1: Executar checklist de regressao na etapa Evento (desktop, tablet, mobile)
- [x] T2: Executar checklist na etapa Formulario de Lead (layout, preview, dnd, redundancias removidas)
- [x] T3: Executar checklist nas etapas Gamificacao, Ativacoes e Questionario
- [x] T4: Documentar resultados e obter aprovacao do PM

## Arquivos Reais Envolvidos

- Todas as paginas do wizard
- `frontend/src/features/event-lead-form-config/`
- `frontend/src/pages/EventGamificacao.tsx`
- `frontend/src/pages/EventAtivacoes.tsx`
- `frontend/src/pages/EventQuestionario.tsx`
- `frontend/src/features/event-wizard/EventWizardPage.tsx`

## Artifact Minimo

Checklist preenchido com resultados por etapa e viewport; registro de aprovacao PM.

## Resultado da Execucao

### Ambiente e baseline

- Data da execucao: `2026-03-14`
- Validacao navegada em ambiente local autenticado com `david.cantidio@npbb.com.br`
- Evento criado para a rodada: `#117 - Evento Validacao F3 2026-03-14`
- Baseline automatizado executado:

```text
cd frontend
npm run test -- --run src/pages/__tests__/EventoPages.smoke.test.tsx src/features/event-wizard/__tests__/EventWizardPage.integration.test.tsx src/features/event-lead-form-config/hooks/useCamposState.test.tsx
```

- Resultado do baseline: `19/19 testes passando`

### Checklist por etapa e viewport

| Etapa | Desktop | Tablet | Mobile | Fluxo validado | Resultado | Observacoes |
|---|---|---|---|---|---|---|
| Evento | ok | ok | ok | criacao do evento `#117`, abertura de edicao e persistencia dos campos principais | ok | wizard criou o evento e carregou os valores persistidos na rota `/eventos/117/editar` |
| Formulario de Lead | falha | falha | falha | edicao de campos, drag-and-drop, reatividade do preview e persistencia | bloqueado | layout responsivo, DnD e persistencia passaram, mas ainda existem redundancias que deveriam ter sido removidas na F2 |
| Gamificacao | ok | ok | ok | criacao e edicao de gamificacao | ok | gamificacao `Gamificacao Validacao F3` criada e atualizada sem regressao funcional |
| Ativacoes | ok | ok | ok | criacao e edicao de ativacao com preview mobile | ok | ativacao `Ativacao Validacao F3` criada e atualizada; preview refletiu a edicao no painel direito |
| Questionario | ok | ok | ok | criacao de pagina/pergunta, salvamento e recarga | ok | questionario persistiu `Pagina 1` com a pergunta criada apos reload |

### Evidencias observadas

- `Evento`: desktop, tablet e mobile mantiveram stepper, botoes de navegacao e campos acessiveis; a rota de edicao carregou o evento `#117` com `Nome`, `UF`, `Cidade` e datas persistidos
- `Formulario de Lead`: desktop entrou em `side-by-side`; tablet e mobile colapsaram para `stacked`; mover `Estado` acima de `Telefone` atualizou o preview e remover `Telefone` persistiu apos `Salvar` e `reload`
- `Gamificacao`: desktop entrou em `side-by-side`; tablet e mobile colapsaram para `stacked`; criacao e edicao atualizaram a tabela sem erro
- `Ativacoes`: desktop entrou em `side-by-side`; tablet e mobile colapsaram para `stacked`; preview da landing foi carregado no painel direito apos salvar
- `Questionario`: desktop entrou em `side-by-side`; tablet e mobile colapsaram para `stacked`; salvamento mostrou feedback de sucesso e a estrutura reapareceu apos recarga

### Follow-ups identificados

1. Remover o box azul de `Customizacao controlada` ainda visivel no Formulario de Lead
2. Remover a secao `Governanca e performance` ainda visivel no Formulario de Lead
3. Remover o texto descritivo acima do preview (`O painel abaixo renderiza...`) ainda visivel no Formulario de Lead

### Conclusao da rodada

- Checklist executado integralmente
- Regressao funcional/visual localizada apenas na etapa `Formulario de Lead`
- `PM aprovou ou follow-ups identificados`: atendido via follow-ups bloqueantes acima
- Deploy nao aprovado nesta rodada

## Dependencias

- [Intake](../../../INTAKE-UX.md)
- [Epic](../EPIC-F3-01-Validacao-Regressao.md)
- [Fase](../F3_UX_EPICS.md)
- [PRD](../../../PRD-UX.md)
- [F2](../../../F2-Implementacao/F2_UX_EPICS.md) — concluida
