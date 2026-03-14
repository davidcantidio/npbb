---
doc_id: "EPIC-F2-02-Formulario-Lead-Drag-and-Drop-Limpeza.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-14"
---

# EPIC-F2-02 - Formulario de Lead - Drag-and-drop e Limpeza

## Objetivo

Remover redundancias na etapa Formulario de Lead (Tema duplicado, box azul, Governanca e performance, texto descritivo), aplicar preview em frame mobile ~390px, e implementar campos em 1 coluna com visibilidade progressiva e reordenacao por drag-and-drop.

## Resultado de Negocio Mensuravel

Interface limpa sem elementos redundantes; preview mobile visivel; campos reordenaveis por arrastar; CPF, Nome, Sobrenome e Data de nascimento pre-selecionados por padrao.

## Contexto Arquitetural

EventLeadFormConfigPage possui TemaSection, LandingContextSection, PreviewSection, GovernanceSection, CamposSection. Remover TemaSection (redundante com LandingContextSection), GovernanceSection, box informativo azul e texto descritivo. CamposSection precisa migrar para 1 coluna, visibilidade progressiva via botao "+" e drag-and-drop (lib aprovada na F1).

## Definition of Done do Epico
- [ ] Redundancias removidas
- [x] Preview em frame mobile ~390px
- [x] Campos em 1 coluna com visibilidade progressiva
- [x] Drag-and-drop funcional para reordenacao
- [x] CPF nao desmarcavel; Nome, Sobrenome, Data nascimento pre-selecionados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Remover Redundancias e Aplicar Preview Mobile | Remover Tema, box azul, Governanca, texto; preview ~390px | 3 | todo | [ISSUE-F2-02-001-Remover-Redundancias-Aplicar-Preview-Mobile.md](./issues/ISSUE-F2-02-001-Remover-Redundancias-Aplicar-Preview-Mobile.md) |
| ISSUE-F2-02-002 | Implementar Campos em 1 Coluna com Drag-and-drop | Campos 1 coluna, visibilidade progressiva, dnd | 3 | done | [ISSUE-F2-02-002-Implementar-Campos-Drag-and-Drop.md](./issues/ISSUE-F2-02-002-Implementar-Campos-Drag-and-Drop.md) |
| ISSUE-F2-02-003 | Remover Redundancias Restantes | Box azul, GovernanceSection, texto descritivo (follow-up F3) | 2 | todo | [ISSUE-F2-02-003-Remover-Redundancias-Restantes.md](./issues/ISSUE-F2-02-003-Remover-Redundancias-Restantes.md) |

## Artifact Minimo do Epico

Formulario de Lead refatorado; preview mobile; drag-and-drop funcional.

## Dependencias
- [Intake](../../INTAKE-UX.md)
- [PRD](../../PRD-UX.md)
- [Fase](./F2_UX_EPICS.md)
- [EPIC-F2-01](./EPIC-F2-01-Layout-Side-by-Side.md)
- [F1](../../F1-Discovery-Tecnico/F1_UX_EPICS.md) — concluida
