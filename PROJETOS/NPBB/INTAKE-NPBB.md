---
doc_id: "INTAKE-NPBB.md"
version: "1.0"
status: "approved"
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

# INTAKE - NPBB

> Intake inicial do piloto do framework atual no `npbb`. O foco da primeira
> rodada e abrir uma feature real e acompanhavel sobre o produto, usando o
> pipeline canônico `Feature -> User Story -> Task`.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- unidade de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: migrar o `npbb` para o framework atual e
  validar o fluxo real de desenvolvimento numa feature de ingestao e
  qualificacao de leads

## 1. Resumo Executivo

- nome curto da iniciativa: pipeline de leads bronze silver gold
- tese em 1 frase: consolidar a ingestao de leads do NPBB num fluxo unificado,
  rastreavel e executado no formato atual do framework
- valor esperado em 3 linhas:
  - substituir telas e processos paralelos de importacao por um fluxo unico
  - rastrear cada lead desde o arquivo bruto ate o estado validado no banco
  - validar o framework atual em uma feature de negocio com backend, frontend e banco

## 2. Problema ou Oportunidade

- problema atual: o `npbb` ainda carrega fluxos documentais antigos e, no
  produto, a ingestao de leads continua dividida entre interfaces e etapas
  paralelas que dificultam rastreabilidade ponta a ponta
- evidencia do problema: o contexto legado ja descreve a necessidade de unificar
  upload, mapeamento, persistencia intermediaria e pipeline de tratamento
- custo de nao agir: o time continua com drift entre processo, codigo e
  governanca, enquanto a origem e a qualidade dos leads seguem pouco auditaveis
- por que agora: a migracao do framework para o formato atual precisa ser
  provada dentro de uma feature real do produto

## 3. Publico e Operadores

- usuario principal: operador interno que importa leads e acompanha o resultado
  do processamento
- usuario secundario: times de marketing, operacao e analytics que dependem de
  contagens confiaveis por evento
- operador interno: PM e engenharia responsaveis pela migracao do framework e
  pela feature piloto
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: importar um arquivo de leads e acompanhar o lote desde o
  upload bruto ate a promocao validada
- jobs secundarios: mapear colunas com reuso, associar evento, inspecionar
  erros do pipeline e consultar o relatorio de qualidade do lote
- tarefa atual que sera substituida: executar fluxos paralelos de importacao e
  perder rastreabilidade entre origem, mapeamento e lead final

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. Operador envia CSV ou XLSX e registra metadados do lote.
2. Sistema preserva o arquivo bruto e prepara mapeamento assistido.
3. Operador confirma evento e colunas canônicas principais.
4. Backend persiste o estado intermediario e dispara o pipeline Gold.
5. UI apresenta status do lote, erros e relatorio de qualidade.

## 6. Escopo Inicial

### Dentro

- fluxo unificado de ingestao Bronze -> Silver -> Gold
- rastreabilidade por lote, evento e linha de origem
- feature piloto documentada em `Feature -> User Story -> Task`
- migracao do projeto `NPBB` para o framework documental atual

### Fora

- integracoes futuras com Google Drive ou agendamentos automáticos
- notificacoes por email do resultado do pipeline
- rollout de multiplas features de produto nesta mesma rodada

## 7. Resultado de Negocio e Metricas

- objetivo principal: tornar a ingestao de leads auditavel e operacionalmente
  previsivel
- metricas leading: percentual de lotes com mapeamento concluido; tempo para
  chegar ao estado Gold; numero de erros rastreaveis por lote
- metricas lagging: reducao de retrabalho na importacao; maior confianca em
  dashboards e relatorios abastecidos por esses leads
- criterio minimo para considerar sucesso: o `npbb` consegue abrir e conduzir
  a primeira feature piloto integralmente no paradigma atual do framework

## 8. Restricoes e Guardrails

- restricoes tecnicas: preservar stack FastAPI + React + Postgres/Supabase e
  usar `PROJETOS/**/*.md` como fonte de verdade
- restricoes operacionais: nao manter artefatos ativos do paradigma
  `ISSUE/EPIC/FASE`
- restricoes legais ou compliance: tratamento de leads deve respeitar LGPD
- restricoes de prazo: nao definido
- restricoes de design ou marca: manter UX existente fora do necessario para a
  feature piloto

## 9. Dependencias e Integracoes

- sistemas internos impactados: backend FastAPI, frontend React, `lead_pipeline`,
  dashboards de leads e governanca em `PROJETOS/`
- sistemas externos impactados: Supabase como banco oficial
- dados de entrada necessarios: arquivos CSV/XLSX, metadados de envio, evento e
  mapeamento de colunas
- dados de saida esperados: lote rastreavel, relatorio de qualidade e leads
  promovidos quando aprovados

## 10. Arquitetura Afetada

- backend: endpoints de ingestao, orquestracao do pipeline e persistencia de lotes
- frontend: fluxo unificado de importacao e leitura de status do lote
- banco/migracoes: tabelas de lotes, aliases de coluna e persistencia Silver
- observabilidade: audit log, relatorios de qualidade e indice derivado local
- autorizacao/autenticacao: manter o modelo JWT atual
- rollout: inicial em ambiente local e de homologacao do `npbb`

## 11. Riscos Relevantes

- risco de produto: o fluxo unificado pode cobrir apenas parte dos casos reais
  de importacao na primeira rodada
- risco tecnico: migrar governanca e feature real ao mesmo tempo pode expor
  gaps de contrato nos artefatos novos
- risco operacional: operadores seguirem usando atalhos antigos fora do fluxo
  unificado
- risco de dados: persistir lote ou mapping incorreto pode contaminar a
  promocao para Gold
- risco de adocao: o time pode hesitar em abandonar definitivamente o paradigma
  anterior se a primeira feature nao for acompanhada ate o fim

## 12. Nao-Objetivos

- nao redesenhar toda a experiencia de dashboards
- nao migrar o host operacional completo do OpenClaw
- nao implementar integracoes externas futuras nesta rodada

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: o `npbb` tinha governanca em formato antigo e backlog
  espalhado entre projetos legados, enquanto o produto ainda demanda uma trilha
  clara para ingestao e qualificacao de leads
- impacto operacional: dificuldade para acompanhar a entrega real da feature e
  para sincronizar docs, implementacao e auditoria
- evidencia tecnica: o historico do repositório e o PRD legado de
  `NPBB-LEADS` descrevem o pipeline Bronze -> Silver -> Gold como necessidade
  concreta de negocio
- componente(s) afetado(s): `PROJETOS/NPBB`, `scripts/criar_projeto.py`,
  `scripts/openclaw_projects_index/`, `backend`, `frontend` e `lead_pipeline`
- riscos de nao agir: o framework atual nao sera provado em producao real do
  projeto e a ingestao de leads continuara com rastreabilidade fraca

## 14. Lacunas Conhecidas

- a priorizacao detalhada das user stories alem da primeira US ainda precisa ser
  refinada apos a aprovacao deste intake
