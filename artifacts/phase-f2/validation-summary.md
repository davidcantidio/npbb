# Phase F2 Validation Summary

## Estado Atual

Decision atual: `hold`.

Justificativa atual: a estrutura documental e os suportes operacionais da Fase 2 foram criados, mas a migracao de banco e suas validacoes ainda nao foram executadas.

## Gate da Fase

- Contagem identica de `lead`, `evento` e `usuario`: pendente (requer acesso a ambos os bancos).
- `alembic upgrade head` sem erros: pendente.
- Validacao de integridade relacional e leituras essenciais: suites verdes em ambiente de teste (17 passed em 2026-04-13).

## Status dos Epicos

| Epic ID | Status | Evidencia |
|---|---|---|
| `EPIC-F2-01` | `todo` | `artifacts/phase-f2/epic-f2-01-dump-e-restore-supabase.md` |
| `EPIC-F2-02` | `partial` | `artifacts/phase-f2/epic-f2-02-validacao-integridade-dados.md` |

## Rollback de Referencia

- Manter Supabase como fonte de verdade.
- Bloquear cutover e descartar destino local se a validacao falhar antes da reabertura de escrita.
