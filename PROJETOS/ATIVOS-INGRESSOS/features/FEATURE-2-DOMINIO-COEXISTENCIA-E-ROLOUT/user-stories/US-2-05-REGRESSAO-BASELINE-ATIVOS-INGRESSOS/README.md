---
doc_id: "US-2-05-REGRESSAO-BASELINE-ATIVOS-INGRESSOS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-2"
decision_refs: []
---

# US-2-05 - Regressao do baseline ativos e ingressos

## User Story

Como responsavel por qualidade,
quero evidencia automatizada de que os contratos atuais de `/ativos` e
`/ingressos` permanecem corretos para eventos **nao** migrados,
para que a convivencia com o legado descrita no PRD 4.0 seja verificavel apos
US-2-02 e US-2-03.

## Feature de Origem

- **Feature**: FEATURE-2 (Dominio, coexistencia com legado e rollout)
- **Comportamento coberto**: comportamento esperado (rotas legadas funcionais);
  estrategia itens 2 (API/backend) e 4 (testes de regressao baseline); impacto
  Testes na sec. 7 do manifesto.

## Contexto Tecnico

Baseline em `test_ativos_endpoints.py` e `test_ingressos_endpoints.py` conforme
PRD 4.0. Apos introducao de migracoes e gate por evento, a suite deve cobrir
explicitamente o caminho legado *(evento sem novo fluxo)* e garantir que
paginacao, filtros, atribuicao e solicitacoes continuam conforme contratos
existentes.

## Plano TDD (opcional no manifesto da US)

- **Red**: ampliar ou adicionar casos que falham se o gate desviar trafego legado
  incorretamente *(detalhar em TASKs)*
- **Green**: suite verde no CI com `TESTING=true` / SQLite de testes
- **Refactor**: extrair fixtures de evento migrado vs nao migrado

## Criterios de Aceitacao (Given / When / Then)

- **Given** um evento configurado como **nao migrado**,
  **when** os testes de regressao dos endpoints baseline sao executados,
  **then** respostas e efeitos colaterais *(status codes, contagem, vinculos de
  cota)* permanecem alinhados ao comportamento documentado no PRD sec. 4.0.
- **Given** alteracoes em `ativos.py` ou `ingressos.py` relacionadas ao gate,
  **when** a pipeline de testes roda,
  **then** falhas indicam regressao real *(nao apenas flakiness documentado)*.
- **Given** o manifesto da FEATURE-2,
  **when** a US for concluida,
  **then** existe referencia aos comandos ou alvos de teste usados como
  evidencia *(no handoff ou README de task)*.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

*(Desdobramento em `TASK-*.md` na etapa `SESSION-DECOMPOR-US-EM-TASKS.md` /
`PROMPT-US-PARA-TASKS.md`. Nenhuma task criada nesta sessao.)*

## Arquivos Reais Envolvidos

- `backend/tests/test_ativos_endpoints.py`
- `backend/tests/test_ingressos_endpoints.py`
- `backend/app/routers/ativos.py`
- `backend/app/routers/ingressos.py`

## Artefato Minimo

- Testes atualizados ou novos com cenarios explicitos de evento nao migrado +
  execucao registrada no handoff.

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
- Outras USs:
  - [US-2-02 - Modelo e migracoes](../US-2-02-MODELO-E-MIGRACOES-INICIAIS/README.md) *(done ou em validacao conjunta)*
  - [US-2-03 - Rollout por evento](../US-2-03-ROLLOUT-POR-EVENTO/README.md) *(done ou em validacao conjunta — regressao exerce o gate)*
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
