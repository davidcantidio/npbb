---
doc_id: "US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "optional"
feature_id: "FEATURE-3"
decision_refs: []
---

# US-3-04 - Regressao FEATURE-2, testes de cobertura e observabilidade de alteracoes

## User Story

**Como** responsavel por qualidade e operacao,
**quero** testes automatizados e trilha minima de auditoria para configuracao de categorias e modos,
**para** garantir que eventos legados nao regrediram (FEATURE-2), ambos os modos canonicos estao cobertos e alteracoes sensiveis ficam rastreaveis (PRD 2.6).

## Feature de Origem

- **Feature**: FEATURE-3 — Categorias por evento e modos de fornecimento
- **Comportamento coberto**: testes e evidencias (sec. 6.4 do manifesto); impacto observabilidade (sec. 7); criterios de aceite de nao regressao e RBAC/auditoria operacional.

## Contexto Tecnico

- Executar apos [US-3-02](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md); cenarios E2E ou de contrato que dependam de UI devem aguardar [US-3-03](../US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO/README.md) quando aplicavel.
- Cobrir casos: evento com subset parcial do trio; modo interno vs externo nas leituras expostas; evento sem configuracao explicita (defaults).

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** a baseline de coexistencia definida em FEATURE-2,
  **when** a suite de regressao relevante e executada apos as mudancas de FEATURE-3,
  **then** nao ha falhas atribuiveis a quebra de contrato para eventos legados sem configuracao nova.
- **Given** cenarios de API e/ou integracao acordados,
  **when** exercidos para cada modo canonico,
  **then** os resultados observaveis distinguem corretamente **interno emitido com QR** e **externo recebido** onde o contrato prometer essa distincao.
- **Given** uma alteracao de configuracao por evento por usuario autorizado,
  **when** a operacao conclui,
  **then** existe trilha minima (log ou registro auditavel) alinhada ao manifesto sec. 7 para suporte operacional e compliance.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobrar em ate **5** tasks por US (`GOV-USER-STORY.md`) na etapa `SESSION-DECOMPOR-US-EM-TASKS.md`.

- [TASK-1.md](./TASK-1.md) — regressao FEATURE-2 / eventos legados sem configuracao explicita
- [TASK-2.md](./TASK-2.md) — testes API por modos canonicos e subset do trio
- [TASK-3.md](./TASK-3.md) — trilha minima de auditoria em mutacoes de configuracao
- [TASK-4.md](./TASK-4.md) — smoke E2E Playwright para UI de configuracao (quando aplicavel)

## Arquivos Reais Envolvidos

- `backend/tests/test_ativos_endpoints.py` *(e novos modulos de teste conforme necessario)*
- Testes de frontend se o projeto padronizar para fluxos criticos
- Pontos de logging/auditoria no backend

## Artefato Minimo

- Evidencias de teste documentadas na revisao; trilha de alteracao de configuracao operacional

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
- Outras USs: [US-3-02](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md) `done`; [US-3-03](../US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO/README.md) `done` para cenarios que exijam UI
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
