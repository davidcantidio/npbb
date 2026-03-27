---
doc_id: "US-5-04-UI-EMISSAO-OPERACIONAL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-5"
decision_refs: []
---

# US-5-04 - UI operacional de emissao

## User Story

Como operador NPBB,
quero emitir e visualizar ingressos internos com QR a partir do fluxo em `/ingressos` (ou modulo dedicado acordado), com preview quando aplicavel,
para que o estado `qr_emitido` seja operavel na interface sem depender apenas da API.

## Feature de Origem

- **Feature**: FEATURE-5 (Emissao interna unitaria com QR)
- **Comportamento coberto**: segundo criterio de aceite da feature em versao MVP — layout/visual da categoria aplicado na geracao conforme especificacao funcional; refino avancado de template pode vir em US futura (manifesto sec. 4). Reforca explicitamente que **nao** ha validador no portao neste corte (criterio 5).

## Contexto Tecnico

- Baseline: `frontend/src/pages/IngressosPortal.tsx` e servicos `ingressos.ts` / `ingressos_admin.ts` (PRD 4.0).
- Depende de API de **US-5-02** e de payload/pre-visualizacao coerente com **US-5-03** quando o UI exibir QR ou resumo.
- Padrao visual alinhado ao restante do produto (PRD 2.6 design).

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir em `TASK-*.md` (por exemplo testes de componente ou E2E leves).
- **Green**: a definir em `TASK-*.md`.
- **Refactor**: a definir em `TASK-*.md`.

## Criterios de Aceitacao (Given / When / Then)

- **Given** permissao de operador e categoria interna com QR configurada,
  **when** o usuario conclui o fluxo de emissao para um destinatario,
  **then** a UI reflete estado `qr_emitido` e confirma sucesso com referencia ao identificador ou artefato previsto (sem expor dados desnecessarios).
- **Given** metadados de layout da categoria disponiveis no backend,
  **when** a emissao e solicitada pela UI,
  **then** o documento ou preview gerado aplica o layout basico da categoria conforme especificacao desta US (detalhes de template avancado podem ficar para backlog).
- **Given** um usuario sem permissao,
  **when** acessa rotas ou acoes de emissao,
  **then** a UI nao expoe controles de emissao ou recebe erro tratado de forma consistente.
- **Given** o escopo do PRD,
  **when** a US e considerada concluida,
  **then** nao ha funcionalidade de scanner ou validacao de uso unico no portao embutida nesta entrega.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1 — Cliente HTTP e tipos para emissao interna com QR](TASK-1.md)
- [TASK-2 — Entrada do fluxo operador e gating RBAC na superficie `/ingressos`](TASK-2.md)
- [TASK-3 — Fluxo de emissao ate sucesso com estado `qr_emitido`](TASK-3.md)
- [TASK-4 — Preview e layout basico da categoria na emissao](TASK-4.md)
- [TASK-5 — Testes automatizados e validacao final da US](TASK-5.md)

## Arquivos Reais Envolvidos

- `frontend/src/pages/IngressosPortal.tsx` (ou paginas/componentes novos)
- `frontend/src/services/ingressos.ts`, `frontend/src/services/ingressos_admin.ts`

## Artefato Minimo

- Fluxo de emissao utilizavel na superficie acordada com estados claros e aderencia ao contrato de API.

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
- Outras USs: [US-5-02](../US-5-02-SERVICO-E-API-EMISSAO/README.md) e [US-5-03](../US-5-03-CONTRATO-MINIMO-PAYLOAD-QR/README.md) devem estar `done`
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
