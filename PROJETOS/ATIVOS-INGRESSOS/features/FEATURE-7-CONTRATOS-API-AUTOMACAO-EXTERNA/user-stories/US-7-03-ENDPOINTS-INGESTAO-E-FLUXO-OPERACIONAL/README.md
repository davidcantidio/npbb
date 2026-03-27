---
doc_id: "US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
task_instruction_mode: "required"
feature_id: "FEATURE-7"
decision_refs: []
---

# US-7-03 - Endpoints de ingestao e fluxo operacional

## User Story

**Como** integrador externo (ex.: automacao que processa emails de ticketeiras),
**quero** enviar cargas de recebimento e artefatos via API estavel,
**para** que o sistema registre `recebido_confirmado` ou encaminhe a fila de revisao humana conforme o mesmo desenho das integracoes internas, sem produto inbox no NPBB.

## Feature de Origem

- **Feature**: FEATURE-7 - Contratos de API para automacao externa (ticketeiras)
- **Comportamento coberto**: endpoints ou jobs de carga compativeis com FEATURE-4; espelhamento de registry, ingestao inteligente e revisao humana (PRD 4.2 / manifesto sec. 2 e 4); criterios de aceite sobre fluxo operacional e reflexo em `recebido_confirmado` ou revisao.

## Contexto Tecnico

- Payloads e regras de negocio devem alinhar ao modelo e casos de uso ja definidos em FEATURE-4; esta feature apenas expoe e integra, nao substitui FEATURE-4.
- Reutilizar US-7-01 (idempotencia) e US-7-02 (auth) como pre-requisitos funcionais.
- UI de workbench de revisao: apenas integrar superficies ja existentes no produto, sem inventar escopo de inbox (manifesto sec. 6.3).

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel (planejamento; TDD na desdobramento em tasks).
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** um integrador autenticado e payload valido segundo o contrato em evolucao (OpenAPI consolidado na US-7-04),
  **when** submeter uma carga de ingestao,
  **then** o sistema persiste ou atualiza estado de recebimento de forma coerente com FEATURE-4 e aplica deduplicacao quando a chave de idempotencia for repetida.
- **Given** regras de negocio que exigem revisao humana (conforme PRD e FEATURE-4),
  **when** a carga satisfizer essas condicoes,
  **then** o registro entra na fila ou estado de revisao alinhado ao workbench existente, sem exigir inbox nativo no produto.
- **Given** uma carga aceita sem pendencia de revisao,
  **when** o processamento concluir com sucesso,
  **then** o resultado reflete `recebido_confirmado` (ou estado equivalente documentado no dominio) de forma observavel.
- **Given** payload invalido ou violacao de precondicao de negocio,
  **when** o integrador chamar a API,
  **then** recebe erro com codigo e mensagem acordados (detalhamento fino no contrato OpenAPI na US-7-04).

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobramento: `SESSION-DECOMPOR-US-EM-TASKS.md` / `PROMPT-US-PARA-TASKS.md`.

- [TASK-1.md](./TASK-1.md) — Router FastAPI, prefixo externo e registo na aplicacao
- [TASK-2.md](./TASK-2.md) — Esquemas Pydantic e validacao de carga de ingestao
- [TASK-3.md](./TASK-3.md) — Integracao de idempotencia na ingestao externa
- [TASK-4.md](./TASK-4.md) — Orquestracao com FEATURE-4: recebido confirmado vs revisao humana
- [TASK-5.md](./TASK-5.md) — Quotas, rate limit e observabilidade minima do integrador

## Arquivos Reais Envolvidos

- `backend/` routers, servicos de dominio, integracao com modulos FEATURE-4
- [FEATURE-7.md](../../FEATURE-7.md)
- [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md)

## Artefato Minimo

- API funcional de ingestao protegida, com fluxo de negocio verificavel ate `recebido_confirmado` ou revisao, pronta para documentacao e hardening na US-7-04.

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

- [FEATURE-7](../../FEATURE-7.md)
- [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-7-01](../US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md) e [US-7-02](../US-7-02-AUTENTICACAO-INTEGRADOR/README.md) devem estar `done` antes da execucao desta US
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [FEATURE-7](../../FEATURE-7.md)
