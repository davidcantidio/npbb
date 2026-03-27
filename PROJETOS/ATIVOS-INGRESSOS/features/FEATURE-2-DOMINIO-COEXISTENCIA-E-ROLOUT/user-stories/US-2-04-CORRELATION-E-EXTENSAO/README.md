---
doc_id: "US-2-04-CORRELATION-E-EXTENSAO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-2"
decision_refs: []
---

# US-2-04 - Correlation ID e ponto de extensao para fluxos futuros

## User Story

Como engenheiro de plataforma,
quero definir e implementar um ponto de extensao para `correlation_id` (ou
padrao equivalente alinhado ao PRD),
para que FEATURE-4 a FEATURE-8 possam propagar e correlacionar operacoes sem
redesenhar a observabilidade do zero.

## Feature de Origem

- **Feature**: FEATURE-2 (Dominio, coexistencia com legado e rollout)
- **Comportamento coberto**: criterio de aceite 4; impacto Observabilidade na
  sec. 7 do manifesto; objetivo de negocio sobre trilha minima entre operacoes.

## Contexto Tecnico

FastAPI middleware ou dependencias injetaveis; logging estruturado; aceitacao de
header de entrada (ex.: `X-Correlation-ID`) e propagacao em contexto de
request. O contrato deve ser documentado para uso em routers `ativos` e
`ingressos` e em servicos compartilhados. PRD sec. 4.1 menciona
`correlation_id` na observabilidade.

## Plano TDD (opcional no manifesto da US)

- **Red**: teste que falha quando correlation nao propaga para log ou contexto
  *(detalhar em TASKs)*
- **Green**: middleware/helper aplicado aos fluxos baseline escolhidos
- **Refactor**: unificar com padroes existentes de request id no repo, se houver

## Criterios de Aceitacao (Given / When / Then)

- **Given** uma requisicao HTTP aos endpoints baseline de ativos ou ingressos,
  **when** um `correlation_id` e fornecido pelo cliente ou gerado pelo servidor,
  **then** o identificador esta disponivel em contexto de logging ou struct log
  de forma documentada para encadeamento.
- **Given** o contrato publicado *(doc tecnica ou ADR)*,
  **when** uma feature posterior precisar anexar eventos de dominio,
  **then** o ponto de extensao e localizavel *(modulo/callback/helper nomeado)*
  sem acoplamento a implementacao interna nao estavel.
- **Given** execucao em ambiente de integracao,
  **when** duas requisicoes correlacionadas sao disparadas,
  **then** os logs ou tracos permitem associar ambas ao mesmo id *(evidencia em
  teste ou script de verificacao)*.

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

- `backend/app/main.py` ou modulo de middleware *(a confirmar na execucao)*
- `backend/app/routers/ativos.py`
- `backend/app/routers/ingressos.py`
- Documentacao tecnica ou ADR *(referencia cruzada com US-2-01 quando couber)*

## Artefato Minimo

- Codigo do ponto de extensao + documentacao curta do contrato de
  `correlation_id` para consumo das features seguintes.

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
  *(opcional em paralelo se apenas middleware; alinhar ordem com time para
  evitar conflitos em `main.py`)*
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
