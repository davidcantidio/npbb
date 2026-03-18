---
doc_id: "F2_FRAMEWORK3_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK3 / F2 - CRUD Base e Superficie Admin

## Objetivo da Fase

Estruturar o dominio persistido do FRAMEWORK3 e expor CRUD hierarquico e superficie admin integrada ao dashboard NPBB.

## Gate de Saida da Fase

O modulo Framework permite cadastrar consultar e manter projeto intake PRD fases epicos sprints issues tasks historico e proxima acao em backend e frontend.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F2-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Persistencia do Dominio de Projetos | Cobrir o modelo persistido de projeto ate task com relacionamentos coerentes e migrations rastreaveis. | F1 concluida | todo | [EPIC-F2-01-Persistencia-do-Dominio-de-Projetos.md](./EPIC-F2-01-Persistencia-do-Dominio-de-Projetos.md) |
| EPIC-F2-02 | APIs e Servicos CRUD Hierarquicos | Expor CRUD do dominio FRAMEWORK3 com navegacao hierarquica transicoes de aprovacao e validacoes de capacidade. | EPIC-F2-01 | todo | [EPIC-F2-02-APIs-e-Servicos-CRUD-Hierarquicos.md](./EPIC-F2-02-APIs-e-Servicos-CRUD-Hierarquicos.md) |
| EPIC-F2-03 | Modulo Admin Integrado ao Dashboard | Entregar a superficie administrativa do FRAMEWORK3 no dashboard NPBB com acesso protegido navegacao edicao e timeline. | EPIC-F2-01 EPIC-F2-02 | todo | [EPIC-F2-03-Modulo-Admin-Integrado-ao-Dashboard.md](./EPIC-F2-03-Modulo-Admin-Integrado-ao-Dashboard.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: F1 concluida
- `EPIC-F2-02`: EPIC-F2-01
- `EPIC-F2-03`: EPIC-F2-01 e EPIC-F2-02

## Escopo desta Fase

### Dentro
- consolidar persistencia de projeto ate task com rastreabilidade operacional
- expor APIs CRUD hierarquicas e transicoes de aprovacao
- implantar shell admin navegacao hierarquica edicao e timeline no dashboard

### Fora
- geracao assistida de intake PRD fases e tasks
- loop de execucao automatizada e review pos-issue
- auditoria de fase dataset treinavel e rollout controlado

## Definition of Done da Fase
- [ ] modelo schemas e APIs CRUD alinhados ao contrato canonico aprovado
- [ ] modulo admin protegido e navegavel no frontend
- [ ] timeline e proxima acao visiveis ao PM para o dominio framework
