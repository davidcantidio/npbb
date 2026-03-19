---
doc_id: "F2_DL2_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-19"
audit_gate: "not_ready"
---

# Epicos - DL2 / F2 - Confianca da analise etaria por evento

## Objetivo da Fase

Entregar a primeira prova visivel de confianca por evento, fechando a baseline canonica minima e o reader da analise etaria.

## Gate de Saida da Fase

`/dashboard/leads/analise-etaria` deixa de apresentar falso vazio para eventos com leads validos e a baseline canonica minima fica demonstrada em teste.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/DL2/F2-CONFIANCA-DA-ANALISE-ETARIA-POR-EVENTO/auditorias/RELATORIO-AUDITORIA-F2-R01.md`
- log_do_projeto: [PROJETOS/DL2/AUDIT-LOG.md](PROJETOS/DL2/AUDIT-LOG.md)

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

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F2-01 | Base canonica e writers para leitura confiavel por evento | Fechar a baseline de `LeadEvento` e os caminhos minimos de escrita que sustentam a leitura confiavel por evento. | Feature 1 | F1-FUNDACAO | active | [EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md](./EPIC-F2-01-BASE-CANONICA-E-WRITERS-PARA-LEITURA-CONFIAVEL-POR-EVENTO.md) |
| EPIC-F2-02 | Analise etaria no caminho canonico e cobertura executavel | Consolidar o endpoint de analise etaria e suas suites sobre a semantica canonica aprovada. | Feature 1 | EPIC-F2-01 | todo | [EPIC-F2-02-ANALISE-ETARIA-NO-CAMINHO-CANONICO-E-COBERTURA-EXECUTAVEL.md](./EPIC-F2-02-ANALISE-ETARIA-NO-CAMINHO-CANONICO-E-COBERTURA-EXECUTAVEL.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende do bootstrap estrutural de `F1-FUNDACAO`
- `EPIC-F2-02`: depende de `EPIC-F2-01`

## Escopo desta Fase

### Dentro
- baseline minima de `LeadEvento` para readers e writers prioritarios
- migration e surface de modelos alinhadas ao caminho canonico
- ETL/importacao por `evento_nome` com match deterministico
- reader e paridade da analise etaria

### Fora
- consolidacao dos endpoints agregados `/dashboard/leads` e `/dashboard/leads/relatorio`
- backfill historico amplo e reconciliacao operacional
- retirada final do heuristico residual

## Definition of Done da Fase
- [ ] existe vinculo canonico minimo de `LeadEvento` para os writers e readers da feature
- [ ] o endpoint de analise etaria opera sem depender do caminho heuristico legado
- [ ] fixtures e suites automatizadas cobrem lead direto, lead via ativacao e caso nao resolvido
