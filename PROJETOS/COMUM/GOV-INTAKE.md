---
doc_id: "GOV-INTAKE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
---

# GOV-INTAKE

## Objetivo

Formalizar a etapa `Intake -> PRD` para que a IA gere PRDs completos, auditaveis,
nao ingenuos e reutilizaveis tanto para novas iniciativas quanto para problemas,
refactors e remediacoes estruturais.

## Regra Canonica

- todo fluxo novo comeca em `INTAKE-<PROJETO>.md` ou `INTAKE-<PROJETO>-<SLUG>.md`
- o PRD so e elegivel quando referenciar explicitamente o arquivo de intake usado como origem
- se o intake estiver incompleto, a IA deve devolver lacunas criticas em vez de improvisar regra de negocio
- achados estruturais originados de auditoria podem abrir novos intakes com `intake_kind: audit-remediation`
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, o PRD gerado deve ser de remediacao controlada

## Taxonomias Controladas

Usar apenas valores desta lista, salvo decisao documentada em `GOV-DECISOES.md`:

- `intake_kind`: `new-product`, `new-capability`, `problem`, `refactor`, `audit-remediation`
- `source_mode`: `original`, `backfilled`, `audit-derived`
- `product_type`: `campaign-experience`, `internal-tool`, `data-product`, `platform-capability`, `integration`, `workflow-improvement`
- `delivery_surface`: `frontend-web`, `backend-api`, `fullstack-module`, `data-pipeline`, `admin-panel`, `docs-governance`
- `business_domain`: `landing-pages`, `dashboard`, `leads`, `eventos`, `etl`, `crm`, `autenticacao`, `governanca`
- `criticality`: `baixa`, `media`, `alta`, `critica`
- `data_sensitivity`: `publica`, `interna`, `restrita`, `lgpd`
- `change_type`: `novo-produto`, `nova-capacidade`, `evolucao`, `migracao`, `refactor`, `correcao-estrutural`
- `audit_rigor`: `standard`, `elevated`, `strict`

`integrations` permanece lista livre de sistemas, servicos, APIs ou modulos afetados.

## Campos Minimos Obrigatorios

O intake nao esta pronto para PRD sem:

- problema ou oportunidade
- publico ou operador principal
- job to be done dominante
- fluxo principal esperado
- objetivo de negocio e metricas de sucesso
- restricoes e nao-objetivos
- dependencias e integracoes
- arquitetura ou superficies impactadas
- riscos relevantes
- lacunas conhecidas
- rastreabilidade de origem quando o intake vier de auditoria ou backfill

Para `intake_kind: problem | refactor | audit-remediation`, tambem sao obrigatorios:

- sintoma observado
- impacto operacional
- evidencia tecnica
- componente(s) afetado(s)
- riscos de nao agir

## Intakes Retroativos (`source_mode: backfilled`)

Contextos validos de origem:

- PRD existente sem intake formal
- conjunto de artefatos ativos de um projeto ja em andamento
- analise critica consolidada de documentos vigentes
- contexto historico fornecido pelo PM com rastreabilidade suficiente

Regras operacionais:

- o gate `Intake -> PRD` continua valendo integralmente
- o que muda e a origem da evidencia, nao o nivel minimo de clareza exigido
- campos historicos desconhecidos podem ficar como `nao_definido` somente se isso nao bloquear objetivo, escopo, restricoes, arquitetura ou riscos
- todo `nao_definido` precisa aparecer em `Lacunas Conhecidas`
- a secao de rastreabilidade deve apontar o documento, auditoria ou contexto usado para o backfill

## Gate de Prontidao para PRD

Esta e a fonte unica do gate `Intake -> PRD`.

A etapa de geracao do PRD so deve avancar quando o `INTAKE-*.md` responder, com clareza suficiente:

- por que isso existe
- para quem existe
- o que entra e o que nao entra
- onde a mudanca toca na arquitetura
- como o sucesso sera medido
- quais restricoes e riscos sao incontornaveis
- o que ainda esta em aberto
- se existe origem auditavel de um problema ou remediacao

## Regra Anti-PRD-Ingenuo

A IA nao pode:

- preencher silenciosamente regra de negocio nao declarada
- inferir dependencia externa critica sem marcar como hipotese
- transformar wishlist em escopo fechado sem nao-objetivos claros
- ignorar restricoes de dados, seguranca, rollout ou operacao
- tratar remediacao estrutural como ajuste pontual quando o proprio intake declarar escopo sistemico

## Artefatos Vinculados

- template preenchivel: `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
- prompt canonico: `PROJETOS/COMUM/PROMPT-INTAKE-PARA-PRD.md`
- sessao de intake: `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`
- sessao de PRD: `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
