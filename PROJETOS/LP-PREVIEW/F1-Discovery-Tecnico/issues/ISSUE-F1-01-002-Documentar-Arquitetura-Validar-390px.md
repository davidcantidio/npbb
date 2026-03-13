---
doc_id: "ISSUE-F1-01-002-Documentar-Arquitetura-Validar-390px.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-01-002 - Documentar Decisao de Arquitetura e Validar 390px

## User Story

Como PM ou desenvolvedor, quero a decisao de arquitetura (componente compartilhado ou nao) registrada e a largura-alvo 390px validada com design, para prosseguir com confianca na F2.

## Contexto Tecnico

O PRD propoe viewport mobile ~390px (referencia iPhone 16). A validacao com design evita retrabalho. A decisao de arquitetura (reuso de componente vs instancias distintas) impacta o escopo da F2.

## Plano TDD

- Red: N/A (documentacao e validacao)
- Green: Decisao registrada; 390px validado
- Refactor: N/A

## Criterios de Aceitacao

- Given o mapeamento da ISSUE-F1-01-001, When consolido, Then registro a decisao de arquitetura (componente compartilhado ou nao) com justificativa
- Given a proposta de 390px do PRD, When valido com design, Then documento aprovacao ou ajuste

## Definition of Done da Issue
- [ ] Decisao de arquitetura documentada
- [ ] 390px validado com design (ou ajuste acordado registrado)

## Tasks Decupadas

- [x] T1: Consolidar decisao de arquitetura com base no mapeamento da F1-01-001
- [x] T2: Validar largura 390px com design (PM ou design system)
- [ ] T3: Documentar resultado da validacao na issue ou no epic

## Resultado Consolidado

### T1 - Decisao de arquitetura

Com base no mapeamento registrado na `ISSUE-F1-01-001`, a decisao de arquitetura
para a F2 fica consolidada da seguinte forma:

- `LandingPageView` permanece como renderer visual compartilhado entre o contexto
  publico da landing e o preview interno
- `EventLeadFormConfigPage`, `PreviewSection` e `useLandingPreview` formam o
  shell especifico do fluxo de configuracao
- a implementacao da F2 deve alterar o layout do shell de configuracao, sem
  transformar `LandingPageView` em componente de orquestracao de tela

Justificativa:

- o compartilhamento real identificado em F1 ocorre no renderer da landing
- o fluxo de configuracao possui responsabilidades proprias de carregamento,
  estado, acoes e posicionamento do preview
- separar renderer compartilhado de shell especifico reduz risco de acoplamento
  indevido ao refatorar o layout side-by-side

### T2 - Validacao da largura-alvo

Em 2026-03-13, o PM aprovou explicitamente o uso de `390px` como largura-alvo
do frame mobile para a F2.

Registro da validacao:

- a aprovacao do PM substitui, nesta fase de discovery, uma evidencia externa
  de design
- F2 fica autorizada a usar `390px` como alvo inicial do frame mobile
- qualquer ajuste posterior de design deve ser tratado como refinamento da F2 ou
  follow-up, sem reabrir a decisao base de F1

## Arquivos Reais Envolvidos

- Nenhum codigo; documentacao em issues/epic

## Artifact Minimo

- Decisao de arquitetura registrada no epic ou issue
- Evidencia de validacao 390px (ou ajuste)

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [Epic](../EPIC-F1-01-Levantamento-Documentacao.md)
- [Fase](../F1_LP-PREVIEW_EPICS.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [ISSUE-F1-01-001](./ISSUE-F1-01-001-Mapear-Componentes-Layout.md) — mapeamento previo
