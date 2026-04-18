# Task 6 — Rastreabilidade: linha do ficheiro original até ao Gold

**Prioridade:** P2

## Problema

O `row_index` no Silver é derivado de `enumerate(data_rows)` após remover preâmbulo/cabeçalho, não da linha física do ficheiro original. A exportação Silver → CSV pode consultar `LeadSilver` **sem `ORDER BY`**, tornando a ordem não determinística. A UI mostra `source_row` no relatório Gold como referência operacional, mas **não corresponde de forma estável** à planilha original (ex.: XLSX com várias linhas de preâmbulo).

## Escopo

- `backend/app/services/lead_mapping.py` — `mapear_batch` (persistência de índice / metadados de origem)
- `backend/app/services/lead_pipeline_service.py` — `materializar_silver_como_csv` (`ORDER BY LeadSilver.row_index` ou chave estável)
- Modelos `LeadSilver` / `LeadBatch` se necessário para `source_file`, `source_sheet`, `source_row_original`
- `frontend/src/pages/leads/PipelineStatusPage.tsx` — alinhar labels com semântica real após correção

## Critérios de aceite

1. Cada linha Silver (e relatório Gold) permite mapear para **ficheiro + folha + linha original** (ou equivalente documentado).
2. Materialização Silver → CSV usa ordem **determinística** (ex.: `ORDER BY row_index` ou chave composta estável).
3. Teste de regressão: XLSX com preâmbulo + linhas conhecidas + rejeição controlada no Gold — número mostrado alinha com a linha física esperada.

## Plano de verificação

- Fixture com preâmbulo de 8 linhas; comparar linha exibida na UI com linha física no Excel/CSV de teste.
- Teste automatizado que falharia no comportamento antigo se exigir igualdade exacta de `source_row_original`.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/fullstack-guardian/SKILL.md](.claude/skills/fullstack-guardian/SKILL.md) — modelo de dados e UI alinhados à mesma semântica de linha de origem.
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — `lead_mapping`, `lead_pipeline_service`, migrações de colunas.
- [.claude/skills/postgres-pro/SKILL.md](.claude/skills/postgres-pro/SKILL.md) — `ORDER BY` estável, índices para ordenação em exports.
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md) — labels e tooltips em `PipelineStatusPage` coerentes com o backend.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — regressão com XLSX de preâmbulo e asserts de `source_row_original`.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task6.md`** com:

1. **Resumo** dos campos novos, semântica de `row_index` vs linha física e impacto em relatórios Gold.
2. **Lista de ficheiros** tocados (modelos, serviços, frontend, migrações).
3. **Diffs / revisão**: `git diff` por componente, notas sobre dados existentes (backfill opcional) e compatibilidade de API com clientes antigos.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **A rastreabilidade por linha se perde do arquivo original até o Gold**; **Próximos passos** (quick wins: ORDER BY, preservar source_row_original).
