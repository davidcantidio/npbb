---
doc_id: "F3_FRAMEWORK2_0_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK2.0 / F3 - PROMPTS DE SESSAO

## Objetivo da Fase

Cobrir o fluxo canonico completo em chat interativo, do intake a auditoria,
incluindo remediacao guiada de monolito.

## Gate de Saida da Fase

Todos os prompts de sessao existem, seguem um protocolo HITL coerente e estao
listados em `SESSION-MAPA.md`.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold/approved`
- [ ] existe `RELATORIO-AUDITORIA-F3-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] veredito e estado do gate estao coerentes

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Registro e Validacao dos Prompts Antecipados | Formalizar o mapa de sessao e revisar os prompts ja existentes. | F1 done | todo | [EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md](./EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md) |
| EPIC-F3-02 | SESSION-CRIAR-PRD | Criar a sessao de intake aprovado para PRD. | EPIC-F3-01 | todo | [EPIC-F3-02-SESSION-CRIAR-PRD.md](./EPIC-F3-02-SESSION-CRIAR-PRD.md) |
| EPIC-F3-03 | SESSION-IMPLEMENTAR-ISSUE | Criar a sessao de execucao de issue com HITL. | EPIC-F3-01 | todo | [EPIC-F3-03-SESSION-IMPLEMENTAR-ISSUE.md](./EPIC-F3-03-SESSION-IMPLEMENTAR-ISSUE.md) |
| EPIC-F3-04 | SESSION-AUDITAR-FASE | Criar a sessao de auditoria de fase com follow-up guiado. | EPIC-F3-01, EPIC-F2-02, EPIC-F2-03 | todo | [EPIC-F3-04-SESSION-AUDITAR-FASE.md](./EPIC-F3-04-SESSION-AUDITAR-FASE.md) |
| EPIC-F3-05 | SESSION-REFATORAR-MONOLITO | Criar a sessao de mini-projeto de remediacao estrutural. | EPIC-F3-01, EPIC-F2-03 | todo | [EPIC-F3-05-SESSION-REFATORAR-MONOLITO.md](./EPIC-F3-05-SESSION-REFATORAR-MONOLITO.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: depende de `F1` concluida
- `EPIC-F3-02`: depende de `EPIC-F3-01`
- `EPIC-F3-03`: depende de `EPIC-F3-01`
- `EPIC-F3-04`: depende de `EPIC-F3-01`, `EPIC-F2-02` e `EPIC-F2-03`
- `EPIC-F3-05`: depende de `EPIC-F3-01` e `EPIC-F2-03`

## Escopo desta Fase

### Dentro

- mapa final de prompts de sessao
- prompts para PRD, implementacao, auditoria e refatoracao
- alinhamento dos prompts de sessao ao estado pos-F1 e pos-F2

### Fora

- automacao de escolha de prompt
- interfaces alem de Markdown

## Definition of Done da Fase

- [ ] `SESSION-MAPA.md` lista todos os prompts de sessao
- [ ] todos os prompts param antes de qualquer gravacao
- [ ] auditoria e remediacao de monolito estao cobertas em chat
