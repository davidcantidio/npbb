---
doc_id: "PRD-NPBB.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "NPBB"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
- "backend"
- "frontend"
- "lead_pipeline"
- "supabase"
change_type: "evolucao"
audit_rigor: "elevated"
---

# PRD - NPBB

> Origem: [INTAKE-NPBB.md](INTAKE-NPBB.md)
>
> Este PRD abre o piloto real do framework atual dentro do `npbb`. O escopo
> inicial reescreve o backlog legado em torno de uma feature concreta:
> ingestao de leads Bronze -> Silver -> Gold com rastreabilidade ponta a ponta.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-NPBB.md](INTAKE-NPBB.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-26
- **PRD derivado**: nao aplicavel
- **Contexto legado reaproveitado**: `PROJETOS__legacy_pre_openclaw_migration/FEITO/NPBB-LEADS/PRD-NPBB-LEADS.md`

## 1. Resumo Executivo

- **Nome do projeto**: NPBB
- **Tese em 1 frase**: unificar a ingestao de leads do NPBB em um fluxo Bronze
  -> Silver -> Gold rastreavel e governado pelo framework atual
- **Valor esperado em 3 linhas**:
  - substituir importacoes paralelas por um fluxo unico com metadados de lote
  - preservar a origem do arquivo e do mapeamento ate a promocao final do lead
  - validar o framework atual do OpenClaw numa feature real do produto

## 2. Problema ou Oportunidade

- **Problema atual**: o `npbb` tinha governanca documental legada e ainda
  depende de processos de importacao que separam upload, mapeamento,
  tratamento e leitura de resultados sem uma trilha unica e auditavel
- **Evidencia do problema**: o PRD legado de `NPBB-LEADS` ja descreve a
  necessidade de consolidar o pipeline Bronze -> Silver -> Gold e o repositório
  mantinha o framework antigo em paralelo
- **Custo de nao agir**: o time continua com drift entre docs e implementacao,
  e os lotes de leads seguem com rastreabilidade limitada entre arquivo bruto e
  dado final
- **Por que agora**: a migracao para o framework atual precisa ser comprovada em
  um caso de negocio real do `npbb`

## 3. Publico e Operadores

- **Usuario principal**: operador interno responsavel por importar leads de
  eventos e campanhas
- **Usuario secundario**: marketing, operacao e analytics que consomem os
  leads e dashboards derivados
- **Operador interno**: PM e engenharia que vao acompanhar a feature piloto
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: enviar um arquivo de leads e acompanhar o lote ate o
  resultado final do processamento
- **Jobs secundarios**: mapear colunas, associar evento, reaproveitar aliases,
  consultar erros e validar a promocao para Gold
- **Tarefa atual que sera substituida**: importacoes fragmentadas e com pouca
  rastreabilidade entre o arquivo original e os leads promovidos

## 5. Escopo

### Dentro

- fluxo unico Bronze -> Silver -> Gold
- preservacao do arquivo bruto e dos metadados do lote
- mapeamento assistido de colunas e persistencia Silver
- execucao do `lead_pipeline` e relatorio de qualidade por lote
- migracao do projeto `NPBB` para o layout `Feature -> User Story -> Task`

### Fora

- integracao com Google Drive
- notificacoes de resultado por email
- agendamento automatico de reprocessamento
- migracao do host operacional completo do OpenClaw

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: tornar ingestao e qualificacao de leads confiaveis e
  auditaveis
- **Metricas leading**: lotes com Bronze persistido; lotes com mapeamento
  Silver concluido; tempo de transicao ate Gold
- **Metricas lagging**: reducao de retrabalho na importacao; menor divergencia
  entre lote processado e dashboards; melhor capacidade de auditoria por lote
- **Criterio minimo para considerar sucesso**: a primeira feature do `npbb`
  consegue ser planejada, executada e revisada integralmente no framework atual

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: manter FastAPI, React/Vite, SQLModel/Alembic e
  Supabase como stack principal; `PROJETOS/**/*.md` segue como fonte de verdade
- **Restricoes operacionais**: nao manter backlog ou wrappers ativos do modelo
  `ISSUE/EPIC/FASE`
- **Restricoes legais ou compliance**: dados de leads seguem sob LGPD
- **Restricoes de prazo**: nao definido
- **Restricoes de design ou marca**: preservar UX existente fora do recorte da
  feature piloto

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: backend, frontend, `lead_pipeline`,
  dashboards de leads, scripts do indice derivado e governanca em `PROJETOS`
- **Sistemas externos impactados**: Supabase como banco oficial do projeto
- **Dados de entrada necessarios**: CSV/XLSX, metadados do envio, aliases de
  colunas, vinculo de evento
- **Dados de saida esperados**: lote rastreavel, dados Silver, resultado Gold e
  relatorio de qualidade

## 9. Arquitetura Geral do Projeto

> Visao unificada de impacto arquitetural em nivel de projeto. O detalhamento
> por entregavel acontece apos este PRD, na etapa `PRD -> Features`.

- **Backend**: endpoints de upload, mapeamento e orquestracao do pipeline
- **Frontend**: tela unificada de importacao e consulta do estado do lote
- **Banco/migracoes**: lotes, aliases, persistencia Silver e relatorio de pipeline
- **Observabilidade**: relatorio por lote, `AUDIT-LOG.md` e indice derivado
- **Autorizacao/autenticacao**: manter JWT atual
- **Rollout**: ambiente local e homologacao antes de producao

## 10. Riscos Globais

- **Risco de produto**: o fluxo unificado pode deixar casos edge de importacao
  para rodadas posteriores
- **Risco tecnico**: gaps do framework atual podem aparecer ao coordenar docs,
  indice derivado e backlog real ao mesmo tempo
- **Risco operacional**: o time pode continuar recorrendo a rotas e docs antigas
- **Risco de dados**: mapeamentos ou promocao Gold incorretos podem gerar dados
  inconsistentes
- **Risco de adocao**: a migracao do framework pode ser revertida na pratica se
  a primeira feature nao avançar alem do papel

## 11. Nao-Objetivos

- nao redesenhar todos os dashboards do sistema
- nao cobrir integracoes externas futuras
- nao expandir o escopo do piloto para multiplas features simultaneas

> **Pos-PRD (nao faz parte deste arquivo):** backlog estruturado de features,
> user stories e tasks segue `GOV-FEATURE.md`, `GOV-USER-STORY.md`,
> `GOV-SCRUM.md` e as sessoes `SESSION-DECOMPOR-*`.

## 12. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| `PROJETOS/COMUM` | docs-governance | framework | contrato normativo do fluxo atual | active |
| `lead_pipeline` | backend-module | repositorio local | tratamento e validacao Gold | active |
| Supabase | database | externo | persistencia oficial do produto | active |

## 13. Rollout e Comunicacao

- **Estratégia de deploy**: rollout incremental da feature piloto com validacao
  local e de homologacao
- **Comunicacao de mudancas**: alinhar time de produto e engenharia em torno do
  fluxo unificado e do novo modelo documental
- **Treinamento necessário**: leitura das sessoes canonicas e do fluxo
  `Feature -> User Story -> Task`
- **Suporte pos-launch**: acompanhar gaps do framework e da feature piloto no
  `AUDIT-LOG.md`

## 14. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto**: intake aprovado, PRD ativo,
  revisao pos-US obrigatoria e auditoria de feature antes de encerrar a feature
- **Critérios de auditoria**: rastreabilidade do lote, aderencia ao fluxo atual
  e ausencia de retorno ao modelo legado
- **Threshold anti-monolito**: aplicar se a primeira feature crescer alem do
  limite adequado para uma unica feature

## 15. Checklist de Prontidao

- [ ] Intake referenciado e versao confirmada
- [ ] Problema, escopo, restricoes, riscos e metricas preenchidos de forma verificavel
- [ ] Arquitetura geral e rollout descritos sem catalogo de features nem tabelas de user stories neste PRD
- [ ] Dependencias externas mapeadas
- [ ] Proxima etapa explicita: `PRD -> Features` via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`
- [ ] O projeto nao depende mais de artefatos ativos `ISSUE/EPIC/FASE`

## 16. Anexos e Referencias

- [Intake](INTAKE-NPBB.md)
- [Audit Log](AUDIT-LOG.md)
- [Feature piloto](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
- [User Story piloto](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md)
- [Relatorio de auditoria](features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- [Relatorio de encerramento](encerramento/RELATORIO-ENCERRAMENTO.md)

> Frase Guia: "PRD direciona, Feature organiza, User Story fatia, Task executa, Teste valida"
