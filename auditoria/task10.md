# Task 10 — Observabilidade: métricas, logs e lotes presos

**Prioridade:** P2 (escopo pode incluir itens P1 ligados a alertas de pipeline)

## Problema

Existem identificadores úteis (`batch_id`, `session_token`) e estado de pipeline na base, mas falta **correlação operacional completa**: contagem de rejeições por motivo, duração por etapa, request-id/job-id distribuído, e alertas para lotes `pending` **sem heartbeat** recente. Isto dificulta diagnóstico em produção e prolonga incidentes.

## Escopo

- Instrumentação em serviços de import, ETL preview/commit, `lead_pipeline_service` (Gold)
- Métricas (Prometheus/OpenTelemetry ou o que o projecto já usar) e logs estruturados com `batch_id` / `session_token`
- Regras de alerta ou dashboard mínimo para: lotes pending sem progresso, taxa de rejeição, latência por etapa

## Critérios de aceite

1. Pelo menos um **dashboard ou consulta** operacional documentada com as métricas-chave do relatório.
2. Logs estruturados nas transições de estado do pipeline (início/fim/erro por etapa).
3. Contadores de linhas rejeitadas **por motivo** no preview ETL (ou agregação exportável).
4. Alerta ou runbook para lote `pending` acima de limiar temporal (definir limiar).

## Plano de verificação

- Verificar em ambiente de staging que uma importação gera trilho de logs/métricas pesquisável.
- Simular lote preso e confirmar que o alerta ou query de detecção dispara.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/monitoring-expert/SKILL.md](.claude/skills/monitoring-expert/SKILL.md) — métricas, logs estruturados, dashboards e alertas.
- [.claude/skills/sre-engineer/SKILL.md](.claude/skills/sre-engineer/SKILL.md) — SLIs/SLOs para jobs pendentes e runbooks operacionais.
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — instrumentação no pipeline e nos serviços ETL.
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md) — se expuser telemetria ou estados enriquecidos na UI.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes de que logs/métricas não quebram em import mínimo.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task10.md`** com:

1. **Resumo** das métricas/logs adicionados, nomes de séries/campos e alertas configurados.
2. **Lista de ficheiros** tocados e dependências novas (ex.: biblioteca OTEL/Prometheus).
3. **Diffs / revisão**: comandos `git diff` por serviço; links ou queries de dashboard; variáveis de ambiente para sampling/nível de log.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secções **Lacunas de teste e observabilidade**, **Observabilidade e operação** (checklist), **Próximos passos** (logs/metrics por batch_id e session_token).
