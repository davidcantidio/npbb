---
doc_id: "US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-7"
decision_refs: []
---

# US-7-01 - Modelo de idempotencia e chaves externas

## User Story

**Como** engenheiro de plataforma,
**quero** persistir chaves de deduplicacao e referencias externas alinhadas ao modelo de recebimento (FEATURE-4),
**para** que reenvios da mesma mensagem ou fonte sejam tratados de forma segura antes e durante a exposicao da API de ingestao.

## Feature de Origem

- **Feature**: FEATURE-7 - Contratos de API para automacao externa (ticketeiras)
- **Comportamento coberto**: modelagem e migrations para idempotencia, chaves externas e estruturas auxiliares acordadas no manifesto sec. 6.1 e 7 (camada Banco).

## Contexto Tecnico

- Depende de [FEATURE-2](../../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md), [FEATURE-3](../../../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md) e [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md) para entidades de dominio e recebimento ja existentes.
- A API publica (US-7-03) consumira estas estruturas; o contrato documental de idempotencia sera detalhado na US-7-04 em conjunto com OpenAPI.
- Fora de escopo: skill OpenClaw no repositorio, inbox nativo (manifesto FEATURE-7 sec. 2).

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel (planejamento; TDD na desdobramento em tasks).
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** o desenho da FEATURE-7 (idempotencia, chaves externas, filas se necessario),
  **when** as migrations forem aplicadas,
  **then** existem estruturas persistidas que permitem registrar tentativas de ingestao e chaves de deduplicacao por integrador ou mensagem, sem quebrar o modelo de FEATURE-4.
- **Given** uma chave de idempotencia ja consumida com sucesso,
  **when** o mesmo integrador reenviar a mesma chave,
  **then** o esquema suporta resposta idempotente ou rejeicao explicita conforme regra definida na camada de aplicacao (US-7-03), com trilha minimamente auditavel.
- **Given** referencias a artefatos ou IDs externos de ticketeiras,
  **when** forem persistidas,
  **then** o modelo permanece alinhado a placeholders LGPD onde o PRD sec. 7 ainda nao fechou storage de binarios.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — Migration: registos de idempotencia para ingestao externa
- [TASK-2.md](./TASK-2.md) — Migration: referencias externas (ticketeira) sem binarios
- [TASK-3.md](./TASK-3.md) — Modelos SQLModel e import em `alembic/env.py`
- [TASK-4.md](./TASK-4.md) — Validacao migrate/revert e notas de integracao para US-7-03

## Arquivos Reais Envolvidos

- `backend/` migrations Alembic e modelos SQLModel (caminhos exatos nas tasks)
- [FEATURE-7.md](../../FEATURE-7.md)

## Artefato Minimo

- Esquema e migrations revisaveis que suportem autenticacao de integrador (US-7-02) e endpoints de ingestao (US-7-03) sem retrabalho destrutivo.

## Handoff para Revisao Pos-User Story

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [FEATURE-7](../../FEATURE-7.md)
- [FEATURE-2](../../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md)
- [FEATURE-3](../../../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md)
- [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: nenhuma (primeira da cadeia de API externa nesta feature)
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [FEATURE-7](../../FEATURE-7.md)
