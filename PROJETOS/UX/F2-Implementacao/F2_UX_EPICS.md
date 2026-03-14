---
doc_id: "F2_UX_EPICS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-14"
audit_gate: "approved"
---

# Epicos - UX / F2 - Implementacao

## Objetivo da Fase

Implementar layout side-by-side em todas as 5 etapas do wizard, remover redundancias na etapa Landing Page, aplicar preview mobile ~390px, implementar campos em 1 coluna com drag-and-drop e tratar breakpoint para viewports menores.

## Gate de Saida da Fase

- Layout de duas colunas visivel em todas as etapas
- Zero elementos listados como removidos no escopo
- Reatividade do preview preservada
- Drag-and-drop funcional para reordenacao de campos
- Layout colapsa adequadamente em viewports menores

## Estado do Gate de Auditoria

- gate_atual: `approved`
- ultima_auditoria: `F2-R02`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Layout Side-by-Side | Converter layout para duas colunas em todas as 5 etapas e tratar breakpoint | F1 | done | [EPIC-F2-01-Layout-Side-by-Side.md](./EPIC-F2-01-Layout-Side-by-Side.md) |
| EPIC-F2-02 | Landing Page - Drag-and-drop e Limpeza | Remover redundancias, preview mobile, campos 1 coluna com dnd | EPIC-F2-01 | done | [EPIC-F2-02-Formulario-Lead-Drag-and-Drop-Limpeza.md](./EPIC-F2-02-Formulario-Lead-Drag-and-Drop-Limpeza.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: F1 concluida
- `EPIC-F2-02`: EPIC-F2-01

## Escopo desta Fase

### Dentro
- Layout de duas colunas em todas as 5 etapas
- Breakpoint para viewports menores
- Remocao de redundancias (Tema duplicado, box azul, Governanca e performance, texto descritivo)
- Preview mobile ~390px na etapa Landing Page
- Campos em 1 coluna com visibilidade progressiva e drag-and-drop
- Preview de ativacao em frame mobile na etapa Ativacoes

### Fora
- Novas funcionalidades de configuracao
- Redesign do sistema de design global
- Alteracao de API ou modelo de dados

## Definition of Done da Fase
- [ ] Layout side-by-side em todas as etapas
- [ ] Zero elementos redundantes
- [ ] Preview reativo preservado
- [ ] Drag-and-drop funcional
- [ ] Breakpoint implementado
