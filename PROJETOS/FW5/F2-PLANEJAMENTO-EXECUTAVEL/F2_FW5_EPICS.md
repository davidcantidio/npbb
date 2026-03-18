---
doc_id: "F2_FW5_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
audit_gate: "not_ready"
---

# Epicos - FW5 / F2 - Planejamento executavel

## Objetivo da Fase

Derivar a cadeia executavel do projeto a partir das features aprovadas no PRD.

## Features Entregues

- Feature 3: Planejamento executavel com rastreabilidade canonica

## Gate de Saida da Fase

O projeto exibe fases, epicos, issues e tasks com `Feature de Origem` explicita e sem drift para planejamento por camada tecnica.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/FW5/F2-PLANEJAMENTO-EXECUTAVEL/auditorias/RELATORIO-AUDITORIA-F2-R01.md`
- log_do_projeto: [PROJETOS/FW5/AUDIT-LOG.md](PROJETOS/FW5/AUDIT-LOG.md)

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
| EPIC-F2-01 | Planejamento executavel rastreavel | Materializar a hierarquia canonica com `Feature de Origem` explicita e limites de issue/task respeitados. | Feature 3 | F1 aprovada | todo | [EPIC-F2-01-PLANEJAMENTO-EXECUTAVEL-RASTREAVEL.md](./EPIC-F2-01-PLANEJAMENTO-EXECUTAVEL-RASTREAVEL.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: F1 aprovada

## Escopo desta Fase

### Dentro
- derivacao de fases e epicos a partir das features do PRD
- derivacao de issues e tasks com dependencias, IDs e `Feature de Origem`
- mapa administrativo e navegacao da hierarquia planejada

### Fora
- execucao da proxima unidade elegivel
- politica de autonomia e disparo operacional
- review, auditoria final e timeline consultavel

## Definition of Done da Fase
- [ ] rastreabilidade `feature -> fase -> epico -> issue` visivel e consistente
- [ ] lacunas de nomeacao fina aparecem explicitamente quando existirem
- [ ] decomposicao respeita limites canonicos de issue/task ou sinaliza necessidade de quebra
