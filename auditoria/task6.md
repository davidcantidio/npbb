# Task 6 — Armazenamento: binários Bronze e snapshots ETL (storage + TTL)

**Prioridade:** P1

## Problema

O Bronze guarda o ficheiro bruto em `LargeBinary` (`lead_batches`); o preview ETL persiste JSON grande (`approved_rows_json`, `rejected_rows_json`, `dq_report_json`). Isto pressiona **memória, I/O, backups e custo**, especialmente com ficheiros grandes e timeouts já elevados no cliente.

## Escopo

- Modelo `LeadBatch` / migração — referência a object storage (URL + checksum) em vez de blob inline (estratégia faseada aceitável)
- `LeadImportEtlPreviewSession` / repositório — snapshots resumidos + artefactos detalhados em storage temporário com **TTL**
- Infra: variáveis de ambiente, cliente S3/R2/Azure Blob (conforme stack do projecto)
- Política de retenção documentada para operação

## Critérios de aceite

1. Plano de rollout: fase 1 pode ser “novos uploads usam storage; antigos mantêm blob” com job de migração opcional.
2. Métricas ou queries documentadas para tamanho médio de `lead_batches` / sessões ETL antes e depois.
3. Nenhuma regressão nos fluxos de preview e commit ETL nos testes existentes.

## Plano de verificação

- Testes de integração com storage mock ou MinIO local.
- Benchmark simples (opcional) documentado no handoff.

## Skills recomendadas (acionar na execução)

- [.claude/skills/cloud-architect/SKILL.md](.claude/skills/cloud-architect/SKILL.md)
- [.claude/skills/devops-engineer/SKILL.md](.claude/skills/devops-engineer/SKILL.md)
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md)
- [.claude/skills/postgres-pro/SKILL.md](.claude/skills/postgres-pro/SKILL.md)
- [.claude/skills/database-optimizer/SKILL.md](.claude/skills/database-optimizer/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task6.md`** (credenciais, buckets, políticas IAM — sem secrets no repo).

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Arquitetura de armazenamento e parsing tende a doer com arquivo grande**; **Priorização final** (item 6).
