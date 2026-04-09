---
doc_id: "PRD-ATIVOS-INGRESSOS"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-04-06"
project: "ATIVOS-INGRESSOS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "internal-framework"
delivery_surface: "cli-deterministica"
business_domain: "engenharia"
criticality: "media"
data_sensitivity: "interna"
integrations:
  - "Postgres"
  - "Markdown"
change_type: "nova-capacidade"
audit_rigor: "standard"
generated_by: "fabrica-cli"
generator_stage: "scaffold"
---

# PRD - ATIVOS-INGRESSOS

> PRD inicial lean. Complete manualmente ou use `fabrica generate prd --project ATIVOS-INGRESSOS`.
> Este documento nao lista backlog entregavel; a proxima etapa explicita e `PRD -> Features`.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-ATIVOS-INGRESSOS.md](./INTAKE-ATIVOS-INGRESSOS.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-04-06
- **PRD derivado**: nao_aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: ATIVOS-INGRESSOS
- **Tese em 1 frase**: nao_definido
- **Valor esperado em 3 linhas**:
  - nao_definido
  - nao_definido
  - nao_definido

## 2. Especificacao Funcional

### 2.1 Problema ou Oportunidade

- **Problema atual**: nao_definido
- **Evidencia do problema**: nao_definido
- **Custo de nao agir**: nao_definido
- **Por que agora**: nao_definido

### 2.2 Publico e Operadores

- **Usuario principal**: nao_definido
- **Usuario secundario**: nao_definido
- **Operador interno**: CLI Fabrica
- **Quem aprova ou patrocina**: nao_definido

### 2.3 Jobs to be Done

- **Job principal**: nao_definido
- **Jobs secundarios**: nao_definido
- **Tarefa atual que sera substituida**: nao_definido

### 2.4 Escopo

### Dentro

- definir o fluxo principal do projeto

### Fora

- TUI

### 2.5 Resultado de Negocio e Metricas

- **Objetivo principal**: projeto operacional na Fabrica
- **Metricas leading**: tempo de bootstrap
- **Metricas lagging**: sync bem sucedido com projeto visivel no banco
- **Criterio minimo para considerar sucesso**: cadeia documental gerada sem drift

### 2.6 Restricoes e Guardrails

- **Restricoes tecnicas**: Markdown como fonte de verdade
- **Restricoes operacionais**: sync Postgres obrigatorio
- **Restricoes legais ou compliance**: nao_aplicavel
- **Restricoes de prazo**: nao_definido
- **Restricoes de design ou marca**: nome publico Fabrica

### 2.7 Dependencias e Integracoes

- **Sistemas internos impactados**: `PROJETOS/`, `scripts/fabrica_projects_index/`
- **Sistemas externos impactados**: Postgres
- **Dados de entrada necessarios**: intake aprovado
- **Dados de saida esperados**: features, user stories, tasks

## 3. Hipoteses Congeladas

- **Lacunas resolvidas na clarificacao**: nenhuma ainda
- **Hipoteses congeladas**: core CLI-only
- **Dependencias externas pendentes**: URL do Postgres operacional
- **Riscos de interpretacao**: backlog ainda nao decomposto

## 4. Plano Tecnico

### 4.1 Arquitetura Geral do Projeto

- **Backend**: scripts Python da Fabrica
- **Frontend**: nao_aplicavel
- **Banco/migracoes**: schema Postgres do indice derivado
- **Observabilidade**: `sync_runs`
- **Autorizacao/autenticacao**: nao_aplicavel
- **Rollout**: execucao local por CLI

### 4.2 Decisoes Tecnicas e Contratos Relevantes

- **Contratos de API / integracoes**: CLI `fabrica`
- **Persistencia / migracoes**: sync para Postgres
- **Observabilidade e operacao**: falha de sync encerra o comando
- **Trade-offs tecnicos assumidos**: alias `openclaw` apenas como compatibilidade

## 5. Riscos Globais

- **Risco de produto**: escopo sem consolidacao
- **Risco tecnico**: automacao gerar backlog generico demais
- **Risco operacional**: dependencia do Postgres indisponivel
- **Risco de dados**: baixo
- **Risco de adocao**: persistencia de fluxos legados

## 6. Nao-Objetivos

- operar runtime de host no core
- reintroduzir bootstrap de features no create
- substituir revisao humana do intake/PRD

---

> **Pos-PRD (nao faz parte deste arquivo):** execute
> `fabrica generate features --project ATIVOS-INGRESSOS`
> para o fluxo canonico com provider; use `--proposal-file <JSON>` para modo offline
> e `--legacy` somente para o pipeline heuristico legado.

## 7. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| Postgres | banco | runtime operacional | read model do projeto | pending |

## 8. Rollout e Comunicacao

- **Estrategia de deploy**: execucao local por CLI
- **Comunicacao de mudancas**: registrar em docs do projeto
- **Treinamento necessario**: uso basico da Fabrica CLI
- **Suporte pos-launch**: nao_aplicavel

## 9. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto**: revisao humana de intake e PRD
- **Criterios de auditoria**: `PROJETOS/COMUM/GOV-AUDITORIA.md`
- **Threshold anti-monolito**: `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## 10. Checklist de Prontidao

- [ ] Intake revisado
- [ ] Escopo e metricas verificados
- [ ] Riscos declarados
- [ ] Proxima etapa explicita: `fabrica generate features`

## 11. Anexos e Referencias

- `PROJETOS/COMUM/GOV-PRD.md`
- `PROJETOS/COMUM/PROMPT-PRD-PARA-FEATURES.md`
- `PROJETOS/COMUM/SESSION-DECOMPOR-PRD-EM-FEATURES.md`
