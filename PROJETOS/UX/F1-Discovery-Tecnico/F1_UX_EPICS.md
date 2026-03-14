---
doc_id: "F1_UX_EPICS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-14"
audit_gate: "pending"
---

# Epicos - UX / F1 - Discovery Tecnico

## Objetivo da Fase

Resolver lacunas conhecidas do intake e validar premissas antes da implementacao. Identificar componentes de preview, estrutura de layout do wizard, biblioteca de drag-and-drop, breakpoint e conteudo das colunas direitas nas etapas Evento e Questionario.

## Gate de Saida da Fase

- Todas as lacunas `nao_definido` do intake resolvidas e documentadas
- Decisoes de arquitetura registradas (componentes compartilhados, lib de dnd, breakpoint)
- Confirmacao de que "Contexto da landing" cobre 100% dos valores do dropdown "Tema" removido

## Estado do Gate de Auditoria

- gate_atual: `pending`
- ultima_auditoria: `F1-R01` (provisional, verdict go — worktree suja; reauditar apos commit para aprovar)

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Levantamento e Documentacao | Mapear componentes, layout, dnd, breakpoint, coluna direita e cobertura Tema | nenhuma | done | [EPIC-F1-01-Levantamento-Documentacao.md](./EPIC-F1-01-Levantamento-Documentacao.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- Identificar nomes exatos dos componentes de preview (landing e ativacao)
- Documentar estrutura atual de layout do wizard (CSS Grid / Flexbox / outro)
- Verificar se existe biblioteca de drag-and-drop no codebase; se nao, recomendar e obter aprovacao
- Definir breakpoint de colapso para coluna unica
- Definir conteudo da coluna direita nas etapas Evento e Questionario
- Confirmar que o seletor "Contexto da landing" cobre todos os valores do dropdown "Tema" removido

### Fora
- Implementacao de layout (F2)
- Alteracoes em codigo

## Definition of Done da Fase
- [x] Lacunas do PRD resolvidas e documentadas
- [x] Decisoes de arquitetura registradas
- [x] Cobertura Tema/Contexto confirmada
