---
doc_id: "US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-3"
decision_refs: []
---

# US-3-02 - API de configuracao, RBAC e exposicao dos modos canonicos

## User Story

**Como** consumidor do modulo de ativos (frontend ou integracao interna),
**quero** endpoints e contratos que permitam ler e alterar a configuracao de categorias por evento e obter os modos canonicos de fornecimento,
**para** que apenas perfis autorizados alterem configuracao sensivel (LGPD/operacao, PRD 2.6) e FEATURE-4/FEATURE-5 possam distinguir categoria e modo nas leituras.

## Feature de Origem

- **Feature**: FEATURE-3 — Categorias por evento e modos de fornecimento
- **Comportamento coberto**: API/backend (sec. 6.2 do manifesto); criterios de aceite de modos expostos, RBAC na alteracao de configuracao e validacao de modos.

## Contexto Tecnico

- Pressupoe modelo persistido entregue por [US-3-01](../US-3-01-MODELAGEM-PERSISTENCIA-E-DEFAULTS-LEGADO/README.md).
- Alinhar a rotas existentes em `backend/app/routers/ativos.py` ou extensao coerente (PRD 4.0).
- Respostas de erro 4xx claras para subset invalido ou violacao de permissao, conforme manifesto sec. 7.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um cliente autenticado com permissao de configuracao,
  **when** altera o subset de categorias habilitadas para um evento,
  **then** a persistencia reflete apenas categorias do trio inicial permitidas pela regra de negocio e a operacao e auditavel conforme estrategia definida na US de observabilidade ou task associada.
- **Given** um cliente sem permissao adequada,
  **when** tenta alterar configuracao por evento,
  **then** a API nega com resposta explicita (ex. 403) sem alterar dados.
- **Given** consumidores internos (ex. preparacao para FEATURE-4/5),
  **when** consultam contrato/listagem que inclui modo de fornecimento,
  **then** os dois valores canonicos (**interno emitido com QR** e **externo recebido**) estao disponiveis de forma estavel na API ou contrato interno acordado.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobrar em ate **5** tasks por US (`GOV-USER-STORY.md`) na etapa `SESSION-DECOMPOR-US-EM-TASKS.md`.

- [TASK-1 — Leitura de configuracao por evento e contrato dos modos canonicos](./TASK-1.md) (`T1`, `depends_on: []`)
- [TASK-2 — Escrita da configuracao de categorias por evento com validacao do trio inicial](./TASK-2.md) (`T2`, `depends_on: [T1]`)
- [TASK-3 — RBAC na escrita de configuracao por evento (403 sem efeitos colaterais)](./TASK-3.md) (`T3`, `depends_on: [T2]`)
- [TASK-4 — Suite de testes integrando criterios Given/When/Then da US-3-02](./TASK-4.md) (`T4`, `depends_on: [T1, T2, T3]`)

## Arquivos Reais Envolvidos

- `backend/app/routers/ativos.py` *(ou routers novos no mesmo padrao)*
- Servicos/casos de uso associados ao dominio de ativos
- `backend/tests/test_ativos_endpoints.py` *(ou equivalente apos evolucao)*

## Artefato Minimo

- API funcional com RBAC na escrita de configuracao e leitura estavel dos modos canonicos

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

- [Manifesto da feature](../../FEATURE-3.md)
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-3-01](../US-3-01-MODELAGEM-PERSISTENCIA-E-DEFAULTS-LEGADO/README.md) deve estar `done` antes da execucao
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
