---
doc_id: "F1_FRAMEWORK2_0_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
audit_gate: "hold"
---

# Epicos - FRAMEWORK2.0 / F1 - HARMONIZACAO E RENOMEACAO

## Objetivo da Fase

Eliminar ruido normativo no framework comum, renomear artefatos para uma
convencao funcional e consolidar as regras hoje duplicadas ou dispersas.

## Gate de Saida da Fase

Todos os artefatos de `PROJETOS/COMUM/` usam a convencao nova, os projetos
ativos apontam para os nomes novos, a regra `backfilled` esta documentada e o
template de fase possui checklist de transicao de gate.

## Estado do Gate de Auditoria

- gate_atual: `hold`
- ultima_auditoria: `F1-R01`

## Checklist de Transicao de Gate

### `not_ready -> pending`
- [x] todos os epicos estao `done`
- [x] todas as issues filhas estao `done`
- [x] DoD da fase foi revisado

### `pending -> hold/approved`
- [x] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [x] `AUDIT-LOG.md` foi atualizado
- [x] veredito e estado do gate estao coerentes

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Renomeacao para Convencao de Prefixo | Renomear `PROJETOS/COMUM/` e atualizar referencias obrigatorias. | nenhuma | done | [EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md](./EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md) |
| EPIC-F1-02 | Deprecacao do Legado | Retirar o legado duplicado do caminho de leitura canonica. | EPIC-F1-01 | done | [EPIC-F1-02-DEPRECACAO-DO-LEGADO.md](./EPIC-F1-02-DEPRECACAO-DO-LEGADO.md) |
| EPIC-F1-03 | Unificacao de Responsabilidades e Eliminacao de Drift | Consolidar regras, links e referencias normativas. | EPIC-F1-01 | done | [EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md](./EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md) |
| EPIC-F1-04 | Integracao de PROMPT-PLANEJAR-FASE | Registrar a decisao estrutural sobre o prompt de planejamento e alinhar a sessao correspondente. | EPIC-F1-01 | done | [EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md](./EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md) |
| EPIC-F1-05 | Regra Operacional para Backfilled | Fechar a lacuna de intakes retroativos. | EPIC-F1-01 | done | [EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md](./EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md) |
| EPIC-F1-06 | Checklist de Transicao de Gate | Levar o checklist de gate para o template canonico de fase. | EPIC-F1-01 | done | [EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md](./EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma
- `EPIC-F1-02`: depende de `EPIC-F1-01`
- `EPIC-F1-03`: depende de `EPIC-F1-01`
- `EPIC-F1-04`: depende de `EPIC-F1-01`
- `EPIC-F1-05`: depende de `EPIC-F1-01`
- `EPIC-F1-06`: depende de `EPIC-F1-01`

## Escopo desta Fase

### Dentro

- renomear artefatos comuns
- atualizar referencias em projetos ativos
- consolidar regras de intake, scrum e auditoria
- registrar decisao sobre o prompt de planejamento

### Fora

- mudar escopo de projetos ativos
- criar automacao alem de Markdown

## Definition of Done da Fase

- [x] todos os artefatos de `PROJETOS/COMUM/` seguem a convencao nova
- [x] referencias antigas em projetos ativos foram corrigidas
- [x] `source_mode: backfilled` possui regra operacional
- [x] template de fase inclui checklist de transicao de gate
