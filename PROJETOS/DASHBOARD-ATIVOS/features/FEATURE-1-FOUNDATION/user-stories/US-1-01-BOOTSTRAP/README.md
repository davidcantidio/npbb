---
doc_id: "US-1-01-BOOTSTRAP"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-1-FOUNDATION"
decision_refs: []
---

# US-1-01 - Bootstrap do projeto

## User Story

Como PM, quero validar o scaffold inicial do projeto para que intake,
PRD, wrappers e estrutura `Feature -> User Story -> Task` fiquem prontos
sem preenchimento manual repetitivo.

## Feature de Origem

- **Feature**: FEATURE-1-FOUNDATION
- **Comportamento coberto**: scaffold inicial do projeto com documentos,
  wrappers e relatorio base de auditoria.

## Contexto Tecnico

O script `scripts/criar_projeto.py` gera a raiz do projeto, os docs
canonicos, os wrappers locais, a feature bootstrap, a user story
bootstrap, a primeira task e o shell de auditoria da feature.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um repositorio sem o projeto alvo,
  **when** o script gera o scaffold,
  **then** o projeto nasce com `features/FEATURE-1-FOUNDATION/`.
- **Given** a feature bootstrap criada,
  **when** o PM abre os wrappers locais,
  **then** apenas sessoes canonicas `Feature/User Story/Task` sao
  referenciadas.
- **Given** a user story bootstrap,
  **when** ela for inspecionada,
  **then** `TASK-1.md` estara linkada e pronta para execucao.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [T1 - Validar o scaffold inicial](./TASK-1.md)

## Arquivos Reais Envolvidos

- `INTAKE-DASHBOARD-ATIVOS.md`
- `PRD-DASHBOARD-ATIVOS.md`
- `AUDIT-LOG.md`
- `SESSION-PLANEJAR-PROJETO.md`
- `SESSION-IMPLEMENTAR-US.md`
- `SESSION-REVISAR-US.md`
- `SESSION-AUDITAR-FEATURE.md`
- `features/FEATURE-1-FOUNDATION/FEATURE-1.md`

## Artefato Minimo

- `features/FEATURE-1-FOUNDATION/FEATURE-1.md`
- `features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/README.md`
- `features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/TASK-1.md`

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

- [Feature bootstrap](../../FEATURE-1.md)
- [PRD do projeto](../../../../PRD-DASHBOARD-ATIVOS.md)
- Outras USs: nenhuma
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [TASK-1](TASK-1.md)
