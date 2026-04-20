# Task 5 — Batch Bronze: entidade pai (`ImportSession` / `UploadGroup`)

**Prioridade:** P1

## Problema

Cada ficheiro no modo batch torna-se um `LeadBatch` independente; o workspace multiplica artefactos, contadores por linha e estados de pipeline por `batch_id`. Isto escala em **fricção operacional** e dificulta tratar a importação como **uma operação única** com auditoria consolidada.

## Escopo

- Modelo de domínio + migração: entidade pai (nome acordado: `ImportSession`, `UploadGroup`, etc.) ligada a N `LeadBatch`
- [frontend/src/pages/leads/importacao/batch/](frontend/src/pages/leads/importacao/batch/) — workspace, resumo e navegação para agregar progresso
- Backend: routers/serviços de criação de lote batch alinhados à nova chave estrangeira
- Migração de dados existentes (opcional: sessão sintética por workspace legado)

## Critérios de aceite

1. API e UI expõem **um identificador de sessão de importação** com estado agregado (ex.: N lotes, M concluídos, falhas).
2. `LeadBatch` permanece unidade técnica; a experiência principal reporta-se à **sessão pai**.
3. Testes de regressão do batch upload e mapeamento unificado actualizados.

## Plano de verificação

- Testes E2E ou integração que cobrem upload de múltiplos ficheiros e leitura do resumo agregado.
- Documentação curta do novo ID na UI (copy para operadores).

## Skills recomendadas (acionar na execução)

- [.claude/skills/architecture-designer/SKILL.md](.claude/skills/architecture-designer/SKILL.md)
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md)
- [.claude/skills/postgres-pro/SKILL.md](.claude/skills/postgres-pro/SKILL.md)
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md)
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task5.md`** (destacar migrações e impacto em relatórios existentes).

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Batch Bronze escala a fricção operacional junto com o volume**; **Priorização final** (item 5).
