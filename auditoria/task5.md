# Task 5 — Performance, memória e custo de armazenamento (import leads)

**Prioridade:** P1

## Problema

O desenho atual tende a: ler **ficheiro inteiro** em memória; guardar Bronze como **blob** na base; serializar previews ETL grandes em **JSON** em colunas de texto; no Gold, ler o CSV consolidado **todo** para lista em memória; persistência com padrões **row-by-row** / N+1 em partes do fluxo; frontend com **timeouts longos** e polling agressivo. Em lotes grandes e concorrência, isto pressiona RAM, tempo de resposta, tamanho de base e backups.

## Escopo

- `backend/app/services/imports/file_reader.py` — leitura de upload
- `backend/app/modules/leads_publicidade/application/etl_import/extract.py` e fluxo de preview
- Repositório / modelo de `lead_import_etl_preview_session` (snapshots)
- `backend/app/models/lead_batch.py` e persistência de `arquivo_bronze`
- `backend/app/services/lead_pipeline_service.py` — materialização e leitura do consolidado Gold
- `frontend/src/services/leads_import.ts` — timeouts e eventual ajuste após melhorias de backend

## Critérios de aceite

1. Plano de medição acordado (RSS, tempo de preview ETL, tamanho de linhas em `lead_batches` / `lead_import_etl_preview_session`, latência `executar-pipeline`) com baseline e meta ou “não piorar X%”.
2. Pelo menos **uma** melhoria concreta entregue por fase (ex.: streaming onde viável, leitura em chunks no Gold, inserts em batch, snapshot mais compacto, ou object storage para Bronze) com PRs separáveis.
3. Documentação curta para operadores sobre limites de tamanho de ficheiro recomendados enquanto migração não termina.

## Plano de verificação

- Benchmark com lote grande (ex.: ordem de 100k linhas, conforme ambiente) medindo memória e tempo.
- Consultas `pg_total_relation_size` antes/depois em cenário controlado (relatório cita estas métricas).

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — streaming, generators, uso de memória no backend.
- [.claude/skills/postgres-pro/SKILL.md](.claude/skills/postgres-pro/SKILL.md) — tamanho de tabelas, blobs e estratégias de armazenamento.
- [.claude/skills/database-optimizer/SKILL.md](.claude/skills/database-optimizer/SKILL.md) — batch inserts, índices e medição de `pg_total_relation_size`.
- [.claude/skills/typescript-pro/SKILL.md](.claude/skills/typescript-pro/SKILL.md) — cliente HTTP, timeouts e tipos no frontend.
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md) — ajustes de UX quando o backend ficar mais rápido ou assíncrono.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — benchmarks ou testes de carga leves automatizáveis.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task5.md`** com:

1. **Resumo** das otimizações, baseline vs depois (métricas registadas) e limites operacionais documentados.
2. **Lista de ficheiros** tocados (backend, frontend, migrações, scripts de benchmark).
3. **Diffs / revisão**: comandos por pasta (`file_reader`, `lead_pipeline_service`, `leads_import.ts`), impacto em disco/DB e flags de feature se existirem.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **O desenho atual faz IO e memória em excesso**; **Checklist técnico** → performance; **Mudanças estruturais** (storage externo, bulk upsert, polling).
