---
doc_id: "US-5-02-SERVICO-E-API-EMISSAO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-5"
decision_refs: []
---

# US-5-02 - Servico e API de emissao

## User Story

Como operador ou integracao autorizada,
quero emitir ingressos internos unitarios via API (individual ou em lote) com idempotencia e controle de acesso,
para que a emissao seja segura, repetivel e rastreavel sem vazar dados sensiveis em logs.

## Feature de Origem

- **Feature**: FEATURE-5 (Emissao interna unitaria com QR)
- **Comportamento coberto**: regras de negocio de emissao no backend; RBAC; tratamento de duplicidade; LGPD em trilhas e logs (criterio 4 da feature); integracao com email de saida quando aplicavel (PRD 2.7), sem entregar validador no portao.

## Contexto Tecnico

- Pressupoe **US-5-01** concluida (modelo persistido).
- Endpoints novos ou evolucao de `backend/app/routers/ingressos.py` (ou router dedicado), alinhados a observabilidade com `correlation_id` (manifesto sec. 7).
- Logs e auditoria: nao registrar payload completo de QR ou dados pessoais em claro quando a politica interna exigir mascaramento.

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir em `TASK-*.md`.
- **Green**: a definir em `TASK-*.md`.
- **Refactor**: a definir em `TASK-*.md`.

## Criterios de Aceitacao (Given / When / Then)

- **Given** um operador com permissao adequada e categoria em modo interno com QR,
  **when** solicita emissao para um destinatario elegivel,
  **then** o sistema persiste exatamente uma emissao unitaria e retorna identificador unico coerente com o modelo.
- **Given** uma repeticao de requisicao equivalente (mesmo escopo de idempotencia documentado),
  **when** o cliente reenvia o pedido,
  **then** o sistema nao cria duplicata indevida e comportamento idempotente fica documentado na API.
- **Given** um usuario sem permissao ou escopo inadequado,
  **when** tenta emissao,
  **then** a operacao e negada sem vazamento de dados sensiveis na resposta ou em logs padrao.
- **Given** emissao bem-sucedida ou falha de negocio,
  **when** trilhas de auditoria sao consultadas,
  **then** e possivel correlacionar o evento sem armazenar payload sensivel integral em claro, conforme politica LGPD acordada.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1 — Servico de dominio de emissao unitaria interna](TASK-1.md)
- [TASK-2 — Endpoints HTTP, schemas e OpenAPI para emissao](TASK-2.md)
- [TASK-3 — RBAC e negacao sem vazamento na emissao](TASK-3.md)
- [TASK-4 — Idempotencia documentada e sem duplicata indevida](TASK-4.md)
- [TASK-5 — Auditoria, logs e correlacao sem payload sensivel](TASK-5.md)

## Arquivos Reais Envolvidos

- `backend/app/routers/ingressos.py` (ou novo router de emissao)
- Servicos de dominio em `backend/app/` (use cases de emissao)
- `backend/tests/` (contratos de API e regras de unicidade/RBAC)

## Artefato Minimo

- API documentada (OpenAPI existente do FastAPI) com operacoes de emissao; testes cobrindo unicidade, autorizacao e idempotencia onde declarada.

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

- [FEATURE-5](../../FEATURE-5.md)
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) deve estar `done`
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
