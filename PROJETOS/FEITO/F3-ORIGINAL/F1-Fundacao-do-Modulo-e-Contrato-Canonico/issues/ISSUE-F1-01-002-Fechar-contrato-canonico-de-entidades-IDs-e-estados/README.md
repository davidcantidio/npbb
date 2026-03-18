---
doc_id: "ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-002 - Fechar contrato canonico de entidades IDs e estados

## User Story

Como PM do FRAMEWORK3, quero fechar contrato canonico de entidades ids e estados para dominio framework3 alinhado a taxonomias ids e estados canonicos com modelos e schemas coerentes.

## Contexto Tecnico

Depois de estabilizar a baseline o projeto precisa alinhar a estrutura persistida do dominio a governanca canonicamente aprovada. Esta issue fecha taxonomias IDs estados e o reflexo disso em modelos e schemas. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Fechar contrato canonico de entidades IDs e estados"
- Green: alinhamento minimo do recorte para entregar contrato canonico do dominio framework3 refletido em modelos schemas e migration
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Fechar contrato canonico de entidades IDs e estados" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then contrato canonico do dominio FRAMEWORK3 refletido em modelos schemas e migration.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [x] todas as tasks da issue estao `done`
- [x] validacoes obrigatorias do recorte foram executadas ou revisadas
- [x] o artifact minimo da issue foi produzido e ficou rastreavel
- [x] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Fechar contrato canonicode entidades estados e taxonomias](./TASK-1.md)
- [T2 - Materializar contrato aprovado em models schemas e migration](./TASK-2.md)

## Arquivos Reais Envolvidos
- `PROJETOS/FRAMEWORK3/INTAKE-FRAMEWORK3.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py`
- `backend/tests/test_framework_domain_contract.py`

## Artifact Minimo

Contrato canonico do dominio FRAMEWORK3 refletido em modelos schemas e migration.

## Contrato Canonico Aprovado em T1

### Principios

- separar identificador tecnico interno (`id`) de identificador canonico externo (`canonical_name`, `doc_id`, `canonical_id`, `task_id`, `target_ref`)
- usar `ProjectStatus` apenas para ciclo do projeto; nao reutilizar esse enum para fase, epico, sprint, issue ou task
- usar `DocumentStatus` apenas para artefatos de governanca e execucao (`phase`, `epic`, `sprint`, `issue`, `task`)
- manter `ApprovalStatus` e `AuditGateState` como eixos ortogonais ao `status` documental
- tratar taxonomias de intake como listas controladas por `GOV-INTAKE.md`, sem valores livres em runtime
- tratar `agent_execution` como trilha auditavel de execucao, nao como item de backlog

### Matriz de entidades, IDs e estados

| Entidade | ID canonico externo | Chave tecnica | Estados canonicos | Observacoes |
|---|---|---|---|---|
| `project` | `canonical_name` | `id` | `ProjectStatus` | `canonical_name` substitui a necessidade de `canonical_id` para projeto |
| `intake` | `doc_id` no formato `INTAKE-<PROJETO>` ou `INTAKE-<PROJETO>-<SLUG>` | `id` | `status` documental + `ApprovalStatus` | `intake_kind` e `source_mode` seguem `GOV-INTAKE.md` |
| `prd` | `doc_id` no formato `PRD-<PROJETO>` ou `PRD-<PROJETO>-<SLUG>` | `id` | `status` documental + `ApprovalStatus` | `intake_id` liga ao intake de origem |
| `phase` | `canonical_id` no formato `F<N>` | `id` | `DocumentStatus` + `AuditGateState` | `phase_number` continua chave ordinal interna |
| `epic` | `canonical_id` no formato `EPIC-F<N>-<NN>` | `id` | `DocumentStatus` | `epic_number` continua ordinal dentro da fase |
| `sprint` | `canonical_id` no formato `SPRINT-F<N>-<NN>` | `id` | `DocumentStatus` | continua manifesto operacional de selecao |
| `issue` | `canonical_id` no formato `ISSUE-F<N>-<NN>-<MMM>` | `id` | `DocumentStatus` | `issue_format`, `task_instruction_mode` e `origin_audit_id` sao metadados de contrato |
| `task` | `task_id` no formato `T<N>` e `canonical_id` derivado de `<issue_canonical_id>:<task_id>` | `id` | `DocumentStatus` | `task_number` preserva ordenacao; `tdd_aplicavel` nao substitui status |
| `agent_execution` | `target_ref` apontando para alvo canonico (`F<N>`, `EPIC-...`, `ISSUE-...`, `ISSUE-...:T<N>`) | `id` | `success` booleano + `ApprovalStatus` quando houver HITL | nao recebe `DocumentStatus` nem `canonical_id` proprio nesta issue |

### Taxonomias controladas

- `ProjectStatus`: `draft`, `intake`, `prd`, `planning`, `execution`, `audit`, `completed`, `cancelled`
- `DocumentStatus`: `todo`, `active`, `done`, `cancelled`
- `ApprovalStatus`: `pending`, `approved`, `rejected`, `auto_approved`
- `AgentMode`: `human_in_loop`, `semi_autonomous`, `fully_autonomous`
- `AuditGateState`: `not_ready`, `pending`, `hold`, `approved`
- `IssueFormat`: `directory`, `legacy`
- `TaskInstructionMode`: `optional`, `required`
- `ReviewVerdict`: `aprovada`, `correcao_requerida`, `cancelled`
- `FollowupDestination`: `issue-local`, `new-intake`, `cancelled`
- `FollowupDestination` operacional temporario: `none` apenas como valor neutro antes de haver follow-up decidido; nao substitui destinos canonicos de governanca
- `intake.status` e `prd.status`: `draft`, `active`, `done`, `cancelled`
- `intake_kind`: `new-product`, `new-capability`, `problem`, `refactor`, `audit-remediation`
- `source_mode`: `original`, `backfilled`, `audit-derived`
- `product_type`: `campaign-experience`, `internal-tool`, `data-product`, `platform-capability`, `integration`, `workflow-improvement`
- `delivery_surface`: `frontend-web`, `backend-api`, `fullstack-module`, `data-pipeline`, `admin-panel`, `docs-governance`
- `business_domain`: `landing-pages`, `dashboard`, `leads`, `eventos`, `etl`, `crm`, `autenticacao`, `governanca`
- `criticality`: `baixa`, `media`, `alta`, `critica`
- `data_sensitivity`: `publica`, `interna`, `restrita`, `lgpd`
- `change_type`: `novo-produto`, `nova-capacidade`, `evolucao`, `migracao`, `refactor`, `correcao-estrutural`
- `audit_rigor`: `standard`, `elevated`, `strict`

### Regras de identificacao e separacao de responsabilidades

- APIs e sincronizacao Markdown-banco devem expor IDs canonicos para navegacao humana e rastreabilidade; `id` numerico permanece interno
- `FrameworkProject` deve continuar usando `canonical_name` como identificador de negocio; `canonical_id` adicional seria duplicacao indevida
- `FrameworkTask` nao deve inventar um segundo numero global; a identidade global da task e o par `issue.canonical_id` + `task_id`
- `agent_execution.target_ref` deve sempre apontar para um ID canonico existente e nunca para caminhos livres
- `ProjectStatus` nao substitui `DocumentStatus`; fase, epico, sprint, issue e task permanecem presos aos quatro estados de `GOV-SCRUM.md`
- `ApprovalStatus` nao substitui `status`; aprovacao humana e eixo independente para intake, PRD e execucoes com HITL

### Divergencias observadas no estado atual

- `backend/app/models/framework_models.py` e `backend/app/schemas/framework.py` ja carregam `canonical_id`, `framework_document_status`, `framework_audit_gate_state`, `issue_format`, `task_instruction_mode` e payloads JSON ricos, enquanto a migration citada ainda materializa um contrato mais antigo
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py` cria `framework_phase.status` com o enum de ciclo de projeto (`projectstatus`) em vez de `DocumentStatus`
- a mesma migration ainda usa colunas antigas como `framework_intake.content`, `validated`, `framework_prd.content`, `approved`, `framework_epic.epic_id`, `framework_issue.issue_id` e `framework_task.instruction`, sem os campos canonicos hoje previstos em model/schema
- a migration nao cria `project_id`, `canonical_id`, `document_path`, campos de acceptance/DoD, nem os metadados TDD exigidos para `issue` e `task`
- `FrameworkIntake` e `FrameworkPRD` mantem `status`, `intake_kind` e `source_mode` como `str`; em `T2` isso deve passar a refletir as taxonomias documentadas aqui, sem valores arbitrarios
- `backend/tests/test_framework_domain_contract.py` ainda nao existe; a suite deve nascer em `T2` para congelar este contrato em red/green

### Decisao de escopo para T2

- `T1` encerra apenas o contrato documental; nenhum model, schema, migration ou teste e alterado nesta task
- `T2` deve alinhar implementacao e migration a esta matriz, sem introduzir novos IDs ou estados fora deste manifesto
- a issue permanece `active` apos `T1`; a cascata de fechamento fica bloqueada ate `T2` concluir models, schemas, migration e a suite de contrato

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F1-01-Modelo-Canonico-do-Framework3.md)
- [Fase](../../F1_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-01-001
