---
doc_id: "F4_DL2_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
audit_gate: "not_ready"
---

# Epicos - DL2 / F4 - Historico reconciliado e operacao segura

## Objetivo da Fase

Fechar historico, reconciliacao, fallback, retirada do heuristico e pacote final de observabilidade/rollback.

## Gate de Saida da Fase

Historico resolvivel fica materializado com trilha auditavel, o heuristico residual sai do caminho oficial e a operacao fica pronta para auditoria.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/DL2/F4-HISTORICO-RECONCILIADO-E-OPERACAO-SEGURA/auditorias/RELATORIO-AUDITORIA-F4-R01.md`
- log_do_projeto: [PROJETOS/DL2/AUDIT-LOG.md](PROJETOS/DL2/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F4-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F4-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F4-01 | Backfill idempotente multi-origem | Materializar historico resolvivel em `LeadEvento` por execucao controlada e reexecutavel. | Feature 3 | F3 aprovada | todo | [EPIC-F4-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md](./EPIC-F4-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md) |
| EPIC-F4-02 | Reconciliacao manual e evidencias de pendencias historicas | Tornar visiveis os casos historicos nao resolvidos e formalizar o fechamento manual rastreavel. | Feature 3 | EPIC-F4-01 | todo | [EPIC-F4-02-RECONCILIACAO-MANUAL-E-EVIDENCIAS-DE-PENDENCIAS-HISTORICAS.md](./EPIC-F4-02-RECONCILIACAO-MANUAL-E-EVIDENCIAS-DE-PENDENCIAS-HISTORICAS.md) |
| EPIC-F4-03 | Protocolo operacional de fallback via bronze | Definir quando usar reprocessamento ou fallback via bronze sem abrir automacao destrutiva nova. | Feature 3 | EPIC-F4-02 | todo | [EPIC-F4-03-PROTOCOLO-OPERACIONAL-DE-FALLBACK-VIA-BRONZE.md](./EPIC-F4-03-PROTOCOLO-OPERACIONAL-DE-FALLBACK-VIA-BRONZE.md) |
| EPIC-F4-04 | Retirada controlada do heuristico residual | Eliminar codigo residual de uniao heuristica que nao faca mais parte do caminho oficial. | Feature 3 | EPIC-F4-03 | todo | [EPIC-F4-04-RETIRADA-CONTROLADA-DO-HEURISTICO-RESIDUAL.md](./EPIC-F4-04-RETIRADA-CONTROLADA-DO-HEURISTICO-RESIDUAL.md) |
| EPIC-F4-05 | Observabilidade, rollback e auditoria final | Consolidar o pacote operacional final para auditoria da remediacao. | Feature 3 | EPIC-F4-04 | todo | [EPIC-F4-05-OBSERVABILIDADE-ROLLBACK-E-AUDITORIA-FINAL.md](./EPIC-F4-05-OBSERVABILIDADE-ROLLBACK-E-AUDITORIA-FINAL.md) |

## Dependencias entre Epicos

- `EPIC-F4-01`: depende da conclusao de `F3`
- `EPIC-F4-02`: depende de `EPIC-F4-01`
- `EPIC-F4-03`: depende de `EPIC-F4-02`
- `EPIC-F4-04`: depende de `EPIC-F4-03`
- `EPIC-F4-05`: depende de `EPIC-F4-04`

## Escopo desta Fase

### Dentro
- runner de backfill, precedencia e idempotencia
- relatorio de reconciliacao e fechamento `manual_reconciled`
- criterio de fallback e amarracao aos artefatos operacionais existentes
- retirada do heuristico residual e pacote final de auditoria

### Fora
- novas superficies analiticas fora de `/dashboard/leads/*`
- redesign de UX
- rebaseline estrutural da arvore `DL2`

## Definition of Done da Fase
- [ ] backfill e reconciliacao executam sem duplicidade e com artefatos rastreaveis
- [ ] o protocolo de fallback via bronze esta definido e conectado aos artefatos operacionais existentes
- [ ] residuos heuristicos, rollback e evidencias finais estao fechados
