---
doc_id: "US-4-02-REGISTRO-RECEBIDO-CONFIRMADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
decision_refs: []
---

# US-4-02 - Registro de recebido confirmado

## User Story

**Como** operador ou integracao (FEATURE-7),
**quero** registar `recebido_confirmado` por lote ou registro equivalente com vinculo a categoria e modo externo,
**para** que a operacao tenha fonte de verdade auditavel do que entrou face ao planejado.

## Feature de Origem

- **Feature**: FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira
- **Comportamento coberto**: fluxo de registro de recebimento; persistencia de quantidades e/ou artefatos; criterio de aceite da feature item 1.

## Contexto Tecnico

- API/backend alinhado a cargas automatizadas futuras (FEATURE-7); contrato minimo para formatos heterogeneos de ticketeiras (PRD sec. 5).
- LGPD: metadados e referencias conforme placeholder acordado em US-4-01.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** evento, diretoria, categoria e modo externo validos,
  **when** um lote de recebimento e submetido,
  **then** o sistema persiste `recebido_confirmado` associado a esses eixos e fica consultavel.
- **Given** um recebimento com artefato (ficheiro, link ou nota textual),
  **when** o registo e concluido,
  **then** a rastreabilidade minima exigida pelo manifesto FEATURE-4 sec. 2 e mantida.
- **Given** o mesmo contexto de previsao,
  **when** o operador consulta o historico de recebimentos,
  **then** alteracoes relevantes ficam associadas a identidade temporal e de ator (trilha consumida ou estendida em US-4-01/US seguintes).

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — servico de dominio: lote `recebido_confirmado`, artefatos e trilha
- [TASK-2.md](./TASK-2.md) — API REST (submissao e consulta/historico minimo)
- [TASK-3.md](./TASK-3.md) — testes de dominio e API

## Arquivos Reais Envolvidos

- Servicos e rotas de API em `backend/`
- [FEATURE-4.md](../../FEATURE-4.md)

## Artefato Minimo

- Fluxo documentado e executavel de registro de `recebido_confirmado` (API e/ou caso de uso) com testes de dominio na fase de execucao.

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

- [FEATURE-4](../../FEATURE-4.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) — **pre-requisito**: modelo/migrations de recebimento e campos de trilha conforme US-4-01 concluida (`status` canonico no frontmatter da US-4-01); execucao de codigo desta US fica bloqueada ate essa base existir
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md)
- [FEATURE-4](../../FEATURE-4.md)
