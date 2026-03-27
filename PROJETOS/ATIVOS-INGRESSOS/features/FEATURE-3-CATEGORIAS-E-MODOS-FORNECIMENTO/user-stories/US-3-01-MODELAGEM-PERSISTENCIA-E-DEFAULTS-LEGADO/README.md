---
doc_id: "US-3-01-MODELAGEM-PERSISTENCIA-E-DEFAULTS-LEGADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-3"
decision_refs: []
---

# US-3-01 - Modelagem persistida de categorias e modos canonicos

## User Story

**Como** engenheiro de plataforma,
**quero** persistir o catalogo inicial de categorias (pista, pista premium, camarote), a vinculacao por evento (subset permitido) e os dois modos canonicos de fornecimento no banco,
**para** que APIs e telas posteriores operem sobre um contrato de dados estavel e eventos legados mantenham o comportamento acordado com FEATURE-2.

## Feature de Origem

- **Feature**: FEATURE-3 — Categorias por evento e modos de fornecimento
- **Comportamento coberto**: modelagem e migracao (sec. 6.1 do manifesto); base para criterios de aceite de catalogo por evento, modos persistidos e nao regressao de legado.

## Contexto Tecnico

- **Dependencia de feature**: [FEATURE-2](../../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md) concluida ou em convivencia controlada conforme rollout.
- Stack alinhada ao PRD sec. 4.0: SQLModel/Alembic no backend NPBB; Area equivalente a Diretoria em v1.
- Escopo de catalogo: apenas o trio inicial (PRD 2.4, hipoteses congeladas); expansao futura e politica separada.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto; detalhar em `TASK-*.md` se aplicavel.
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** o modelo canonico de categorias e modos definido no manifesto da feature,
  **when** as migracoes sao aplicadas,
  **then** existem estruturas que permitem registrar subset do trio por evento e associar linhas operacionais ao modo **interno emitido com QR** ou **externo recebido**.
- **Given** um evento existente sem configuracao explicita de categorias,
  **when** o sistema resolve defaults,
  **then** o comportamento permanece alinhado ao contrato de coexistencia em FEATURE-2 (sem regressao documentada nos testes de migracao/dados).
- **Given** o catalogo inicial,
  **when** um evento configura apenas parte das categorias,
  **then** o modelo aceita subset valido (pista, pista premium e/ou camarote) sem exigir uso forcado das tres.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobrar em ate **5** tasks por US (`GOV-USER-STORY.md`) na etapa `SESSION-DECOMPOR-US-EM-TASKS.md`.

- *(pendente de decomposicao em `TASK-*.md`)*

## Arquivos Reais Envolvidos

- `backend/app/models/models.py` *(ou modulo equivalente ao evoluir o dominio)*
- `backend/alembic/versions/*` *(novas revisoes)*
- Testes de modelo/migracao conforme convencao do repositorio

## Artefato Minimo

- Esquema persistido e migracoes aplicaveis com defaults de legado verificados

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
- [FEATURE-2](../../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md) *(dominio base e rollout)*
- Outras USs: nenhuma *(primeira US da cadeia FEATURE-3)*
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
