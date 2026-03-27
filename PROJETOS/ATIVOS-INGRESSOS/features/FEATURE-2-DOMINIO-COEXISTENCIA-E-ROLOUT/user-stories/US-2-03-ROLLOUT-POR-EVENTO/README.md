---
doc_id: "US-2-03-ROLLOUT-POR-EVENTO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-2"
decision_refs: []
---

# US-2-03 - Ativacao gradual por evento (feature gate)

## User Story

Como operacao e engenharia,
quero um mecanismo explicito de ativacao do novo fluxo **por evento** (feature
flag ou equivalente documentado na implementacao),
para que eventos nao migrados continuem no modelo agregado ate corte validado,
conforme PRD sec. 8 e comportamento esperado da FEATURE-2.

## Feature de Origem

- **Feature**: FEATURE-2 (Dominio, coexistencia com legado e rollout)
- **Comportamento coberto**: criterio de aceite 2; estrategia item 4 (testes do
  gate de rollout); sec. 2 comportamento esperado (criterio explicito de
  ativacao).

## Contexto Tecnico

Implementacao pode usar flag em banco, configuracao por `evento_id`, ou servico
de feature flags — a escolha deve ficar documentada e testavel. Backend
(`ativos.py`, `ingressos.py`, servicos) deve consultar o gate antes de
despachar para ramos novos. Ambiente de integracao deve reproduzir evento
migrado vs nao migrado.

## Plano TDD (opcional no manifesto da US)

- **Red**: teste de integracao falhando quando evento deveria estar no legado
  mas codigo assume novo fluxo *(detalhar em TASKs)*
- **Green**: leitura consistente do gate; testes passando para ambos os modos
- **Refactor**: consolidar helper de resolucao de modo por evento

## Criterios de Aceitacao (Given / When / Then)

- **Given** dois eventos A e B no ambiente de integracao,
  **when** apenas A esta marcado para o novo fluxo,
  **then** as operacoes relevantes de ativos/ingressos para B permanecem no
  comportamento agregado legado e para A seguem o caminho acordado para
  migrado *(sem quebrar contratos PRD 4.0 para o legado)*.
- **Given** o mecanismo de gate implementado,
  **when** a suite de testes de integracao (ou equivalente) e executada,
  **then** o gate e exercitado com resultado verificavel *(logs ou asserts)*.
- **Given** a documentacao de operacao ou ADR da US-2-01,
  **when** o gate e alterado,
  **then** a descricao do criterio de ativacao permanece coerente ou e
  atualizada na mesma entrega.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Nota de desbloqueio para decomposicao (planejamento)

**Decisao documental**: as tasks em `TASK-*.md` foram persistidas em
**planejamento antecipado** para atualizar o backlog executavel. A
**implementacao** desta US permanece **bloqueada** enquanto
[US-2-02](../US-2-02-MODELO-E-MIGRACOES-INICIAIS/README.md) nao estiver
`done`, conforme [FEATURE-2](../../FEATURE-2.md) e
`PROJETOS/COMUM/GOV-USER-STORY.md`. Cada task declara precondicoes alinhadas a
essa ordem.

## Tasks

| Task | Titulo | Documento |
|------|--------|-----------|
| T1 | Persistencia e registro do criterio de ativacao por evento | [TASK-1.md](./TASK-1.md) |
| T2 | Servico canonico de resolucao do modo por evento | [TASK-2.md](./TASK-2.md) |
| T3 | Integrar o gate nos routers de ativos e ingressos | [TASK-3.md](./TASK-3.md) |
| T4 | Testes de integracao: evento A migrado vs evento B legado | [TASK-4.md](./TASK-4.md) |
| T5 | Coerencia documental: criterio de ativacao e ADR US-2-01 | [TASK-5.md](./TASK-5.md) |

## Arquivos Reais Envolvidos

- `backend/app/routers/ativos.py`
- `backend/app/routers/ingressos.py`
- `backend/app/models/models.py` *(se flag persistida em tabela)*
- `backend/tests/` *(novos ou estendidos para integracao do gate)*

## Artefato Minimo

- Implementacao do gate por evento + testes de integracao que demonstrem legado
  vs migrado.

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

- [Manifesto FEATURE-2](../../FEATURE-2.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-2-02 - Modelo e migracoes](../US-2-02-MODELO-E-MIGRACOES-INICIAIS/README.md)
  *(obrigatoria se o gate persistir estado no novo schema; se o gate for apenas
  configuracao externa sem dependencia de tabelas novas, documentar excecao nas
  tasks)*
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
