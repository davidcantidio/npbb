---
doc_id: "INTAKE-FRAMEWORK.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# INTAKE-FRAMEWORK

## Objetivo

Formalizar a etapa `Intake -> PRD` para que a IA gere PRDs completos, auditaveis, nao ingenuos e reutilizaveis tanto para novas iniciativas quanto para problemas e remediacoes estruturais.

## Regra Canonica

- todo fluxo novo comeca em `INTAKE-<PROJETO>.md`
- o PRD so e elegivel quando referenciar explicitamente o arquivo de intake usado como origem
- se o intake estiver incompleto, a IA deve devolver lacunas criticas em vez de improvisar regra de negocio
- achados estruturais originados de auditoria podem abrir novos intakes no formato `INTAKE-<PROJETO>-<SLUG>.md`
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, o PRD gerado deve ser de remediacao controlada, nao de produto novo

## Fluxo Operacional

1. capturar o contexto bruto no `INTAKE-<PROJETO>.md` ou `INTAKE-<PROJETO>-<SLUG>.md`
2. preencher taxonomias controladas, rastreabilidade e contexto obrigatorio
3. validar prontidao para PRD
4. rodar o prompt canonico `PROMPT-INTAKE-PARA-PRD.md`
5. gerar `PRD-<PROJETO>.md` ou um PRD derivado conforme o intake definir
6. revisar o PRD contra o intake antes de abrir fases, epicos e issues

## Taxonomias Controladas

Usar apenas valores desta lista, salvo decisao documentada em `DECISION-PROTOCOL.md`:

- `intake_kind`: `new-product`, `new-capability`, `problem`, `refactor`, `audit-remediation`
- `source_mode`: `original`, `backfilled`, `audit-derived`
- `product_type`: `campaign-experience`, `internal-tool`, `data-product`, `platform-capability`, `integration`, `workflow-improvement`
- `delivery_surface`: `frontend-web`, `backend-api`, `fullstack-module`, `data-pipeline`, `admin-panel`, `docs-governance`
- `business_domain`: `landing-pages`, `dashboard`, `leads`, `eventos`, `etl`, `crm`, `autenticacao`, `governanca`
- `criticality`: `baixa`, `media`, `alta`, `critica`
- `data_sensitivity`: `publica`, `interna`, `restrita`, `lgpd`
- `change_type`: `novo-produto`, `nova-capacidade`, `evolucao`, `migracao`, `refactor`, `correcao-estrutural`
- `audit_rigor`: `standard`, `elevated`, `strict`

`integrations` permanece como lista livre de sistemas, servicos, APIs ou modulos afetados.

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

## Regra Anti-PRD-Ingenuo

A IA nao pode:

- preencher silenciosamente regra de negocio nao declarada
- inferir dependencia externa critica sem marcar como hipotese
- transformar wishlist em escopo fechado sem nao-objetivos claros
- ignorar restricoes de dados, seguranca, rollout ou operacao
- tratar remediacao estrutural como ajuste pontual quando o proprio intake declarar escopo sistemico

## Gate de Prontidao para PRD

A etapa de geracao do PRD so deve avancar quando o `INTAKE-*.md` responder, com clareza suficiente:

- por que isso existe
- para quem existe
- o que entra e o que nao entra
- onde a mudanca toca na arquitetura
- como o sucesso sera medido
- o que ainda esta em aberto
- se existe origem auditavel de um problema ou remediacao

## Artefatos Vinculados

- template preenchivel: `PROJETOS/COMUM/INTAKE-TEMPLATE.md`
- prompt de geracao: `PROJETOS/COMUM/PROMPT-INTAKE-PARA-PRD.md`
- governanca base: `PROJETOS/COMUM/SCRUM-GOV.md`
