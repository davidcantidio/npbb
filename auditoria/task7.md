# Task 7 — Ingestão assíncrona: fila, progresso incremental e retomada

**Prioridade:** P2

## Problema

Parsing, preview e operações pesadas permanecem predominantemente **síncronos**, acoplando UX a I/O e levando a timeouts longos (ex.: 120s no cliente). Falta desenho de **fila**, progresso incremental e retomada alinhados ao volume futuro.

## Escopo

- Encadeamento backend: enfileirar jobs para preview ETL e/ou materialização Bronze pesada (tecnologia alinhada ao stack: Celery, RQ, Dramatiq, ou worker dedicado)
- API: endpoints de **status** + `job_id` correlacionável
- Frontend: substituir ou complementar polling síncrono por progresso de job (SSE/WebSocket/polling lento sobre estado de job)
- [lead_pipeline/](lead_pipeline/) e [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py) se o Gold/preview compartilhar padrões

## Critérios de aceite

1. Operação piloto (ex.: preview ETL de ficheiro grande) **não bloqueia** a thread de request até ao fim do parsing; o cliente obtém estado de progresso.
2. Falha ou restart do worker: comportamento documentado (retry idempotente, DLQ ou estado `failed` recuperável).
3. Testes de integração ou contract tests para o fluxo assíncrono mínimo.

## Plano de verificação

- Teste de carga leve local documentado no handoff.
- Simulação de falha a meio do job e verificação de estado final.

## Skills recomendadas (acionar na execução)

- [.claude/skills/architecture-designer/SKILL.md](.claude/skills/architecture-designer/SKILL.md)
- [.claude/skills/devops-engineer/SKILL.md](.claude/skills/devops-engineer/SKILL.md)
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md)
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md)
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task7.md`**.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Melhorias estruturais e arquiteturais** (ingestão assíncrona); **Priorização final** (item 7).
