---
doc_id: "F2_FRAMEWORK2_0_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK2.0 / F2 - ANTI MONOLITH ENFORCEMENT

## Objetivo da Fase

Tornar o achado de monolito objetivo, mensuravel e operacional desde a auditoria
ate a abertura de intake de remediacao.

## Gate de Saida da Fase

Existe um spec com thresholds objetivos, o template de auditoria consome esse
spec e o prompt de monolito gera intake de remediacao valido.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

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
| EPIC-F2-01 | SPEC-ANTI-MONOLITO | Definir e calibrar thresholds objetivos por linguagem. | EPIC-F1-01 done | active | [EPIC-F2-01-SPEC-ANTI-MONOLITO.md](./EPIC-F2-01-SPEC-ANTI-MONOLITO.md) |
| EPIC-F2-02 | Metricas no Template de Auditoria | Levar complexidade estrutural e decision refs ao relatorio. | EPIC-F2-01 | active | [EPIC-F2-02-METRICAS-NO-TEMPLATE-DE-AUDITORIA.md](./EPIC-F2-02-METRICAS-NO-TEMPLATE-DE-AUDITORIA.md) |
| EPIC-F2-03 | PROMPT-MONOLITO-PARA-INTAKE | Transformar achado estrutural em intake de remediacao rastreavel. | EPIC-F2-01 | todo | [EPIC-F2-03-PROMPT-MONOLITO-PARA-INTAKE.md](./EPIC-F2-03-PROMPT-MONOLITO-PARA-INTAKE.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende do fechamento de `EPIC-F1-01`
- `EPIC-F2-02`: depende de `EPIC-F2-01`
- `EPIC-F2-03`: depende de `EPIC-F2-01`

## Escopo desta Fase

### Dentro

- spec anti-monolito
- calibracao minima em projeto ativo
- template de auditoria com metricas estruturais
- prompt de remediacao para intake

### Fora

- thresholds para outras linguagens
- automacao de coleta de metricas

## Definition of Done da Fase

- [ ] existe `SPEC-ANTI-MONOLITO.md`
- [ ] auditoria usa thresholds estruturais de forma explicita
- [ ] prompt de monolito produz intake valido
