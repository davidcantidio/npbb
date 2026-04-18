# Task 4 — Pipeline Gold: durabilidade, retomada e lotes presos

**Prioridade:** P1

## Problema

O Gold executa como **background task** no mesmo processo da API, com estado em `lead_batches.pipeline_status` / `pipeline_progress`. Não há fila durável, DLQ nem retomada automática após queda de processo, deploy ou recycle. O frontend faz **polling** frequente (~1,5 s). Lotes podem ficar `pending` ou com progresso obsoleto sem reentrega automática da tarefa.

## Escopo

- `backend/app/services/lead_pipeline_service.py` — `executar_pipeline_gold`, enfileiramento e finalização de estado
- `frontend/src/pages/leads/PipelineStatusPage.tsx` e `frontend/src/services/leads_import.ts` — UX de estado e polling (após decisão de backend)
- Opções: fila externa (RQ/Celery/SQS/RabbitMQ) **ou** fase intermédia: lease/heartbeat, timeout de job, endpoint administrativo de **retry seguro**, recuperação de lote travado

## Critérios de aceite

1. Comportamento definido para: processo morto a meio do pipeline, worker reiniciado, falha após parte do progresso persistido.
2. Não depender apenas de “esperar o mesmo processo” para concluir o lote; há **reentrega** ou **ação operacional clara** (retry idempotente documentado).
3. Estados terminais e de erro distinguíveis na API/UI (incl. distinção de “em execução com heartbeat” vs “preso”).
4. Teste que simula interrupção (ou documentação de teste manual mínima) + critério de aceite para não regressão.

## Plano de verificação

- Cenário manual: Silver pronto → `executar-pipeline` → matar processo durante `normalize_rows` → verificar estado e capacidade de retomada/retry.
- Se fila durável: teste de redelivery após `nack` simulado.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/architecture-designer/SKILL.md](.claude/skills/architecture-designer/SKILL.md) — escolha entre fila durável, lease/heartbeat ou híbrido; trade-offs operacionais.
- [.claude/skills/fullstack-guardian/SKILL.md](.claude/skills/fullstack-guardian/SKILL.md) — backend assíncrono + UI de estado e polling seguros.
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — tarefas em background, endpoints de retry/admin e contratos de estado.
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md) — `PipelineStatusPage`, hooks de polling e UX de erro/retomada.
- [.claude/skills/devops-engineer/SKILL.md](.claude/skills/devops-engineer/SKILL.md) — se integrar fila/worker externo (CI, env vars, healthchecks).
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes de interrupção/retry e regressão de estados do lote.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task4.md`** com:

1. **Resumo** do desenho escolhido (fila vs mitigação local), estados novos e comportamento em falha de processo.
2. **Lista de ficheiros** tocados no backend e frontend, variáveis de ambiente novas e alterações de infra (se houver).
3. **Diffs / revisão**: `git diff` por área (`lead_pipeline_service`, routers, `PipelineStatusPage`), notas para deploy (ordem: migração → worker → API) e riscos de lotes já `pending` em produção.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **O Gold roda como background task em processo, sem fila durável, sem DLQ e sem retomada automática**; **Próximos passos** → correções de alto impacto (job durável / heartbeat).
