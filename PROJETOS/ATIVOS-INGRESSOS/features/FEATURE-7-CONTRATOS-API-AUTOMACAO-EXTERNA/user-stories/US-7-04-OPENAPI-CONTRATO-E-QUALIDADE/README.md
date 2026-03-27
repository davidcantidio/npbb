---
doc_id: "US-7-04-OPENAPI-CONTRATO-E-QUALIDADE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-7"
decision_refs: []
---

# US-7-04 - OpenAPI, contrato e qualidade

## User Story

**Como** consumidor da API (integrador ou engenheiro),
**quero** documentacao OpenAPI (ou equivalente oficial) e testes de contrato,
**para** integrar com previsibilidade, entender erros e codigos de resposta, e confiar na semantica de idempotencia documentada.

## Feature de Origem

- **Feature**: FEATURE-7 - Contratos de API para automacao externa (ticketeiras)
- **Comportamento coberto**: criterios de aceite da feature sobre OpenAPI/payloads/erros/codigos, idempotencia documentada, e estrategia sec. 6.4 (contratos, seguranca, idempotencia, carga negativa) mais observabilidade (correlation_id, logs por integrador).

## Contexto Tecnico

- Publicar ou gerar artefato OpenAPI alinhado as rotas entregues na US-7-03; incluir esquemas, respostas de erro e descricao das chaves de idempotencia e comportamento em reenvio.
- Contract tests e cenarios de carga negativa validam o contrato e reduzem regressao.
- Logs estruturados com `correlation_id` e identificacao do integrador, coerentes com impacts de observabilidade do manifesto.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel (planejamento; TDD na desdobramento em tasks).
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** as operacoes de ingestao acordadas implementadas na US-7-03,
  **when** um desenvolvedor consultar o artefato de contrato,
  **then** encontra descricao de paths, request/response bodies, codigos HTTP e modelos de erro reutilizaveis.
- **Given** a politica de idempotencia definida em produto,
  **when** ler a documentacao,
  **then** esta explicito quais cabecalhos ou campos funcionam como chave de deduplicacao e qual o efeito de reenvio com a mesma chave.
- **Given** a suite de contract tests e testes de carga negativa,
  **when** executada em CI ou localmente,
  **then** falha quando o comportamento publico divergir do contrato ou quando entradas malformadas nao forem rejeitadas como esperado.
- **Given** um request autenticado,
  **when** processado,
  **then** logs ou traces permitem correlacionar por `correlation_id` e identificar o integrador sem vazar segredos.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — OpenAPI e documentacao de idempotencia
- [TASK-2.md](./TASK-2.md) — Contract tests e carga negativa
- [TASK-3.md](./TASK-3.md) — Observabilidade (`correlation_id`, integrador em logs)
- [TASK-4.md](./TASK-4.md) — Revisao de seguranca do contrato exposto

## Arquivos Reais Envolvidos

- `backend/` OpenAPI, testes de contrato, configuracao de logging
- Documentacao gerada ou ficheiros estaticos de API (caminhos exatos nas tasks)
- [FEATURE-7.md](../../FEATURE-7.md)

## Artefato Minimo

- Contrato publicado verificavel, testes de contrato e negativos passando, e linha de base de observabilidade para suporte a integradores.

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
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-7-03](../US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL/README.md) deve estar `done` (rotas e semantica estaveis)
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [FEATURE-7](../../FEATURE-7.md)
