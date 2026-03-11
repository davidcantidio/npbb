---
doc_id: "SPRINT-F2-01.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
---

# SPRINT-F2-01

## Objetivo da Sprint

Implementar fluxo CPF-first, validação, registro de conversão e bloqueio de CPF duplicado.

## Capacidade

- story_points_planejados: 13
- issues_planejadas: 5
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F2-01-001 | Rota e página landing com contexto de ativação | 3 | todo | [ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md](../issues/ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md) |
| ISSUE-F2-01-002 | Fluxo CPF-first e validação de dígito | 3 | todo | [ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md](../issues/ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md) |
| ISSUE-F2-01-003 | Testes Playwright do fluxo CPF-first | 2 | todo | [ISSUE-F2-01-003-TESTES-PLAYWRIGHT-CPF-FIRST.md](../issues/ISSUE-F2-01-003-TESTES-PLAYWRIGHT-CPF-FIRST.md) |
| ISSUE-F2-02-001 | Extensão POST /leads com ativacao_id e registro de conversão | 3 | todo | [ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md](../issues/ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md) |
| ISSUE-F2-02-002 | Bloqueio CPF duplicado e integração frontend | 2 | todo | [ISSUE-F2-02-002-BLOQUEIO-CPF-DUPLICADO.md](../issues/ISSUE-F2-02-002-BLOQUEIO-CPF-DUPLICADO.md) |

## Riscos e Bloqueios

- ISSUE-F2-01-002 depende de F2-02-001 para contrato POST (pode ser paralelo com mocks)
- Ordem sugerida: F2-02-001 primeiro (backend), depois F2-01-001, F2-01-002, F2-02-002, F2-01-003

## Encerramento

- decisao: pendente
- observacoes: respeitar GOV-SPRINT-LIMITES (max 5 issues, 13 SP)
