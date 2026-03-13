---
doc_id: "ISSUE-F2-02-002-Breakpoint-Viewports-Menores.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-02-002 - Tratamento de Breakpoint para Viewports Menores

## User Story

Como operador em desktop com resolucao baixa ou tablet, quero que o layout colapse de forma controlada (empilhado) quando a tela for menor, para nao perder funcionalidade.

## Contexto Tecnico

O PRD exige tratamento de breakpoint: em viewports menores (ex: tablet, desktop 1024px ou menos), o layout side-by-side pode nao caber. Deve haver fallback para layout empilhado (painel em cima, preview embaixo) de forma controlada. MUI usa breakpoints padrao (xs, sm, md, lg, xl).

## Plano TDD

- Red: Teste que verifica layout em viewport reduzido (matchMedia ou resize)
- Green: Layout colapsa adequadamente abaixo do breakpoint
- Refactor: Reutilizar breakpoint de tema MUI

## Criterios de Aceitacao

- Given viewport menor que o breakpoint (ex: 1024px ou md), When visualizo a pagina, Then o layout muda para empilhado (painel acima, preview abaixo)
- Given layout empilhado, When rolo a pagina, Then acesso ambas as secoes sem perda de funcionalidade
- Given viewport maior que o breakpoint, When redimensiono, Then o layout volta para side-by-side
- Given o layout colapsado, When edito campos, Then o preview ainda atualiza em tempo real

## Definition of Done da Issue
- [ ] Breakpoint definido e aplicado
- [ ] Layout colapsa para empilhado em viewports menores
- [ ] Reatividade preservada em ambos os modos
- [ ] Testes manuais ou automatizados

## Tasks Decupadas

- [ ] T1: Definir breakpoint (ex: lg=1280 ou md=960) para transicao side-by-side <-> empilhado
- [ ] T2: Aplicar sx/theme responsive ao container de duas colunas
- [ ] T3: Garantir ordem logica no modo empilhado (painel primeiro, preview depois)
- [ ] T4: Testar em viewports reais (tablet, desktop pequeno)

## Arquivos Reais Envolvidos

- `frontend/src/features/event-lead-form-config/EventLeadFormConfigPage.tsx`
- `frontend/src/features/event-lead-form-config/components/PreviewSection.tsx`

## Artifact Minimo

- Layout responsivo com breakpoint
- Documentacao do breakpoint utilizado

## Dependencias

- [Intake](../../INTAKE-LP-PREVIEW.md)
- [Epic](../EPIC-F2-02-Frame-Mobile-Breakpoints.md)
- [Fase](../F2_LP-PREVIEW_EPICS.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [ISSUE-F2-01-001](./ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md) — layout side-by-side
- [ISSUE-F2-02-001](./ISSUE-F2-02-001-Frame-Celular-390px.md) — frame mobile
