---
doc_id: "SPRINT-F2-02.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# SPRINT-F2-02

## Objetivo da Sprint

Executar a recarga controlada do Supabase com os dados locais e concluir a
validacao de integridade e rollback da fase de dados.

## Capacidade
- story_points_planejados: 8
- issues_planejadas: 2
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F2-02-001 | Implementar recarga controlada de dados no Supabase | 5 | done | [ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md](../issues/ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md) |
| ISSUE-F2-02-002 | Validar integridade pos-carga e procedimento de rollback | 3 | todo | [ISSUE-F2-02-002-Validar-Integridade-Pos-Carga-e-Procedimento-de-Rollback.md](../issues/ISSUE-F2-02-002-Validar-Integridade-Pos-Carga-e-Procedimento-de-Rollback.md) |
| ISSUE-F2-02-003 | Endurecer contratos e atomicidade da recarga no Supabase | 3 | done | [ISSUE-F2-02-003-Endurecer-Contratos-e-Atomicidade-da-Recarga-no-Supabase.md](../issues/ISSUE-F2-02-003-Endurecer-Contratos-e-Atomicidade-da-Recarga-no-Supabase.md) |
| ISSUE-F2-02-004 | Bloquear prontidao quando DATABASE_URL nao for o Supabase alvo | 3 | done | [ISSUE-F2-02-004-Bloquear-Prontidao-Quando-DATABASE_URL-Nao-For-o-Supabase-Alvo.md](../issues/ISSUE-F2-02-004-Bloquear-Prontidao-Quando-DATABASE_URL-Nao-For-o-Supabase-Alvo.md) |

## Riscos e Bloqueios

- esta e a sprint de maior risco operacional do projeto
- qualquer falha sem backup utilizavel bloqueia o cutover final

## Encerramento
- decisao: pendente
- observacoes: a sprint so fecha quando o Supabase refletir os dados locais e o rollback continuar viavel
