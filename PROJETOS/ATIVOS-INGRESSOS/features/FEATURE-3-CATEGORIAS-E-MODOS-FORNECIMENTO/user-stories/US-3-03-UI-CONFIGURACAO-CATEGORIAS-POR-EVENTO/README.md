---
doc_id: "US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "optional"
feature_id: "FEATURE-3"
decision_refs: []
---

# US-3-03 - UI de configuracao de categorias por evento

## User Story

**Como** operador do modulo de ativos,
**quero** configurar na interface quais categorias do catalogo inicial aplicam-se a cada evento (subset do trio),
**para** reduzir erro operacional e alinhar a operacao ao fluxo do PRD (passo 1: previsao por evento, diretoria, categoria e modo).

## Feature de Origem

- **Feature**: FEATURE-3 — Categorias por evento e modos de fornecimento
- **Comportamento coberto**: superficie UI (sec. 6.3 do manifesto); criterio de aceite de catalogo configuravel por evento com subset; reforco de RBAC na camada de apresentacao coerente com API.

## Contexto Tecnico

- Pressupoe API de [US-3-02](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md).
- Ponto de partida: `frontend/src/pages/AtivosList.tsx` e `frontend/src/services/ativos.ts` (PRD 4.0); seguir padrao visual existente do produto.
- Onde o modo de fornecimento for selecionado ou exibido, utilizar os valores canonicos expostos pela API.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um evento e um usuario com permissao operacional adequada,
  **when** o operador ajusta o subset de categorias habilitadas,
  **then** a UI persiste via API e reflete o estado atual apos recarregar ou atualizar a visao.
- **Given** um usuario sem permissao para alterar configuracao,
  **when** acessa o fluxo relevante,
  **then** acoes de gravacao nao estao disponiveis ou falham de forma clara, consistente com a API.
- **Given** fluxos que exibem dados para operacao futura (conciliacao/emissao),
  **when** o operador inspeciona contexto de evento,
  **then** categoria e modo (quando aplicavel na tela) distinguem-se de forma compreensivel para uso posterior em FEATURE-4 e FEATURE-5.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobrar em ate **5** tasks por US (`GOV-USER-STORY.md`) na etapa `SESSION-DECOMPOR-US-EM-TASKS.md`.

- [TASK-1.md](./TASK-1.md) — Cliente HTTP e tipos para configuracao de categorias e modos canonicos
- [TASK-2.md](./TASK-2.md) — Fluxo UI para subset de categorias por evento (persistencia e refresco)
- [TASK-3.md](./TASK-3.md) — RBAC e feedback de erro na UI de configuracao
- [TASK-4.md](./TASK-4.md) — Distincao compreensivel entre categoria e modo de fornecimento na UI
- [TASK-5.md](./TASK-5.md) — Validacao final da US (build, regressao minima, checklist de aceite)

## Arquivos Reais Envolvidos

- `frontend/src/pages/AtivosList.tsx` *(e componentes extraidos se necessario)*
- `frontend/src/services/ativos.ts`
- Documentacao de apoio em `docs/` quando o projeto exigir

## Artefato Minimo

- Fluxo de UI funcional para configurar subset de categorias por evento, alinhado à API

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
- Outras USs: [US-3-02](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md) deve estar `done` antes da execucao
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
