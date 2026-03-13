---
doc_id: "F1_LP-PREVIEW_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-13"
audit_gate: "pending"
---

# Epicos - LP-PREVIEW / F1 - Discovery Tecnico

## Objetivo da Fase

Levantar informacoes tecnicas necessarias para implementacao segura do layout side-by-side e preview mobile. Resolver lacunas conhecidas do PRD sobre componentes, estrutura de layout e compartilhamento entre contextos.

## Gate de Saida da Fase

- Lacunas conhecidas do intake resolvidas e documentadas
- Decisao de arquitetura (componente compartilhado ou nao) registrada
- Largura-alvo 390px validada com design

## Estado do Gate de Auditoria

- gate_atual: `pending`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [x] todos os epicos estao `done`
- [x] todas as issues filhas estao `done`
- [x] DoD da fase foi revisado

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
| EPIC-F1-01 | Levantamento e Documentacao | Mapear componentes, layout, compartilhamento e validar 390px | nenhuma | done | [EPIC-F1-01-Levantamento-Documentacao.md](./EPIC-F1-01-Levantamento-Documentacao.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- Identificar nome exato do(s) componente(s) de preview no codebase
- Documentar estrutura atual de layout da pagina (CSS Grid / Flexbox / outro)
- Confirmar se o componente de preview e compartilhado entre leads e landing page ou sao instancias distintas
- Validar largura-alvo do frame mobile (390px) com design

### Fora
- Implementacao de layout (F2)
- Alteracoes em codigo

## Definition of Done da Fase
- [x] Lacunas do PRD resolvidas e documentadas
- [x] Decisao de arquitetura registrada
- [x] 390px validado com design
