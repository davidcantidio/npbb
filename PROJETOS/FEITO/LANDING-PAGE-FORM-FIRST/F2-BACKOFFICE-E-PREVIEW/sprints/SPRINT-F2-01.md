---
doc_id: "SPRINT-F2-01.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# SPRINT-F2-01

## Objetivo da Sprint

Ajustar o backoffice e o modo preview para refletir o novo layout form-only: remover `hero_image_url` do produto, atualizar mensagem de customizacao e adaptar preview com badge discreto e sem metadados extras.

## Capacidade

- story_points_planejados: 9
- issues_planejadas: 4
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F2-01-001 | Remover hero_image_url do Painel | 2 | done | [ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md](../issues/ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md) |
| ISSUE-F2-01-002 | Atualizar Mensagem Customizacao | 1 | done | [ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md](../issues/ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md) |
| ISSUE-F2-02-001 | Adaptar Preview Form-Only | 3 | done | [ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md](../issues/ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md) |
| ISSUE-F2-02-002 | Mover Chips para Secao Colapsavel | 3 | cancelled | [ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md](../issues/ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md) |

## Riscos e Bloqueios

- remocao do campo hero_image_url exigiu schema estrito e migration para evitar contrato fantasma
- preview precisava permanecer fiel ao publicado sem reintroduzir metadados operacionais

## Encerramento

- decisao: concluida
- observacoes: backoffice, preview, payloads e banco foram alinhados ao layout form-only; a issue de chips foi cancelada por mudanca de produto.

## Navegacao Rapida

- [Epic F2-01](../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md)
- [Epic F2-02](../EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- `[[../issues/ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL]]`
- `[[../issues/ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO]]`
- `[[../issues/ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY]]`
- `[[../issues/ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL]]`
