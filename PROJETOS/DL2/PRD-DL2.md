---
doc_id: "PRD-DL2.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "DL2"
intake_kind: "refactor"
source_mode: "backfilled"
origin_project: "DASHBOARD-LEADS"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "data-product"
delivery_surface: "fullstack-module"
business_domain: "dashboard"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "dashboard-leads"
  - "pipeline-etl-importacao"
  - "ticketing-importacao-de-ingressos"
  - "modelagem-lead-evento-ativacao"
  - "frontend-dashboard"
change_type: "refactor"
audit_rigor: "elevated"
---

# PRD - DL2

> Este PRD substitui o artefato documental anterior de `DL2` e reabre a
> remediacao de dashboards de leads por evento sob o eixo `delivery-first` /
> `feature-first`. O intake regenerado e a unica fonte de negocio; o legado
> arquivado entra apenas como evidencia complementar e fonte de rastreabilidade.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-DL2.md](./INTAKE-DL2.md)
- **Versao do intake**: 1.1
- **Data de criacao**: 2026-03-18
- **PRD derivado**: nao_aplicavel
- **Evidencia complementar de backfill**: `PROJETOS/FEITO/DASHBOARD-LEADS/` (sem usar `PRD-DASHBOARD-LEADS.MD`, que esta vazio)
- **Drift estrutural conhecido fora do eixo deste PRD**: `F1-FUNDACAO` e o backlog estrutural atual de `DL2` permanecem superseded ate uma sessao posterior de rebaseline

## 1. Resumo Executivo

- **Nome do projeto**: DL2 - dashboards de leads confiaveis por evento
- **Tese em 1 frase**: replanejar a remediacao do legado `DASHBOARD-LEADS` em formato `feature-first` para que os dashboards de leads por evento deixem de depender de correcoes locais e passem a refletir uma semantica consistente de `Lead`, `Evento` e `Ativacao`
- **Valor esperado em 3 linhas**:
  - restaurar confianca nas superfices prioritarias de `/dashboard/leads/*`
  - tratar modelagem canonica, backfill historico e retirada de heuristicas como trabalho habilitador de features demonstraveis
  - concentrar planejamento, execucao e auditoria do tema somente em `DL2`

## 2. Problema ou Oportunidade

- **Problema atual**: a remediacao iniciada em `DASHBOARD-LEADS` atacou sintomas reais, mas foi organizada por eixos tecnicos antes de fechar features demonstraveis, deixando fraca a cadeia `intake -> PRD -> fases -> epicos -> issues`
- **Evidencia do problema**: o legado contem intake util, backlog tecnico detalhado e um `PRD-DASHBOARD-LEADS.MD` vazio; alem disso, a investigacao previa comprovou falso vazio no dashboard de analise etaria por dependencia indevida do caminho `Lead -> AtivacaoLead -> Ativacao -> Evento`
- **Custo de nao agir**: dashboards e relatorios por evento continuam sujeitos a falso vazio e divergencia de contagem, enquanto o backlog tecnico segue desacoplado do valor visivel ao usuario
- **Por que agora**: o framework vigente exige `delivery-first` / `feature-first`, `DASHBOARD-LEADS` foi deprecado como superficie ativa e `DL2` precisa assumir o tema com um PRD auditavel

## 3. Publico e Operadores

- **Usuario principal**: usuarios internos autenticados do NPBB que consomem dashboards e relatorios de leads por evento
- **Usuario secundario**: times de operacao, marketing e analytics que dependem de contagens consistentes de leads para leitura de performance por evento
- **Operador interno**: PM e engenharia backend, frontend e dados responsaveis por replanejar o backlog legado e executar a remediacao sucessora em `DL2`
- **Quem aprova ou patrocina**: nao_definido; o contexto nao informa patrocinador nominal e o PRD preserva essa lacuna explicitamente

## 4. Jobs to be Done

- **Job principal**: consultar dashboards e relatorios de leads por evento com contagens confiaveis, independentemente da origem do lead ou do caminho de conversao
- **Jobs secundarios**: replanejar o backlog legado em features demonstraveis, preservar a semantica canonica entre `Lead`, `Evento` e `Ativacao`, e executar retroprocessamento ou endurecimento apenas quando isso sustentar valor visivel nas superfices priorizadas
- **Tarefa atual que sera substituida**: backlog organizado por fundacao tecnica, backfill e consumidores isolados, sem um eixo unico de feature que leve do intake ate tasks orientadas ao valor entregue

## 5. Escopo

### Dentro

- reescrever `PRD-DL2.md` como PRD sucessor de remediacao controlada para dashboards confiaveis por evento
- priorizar as superfices `/dashboard/leads/analise-etaria`, `/dashboard/leads` e `/dashboard/leads/relatorio`
- carregar modelagem canonica, backfill historico, reconciliacao, fallback e retirada de heuristicas apenas quando ligados a essas superfices
- migrar o backlog arquivado de `DASHBOARD-LEADS` para `DL2` com rastreabilidade explicita por feature, fase, epico e issue

### Fora

- abrir novas superfices analiticas fora do recorte atual de `/dashboard/leads/*`
- redesenhar UX, identidade visual ou payloads de frontend alem do necessario para preservar contratos existentes
- manter `DASHBOARD-LEADS` como superficie ativa de planejamento ou execucao
- rebalancear nesta rodada a estrutura documental atual de `DL2`; isso fica como follow-up posterior

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: restaurar a confianca nos dashboards de leads por evento e alinhar o backlog tecnico a features demonstraveis sob o projeto sucessor `DL2`
- **Metricas leading**: endpoints priorizados deixam de retornar falso vazio quando existem leads validos; contagens para o mesmo evento convergem entre analise etaria, dashboard agregado e relatorio; backlog herdado passa a apontar para features ou habilitadores explicitamente rastreados
- **Metricas lagging**: reducao de incidentes e de correcoes locais em queries de dashboard; maior estabilidade de contagens historicas entre consumidores analiticos; confianca operacional maior no uso dos dashboards por evento
- **Criterio minimo para considerar sucesso**: as superfices priorizadas de `/dashboard/leads/*` retornam contagens coerentes para o mesmo evento, e cada etapa tecnica remanescente da remediacao fica justificada por uma feature de valor visivel

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: preservar o stack atual do NPBB, manter compatibilidade com contratos relevantes do frontend, nao usar `PRD-DASHBOARD-LEADS.MD` como fonte de negocio e nao inferir vinculo de evento em casos ambiguos
- **Restricoes operacionais**: `DASHBOARD-LEADS` deve permanecer como arquivo morto; `DL2` passa a ser a unica superficie ativa para intake, PRD e execucao futura; o drift atual de `F1-FUNDACAO` permanece apenas como follow-up estrutural posterior
- **Restricoes legais ou compliance**: dados de leads seguem sujeitos a LGPD e nao podem perder rastreabilidade durante backfill, reconciliacao ou endurecimento
- **Restricoes de prazo**: nao_definido; o contexto nao informa milestone ou deadline e o PRD preserva essa abertura
- **Restricoes de design ou marca**: nao redesenhar a UX atual dos dashboards nesta rodada; o foco e confiabilidade analitica e reorganizacao `feature-first`

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: servicos backend de dashboard e agregacao por evento, modelagem `Lead`/`Evento`/`Ativacao`, pipelines ETL e importacao, consumidores frontend de `/dashboard/leads/*`, governanca documental do projeto sucessor
- **Sistemas externos impactados**: ticketerias e fontes externas de importacao de leads que alimentam o contexto de evento
- **Dados de entrada necessarios**: intake regenerado de `DL2`, arvore arquivada de fases/epicos/issues do legado, identificadores e metadados de evento, origens dos leads, vinculos atuais com ativacao e evidencias historicas necessarias para reconciliacao
- **Dados de saida esperados**: PRD sucessor aprovado, backlog `feature-first` rastreavel, dashboards confiaveis por evento e criterio claro para migrar, adiar ou cancelar itens herdados

## 9. Arquitetura Geral do Projeto

> Visao geral de impacto arquitetural (detalhes por feature na secao Features)

- **Backend**: servicos e consultas que consolidam leads por evento, semantica de `Lead`, `Evento` e `Ativacao`, endpoints agregados e runners operacionais de backfill/reconciliacao
- **Frontend**: paginas e services que consomem `/dashboard/leads/analise-etaria`, `/dashboard/leads` e `/dashboard/leads/relatorio`, sem mudanca de payload ou UX fora do escopo
- **Banco/migracoes**: baseline de `lead_evento`, estrategia de vinculo canonico `lead-evento`, retroprocessamento historico, reconciliacao e endurecimento de dados persistidos
- **Observabilidade**: testes de regressao, comparacao de contagens entre consumidores, artefatos `missing` / `ambiguous`, runbook de rollback e evidencias finais de auditoria
- **Autorizacao/autenticacao**: preservar o modelo atual de acesso autenticado aos dashboards
- **Rollout**: rollout incremental por feature validada; o legado fica arquivado e o rebaseline da estrutura documental atual de `DL2` fica fora desta rodada

## 10. Riscos Globais

- **Risco de produto**: reorganizar o plano pode atrasar a percepcao de entrega se as features nao forem amarradas a resultados visiveis logo no PRD
- **Risco tecnico**: migrar backlog tecnico sem PRD legado utilizavel pode criar duplicidade, perda de contexto ou falsa equivalencia entre itens `1:1` e itens fundidos
- **Risco operacional**: coexistencia temporaria entre artefatos superseded de `DL2` e o novo PRD pode levar o time a consultar o backlog errado antes do rebaseline estrutural
- **Risco de dados**: backfill ou reconciliacao mal calibrados podem duplicar, omitir ou reclassificar leads de forma incorreta
- **Risco de adocao**: equipes continuarem tratando modelagem e queries compensatorias como fins em si, em vez de sustentacao de features analiticas confiaveis

## 11. Nao-Objetivos

- manter `DASHBOARD-LEADS` como projeto ativo em paralelo
- abrir novas features de analytics fora das superfices atuais de `/dashboard/leads/*`
- transformar esta rodada em redesenho visual ou reformulacao completa de UX
- rebalancear agora a estrutura atual existente de `DL2`

---

# 12. Features do Projeto

> **Este e o eixo principal do planejamento**. Cada feature representa um comportamento
> entregavel e demonstravel. Arquitetura (banco/backend/frontend) aparece como impacto
> de cada feature, nao como organizacao principal.
>
> Regra: se uma feature nao pode ser demonstrada como algo utilizavel, ela esta
> no nivel errado de planejamento.

## Feature 1: Analise etaria confiavel por evento

### Objetivo de Negocio

Eliminar falso vazio na superficie mais critica de leitura por evento e provar,
em producao e em teste, que a semantica canonica de `Lead`, `Evento` e
`Ativacao` sustenta o dashboard de analise etaria.

### Comportamento Esperado

O usuario filtra um evento em `/dashboard/leads/analise-etaria` e recebe
contagens validas para leads diretos do evento e para leads que converteram via
ativacao ligada ao mesmo evento, sem depender de heuristicas silenciosas.

### Criterios de Aceite

- [ ] `/dashboard/leads/analise-etaria` deixa de retornar falso vazio quando existem leads validos do evento por origem direta ou via ativacao
- [ ] `LeadEvento` vira o vinculo canonico usado pelos caminhos de escrita e leitura necessarios para a analise etaria
- [ ] ETL/importacao por `evento_nome` cria vinculo apenas quando o match e deterministico; casos `missing` e `ambiguous` permanecem rastreaveis
- [ ] fixtures e suites automatizadas cobrem ao menos um caso de lead direto, um caso via ativacao e um caso nao resolvido sem inferencia silenciosa

### Dependencias com Outras Features

- nenhuma

### Riscos Especificos

- baseline parcial de writers pode mascarar a confiabilidade do reader da analise etaria
- uma migracao `1:1` de issue do legado pode sugerir progresso maior do que a feature realmente demonstravel entrega

### Fases de Implementacao

1. **Modelagem e Migration**: fechar baseline de `LeadEvento`, import/export, migration e writers canonicos minimos
2. **API**: consolidar o endpoint de analise etaria sobre a semantica canonica
3. **UI**: preservar filtros, estados e contrato atual da pagina de analise etaria
4. **Testes**: alinhar fixtures e paridade para provar ausencia de falso vazio e nao regressao

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | `lead_evento` | baseline de schema, FKs, indice e vinculo canonico `(lead_id, evento_id)` |
| Backend | writers e endpoint de analise etaria | submit publico, pipeline Gold, ETL por `evento_nome` e `dashboard_service.py` |
| Frontend | pagina de analise etaria | preservacao da UX e do contrato ja consumido em `LeadsAgeAnalysisPage` |
| Testes | suites de dashboard e pipeline | fixtures canonicas, paridade do endpoint e nao regressao de contrato |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Fechar baseline de `LeadEvento`, export/import e migration versionada | 3 | - |
| T2 | Garantir writers canonicos no submit publico, pipeline Gold e ETL deterministico | 5 | T1 |
| T3 | Consolidar a analise etaria no caminho canonico | 4 | T2 |
| T4 | Validar paridade, fixtures e ausencia de falso vazio | 2 | T3 |

---

## Feature 2: Dashboards agregados e relatorio coerentes por evento

### Objetivo de Negocio

Fazer com que as superfices agregadas de leads por evento compartilhem a mesma
fonte de verdade e deixem de divergir em totais, rankings e filtros para o
mesmo evento.

### Comportamento Esperado

O usuario consulta `/dashboard/leads` e `/dashboard/leads/relatorio` para um
mesmo evento e encontra contagens coerentes com a analise etaria, sem regressao
funcional nos consumidores frontend existentes.

### Criterios de Aceite

- [ ] `/dashboard/leads` e `/dashboard/leads/relatorio` retornam totais coerentes com `/dashboard/leads/analise-etaria` para o mesmo evento e filtro equivalente
- [ ] rankings, series e filtros agregados usam a mesma semantica canonica de `LeadEvento`
- [ ] consumidores frontend seguem operando sem mudanca de payload ou redesenho de UX
- [ ] existe smoke de nao regressao que cobre os services e paginas frontend prioritarios

### Dependencias com Outras Features

- **Feature 1**: fornece a baseline semantica e de cobertura para os consumidores agregados

### Riscos Especificos

- consolidar apenas parte dos consumidores pode preservar divergencia residual entre superficies
- a preservacao de payload pode esconder drift semantico se o teste nao comparar o mesmo evento

### Fases de Implementacao

1. **Modelagem e Migration**: reutilizar a baseline canonica ja estabelecida pela Feature 1
2. **API**: consolidar `/dashboard/leads`, rankings e `/dashboard/leads/relatorio`
3. **UI**: travar contratos de frontend sem alterar UX
4. **Testes**: comparar paridade entre superficies backend e frontend para o mesmo evento

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | leitura agregada | nenhuma nova tabela; reaproveita `lead_evento` e o historico validado |
| Backend | endpoints agregados | consolidacao de KPIs, series, rankings e relatorio sobre a mesma semantica |
| Frontend | dashboard agregado e relatorio | `dashboard_leads.ts`, `dashboard_age_analysis.ts` e smokes das paginas prioritarias |
| Testes | suites de contrato e smoke | comparacao de contagens, filtros e estabilidade do payload |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Consolidar `/dashboard/leads` e rankings sobre a semantica canonica | 2 | T4 da Feature 1 |
| T2 | Consolidar `/dashboard/leads/relatorio` sobre a mesma base | 1 | T1 |
| T3 | Travar consumidores frontend e smoke de nao regressao | 2 | T1 |

---

## Feature 3: Historico reconciliado e operacao segura do caminho canonico

### Objetivo de Negocio

Garantir que a confiabilidade visivel das superfices priorizadas se sustente no
historico, em operacao e em auditoria, sem manter caminhos heuristicos
residuais como fonte paralela de verdade.

### Comportamento Esperado

O time consegue retroprocessar historico resolvivel sem duplicidade, tratar
casos nao resolvidos com trilha auditavel, operar fallback via bronze quando
necessario e remover o heuristico somente com rollback e observabilidade
documentados.

### Criterios de Aceite

- [ ] o backfill multi-origem reexecuta sem duplicidade por `(lead_id, evento_id)` e com precedencia explicita de `source_kind`
- [ ] casos `missing`, `ambiguous` e `manual_reconciled` geram artefatos rastreaveis e fluxo minimo de fechamento manual
- [ ] o protocolo de fallback via bronze/reprocessamento fica documentado e conectado aos artefatos operacionais existentes
- [ ] a retirada do heuristico residual so ocorre com runbook de rollback, metricas e evidencias finais consolidadas

### Dependencias com Outras Features

- **Feature 1**: define a semantica canonica do vinculo `lead-evento`
- **Feature 2**: fecha os consumidores prioritarios que passarao a depender do historico reconciliado

### Riscos Especificos

- reprocessamento historico pode gerar duplicidade ou reclassificacao incorreta se a precedencia nao estiver explicita
- remocao prematura do heuristico pode quebrar leitura por evento antes do pacote operacional final

### Fases de Implementacao

1. **Modelagem e Migration**: consolidar regras de precedencia, `manual_reconciled` e criterios operacionais de fallback
2. **API**: expor runners, relatorios e pontos de apoio operacional necessarios para backfill e reconciliacao
3. **UI**: nenhuma mudanca de UX obrigatoria; artefatos podem permanecer operacionais/internos
4. **Testes**: provar idempotencia, reconciliacao, rollback e ausencia de dependencia residual do heuristico

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | historico canonico | preenchimento e reconciliacao de `lead_evento` sem reabrir o modelo antigo |
| Backend | runners e servicos operacionais | backfill multi-origem, reconciliacao, fallback e retirada controlada do heuristico |
| Frontend | sem nova superficie obrigatoria | apenas preservacao indireta da confiabilidade dos consumidores existentes |
| Testes | suites operacionais e auditoria | idempotencia, precedencia, reconciliacao, rollback e regressao final |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Implementar e testar o backfill multi-origem idempotente | 5 | T3 da Feature 2 |
| T2 | Emitir reconciliacao, formalizar `manual_reconciled` e fechar pendencias nao resolvidas | 3 | T1 |
| T3 | Definir e conectar o protocolo de fallback via bronze | 3 | T2 |
| T4 | Remover heuristicas residuais e fechar rollback, observabilidade e auditoria final | 5 | T3 |

---

# 13. Estrutura de Fases

> As fases seguem prioridade de entrega e validacao de comportamento. O legado
> arquivado informa a ordem tecnica complementar, mas nao organiza este PRD.

## Fase 1: Confianca da analise etaria por evento

- **Objetivo**: entregar a primeira prova visivel de confiabilidade por evento, fechando a baseline canonica e o reader de analise etaria
- **Features incluidas**:
  - Feature 1
- **Gate de saida**: `/dashboard/leads/analise-etaria` deixa de apresentar falso vazio para eventos com leads validos e a baseline canonica minima esta demonstrada em teste
- **Criterios de aceite**:
  - existe vinculo canonico minimo de `LeadEvento` para os writers e readers da feature
  - o endpoint de analise etaria opera sem depender do caminho heuristico legado
  - fixtures e suites automatizadas cobrem lead direto, lead via ativacao e caso nao resolvido

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F1-01 | Feature 1 | todo | 9 |
| EPIC-F1-02 | Feature 1 | todo | 5 |

## Fase 2: Convergencia dos dashboards agregados

- **Objetivo**: alinhar dashboard agregado, rankings e relatorio sobre a mesma fonte de verdade, preservando o contrato consumido pelo frontend
- **Features incluidas**:
  - Feature 2
- **Gate de saida**: `/dashboard/leads`, `/dashboard/leads/relatorio` e seus consumidores frontend ficam coerentes com a analise etaria para o mesmo evento
- **Criterios de aceite**:
  - contagens para o mesmo evento convergem entre as tres superfices priorizadas
  - rankings, filtros e relatorio usam a semantica canonica acordada
  - frontend segue sem regressao funcional e sem mudanca de payload

### Epicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F2-01 | Feature 2 | todo | 2 |
| EPIC-F2-02 | Feature 2 | todo | 1 |
| EPIC-F2-03 | Feature 2 | todo | 2 |

## Fase 3: Historico reconciliado e operacao segura

- **Objetivo**: fechar historico, reconciliacao, fallback, retirada do heuristico e pacote final de observabilidade/rollback
- **Features incluidas**:
  - Feature 3
- **Gate de saida**: historico resolvivel fica materializado com trilha auditavel, o heuristico residual sai do caminho oficial e a operacao fica pronta para auditoria
- **Criterios de aceite**:
  - backfill e reconciliacao executam sem duplicidade e com artefatos rastreaveis
  - o protocolo de fallback via bronze esta definido e conectado aos artefatos operacionais existentes
  - residuos heuristicos, rollback e evidencias finais estao fechados

### Epicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F3-01 | Feature 3 | todo | 5 |
| EPIC-F3-02 | Feature 3 | todo | 3 |
| EPIC-F3-03 | Feature 3 | todo | 3 |
| EPIC-F3-04 | Feature 3 | todo | 3 |
| EPIC-F3-05 | Feature 3 | todo | 2 |

---

# 14. Epicos

## Epico: Base canonica e writers para leitura confiavel por evento

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: fechar a baseline de `LeadEvento` e os caminhos minimos de escrita que sustentam a leitura confiavel por evento
- **Resultado de Negocio Mensuravel**: a plataforma deixa de depender de relacoes implicitas para materializar o vinculo `lead-evento` necessario a analise etaria
- **Contexto Arquitetural**: reagrupa a fundacao do legado `F1-01`, `F1-02` e `F1-03` como habilitador direto da feature visivel, sem manter arquitetura como eixo principal
- **Definition of Done**:
  - [ ] migration e surface de modelos de `LeadEvento` estao estaveis
  - [ ] submit publico, pipeline Gold e ETL deterministico asseguram o vinculo canonico necessario para a feature

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F1-01-001 | Estabilizar surface de modelo e boot da baseline canonica | 1 | todo | Feature 1 | `ISSUE-F1-01-001` + `ISSUE-F1-01-003` do legado |
| ISSUE-F1-01-002 | Versionar migration de `lead_evento` | 2 | todo | Feature 1 | `ISSUE-F1-01-002` do legado |
| ISSUE-F1-01-003 | Garantir dual-write no submit publico | 2 | done | Feature 1 | `ISSUE-F1-02-001` do legado |
| ISSUE-F1-01-004 | Cobrir duplicata de conversao e invariantes do submit | 1 | done | Feature 1 | `ISSUE-F1-02-002` do legado |
| ISSUE-F1-01-005 | Garantir `LeadEvento` no pipeline Gold | 1 | done | Feature 1 | `ISSUE-F1-03-001` do legado |
| ISSUE-F1-01-006 | Garantir `LeadEvento` no ETL por `evento_nome` | 2 | todo | Feature 1 | `ISSUE-F1-03-002` do legado |

## Epico: Analise etaria no caminho canonico e cobertura executavel

- **ID**: EPIC-F1-02
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: consolidar o endpoint de analise etaria e suas suites sobre a semantica canonica aprovada
- **Resultado de Negocio Mensuravel**: a primeira superficie visivel priorizada volta a ser confiavel para o mesmo evento sem depender de correcoes locais
- **Contexto Arquitetural**: reagrupa cobertura executavel do legado `F1-04` com paridade do consumidor analitico `F3-01`
- **Definition of Done**:
  - [ ] endpoint de analise etaria opera apenas sobre o caminho canonico aprovado
  - [ ] suites e fixtures provam paridade e ausencia de falso vazio

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F1-02-001 | Alinhar fixtures e suites ao modelo canonico | 2 | todo | Feature 1 | `ISSUE-F1-04-001` do legado |
| ISSUE-F1-02-002 | Consolidar a analise etaria no caminho canonico | 2 | todo | Feature 1 | `ISSUE-F3-01-001` do legado |
| ISSUE-F1-02-003 | Validar paridade da analise etaria | 1 | todo | Feature 1 | `ISSUE-F3-01-002` do legado |

## Epico: Dashboard agregado e rankings coerentes por evento

- **ID**: EPIC-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 2
- **Objetivo**: consolidar KPIs, series e rankings de `/dashboard/leads` sobre a mesma leitura canonica
- **Resultado de Negocio Mensuravel**: o dashboard agregado deixa de divergir da analise etaria para o mesmo evento
- **Contexto Arquitetural**: deriva diretamente do legado `F3-02` sem alterar payloads ou UX
- **Definition of Done**:
  - [ ] `/dashboard/leads` usa a mesma base de leitura da Feature 1
  - [ ] rankings e filtros permanecem coerentes para o mesmo evento

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F2-01-001 | Consolidar `/dashboard/leads` e rankings | 2 | todo | Feature 2 | `ISSUE-F3-02-001` do legado |

## Epico: Relatorio agregado coerente por evento

- **ID**: EPIC-F2-02
- **Fase**: F2
- **Feature de Origem**: Feature 2
- **Objetivo**: fechar `/dashboard/leads/relatorio` sobre a mesma semantica canonica dos demais consumidores priorizados
- **Resultado de Negocio Mensuravel**: o relatorio deixa de constituir fonte paralela de verdade para o mesmo evento
- **Contexto Arquitetural**: deriva do legado `F3-02` com foco exclusivo no recorte de relatorio
- **Definition of Done**:
  - [ ] `/dashboard/leads/relatorio` retorna contagens coerentes com as outras superfices priorizadas

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F2-02-001 | Consolidar `/dashboard/leads/relatorio` | 1 | todo | Feature 2 | `ISSUE-F3-02-002` do legado |

## Epico: Contrato frontend e smoke de nao regressao

- **ID**: EPIC-F2-03
- **Fase**: F2
- **Feature de Origem**: Feature 2
- **Objetivo**: travar os consumidores React sobre os contratos consolidados do backend sem redesenho de UX
- **Resultado de Negocio Mensuravel**: o frontend segue funcional enquanto a confiabilidade semantica do backend e consolidada
- **Contexto Arquitetural**: deriva diretamente do legado `F3-03` como fechamento do recorte de consumidores priorizados
- **Definition of Done**:
  - [ ] services e paginas frontend prioritarios seguem operando com o payload atual
  - [ ] existe smoke de nao regressao cobrindo as superfices priorizadas

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F2-03-001 | Travar consumidores frontend e smoke de nao regressao | 2 | todo | Feature 2 | `ISSUE-F3-03-001` do legado |

## Epico: Backfill idempotente multi-origem

- **ID**: EPIC-F3-01
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: materializar historico resolvivel em `LeadEvento` por execucao controlada e reexecutavel
- **Resultado de Negocio Mensuravel**: o historico resolvivel passa a sustentar os dashboards por evento sem duplicidade
- **Contexto Arquitetural**: reaproveita o legado `F2-01`, agora vinculado diretamente a confiabilidade historica da feature
- **Definition of Done**:
  - [ ] runner controlado de backfill esta disponivel
  - [ ] precedencia, upgrade de fonte e idempotencia estao cobertos em teste

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F3-01-001 | Implementar runner idempotente de backfill | 3 | todo | Feature 3 | `ISSUE-F2-01-001` do legado |
| ISSUE-F3-01-002 | Testar precedencia e idempotencia do backfill | 2 | todo | Feature 3 | `ISSUE-F2-01-002` do legado |

## Epico: Reconciliacao manual e evidencias de pendencias historicas

- **ID**: EPIC-F3-02
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: tornar visiveis os casos historicos nao resolvidos e formalizar o fechamento manual rastreavel
- **Resultado de Negocio Mensuravel**: `missing`, `ambiguous` e `manual_reconciled` deixam de ser casos invisiveis para a operacao
- **Contexto Arquitetural**: deriva do legado `F2-02`, mantendo escopo controlado e auditavel
- **Definition of Done**:
  - [ ] relatorio de reconciliacao e emitido com trilha de origem
  - [ ] `manual_reconciled` esta formalizado como caminho minimo de fechamento manual

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F3-02-001 | Gerar relatorio de reconciliacao `missing` e `ambiguous` | 2 | todo | Feature 3 | `ISSUE-F2-02-001` do legado |
| ISSUE-F3-02-002 | Formalizar fechamento `manual_reconciled` | 1 | todo | Feature 3 | `ISSUE-F2-02-002` do legado |

## Epico: Protocolo operacional de fallback via bronze

- **ID**: EPIC-F3-03
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: definir quando usar reprocessamento ou fallback via bronze sem abrir automacao destrutiva nova
- **Resultado de Negocio Mensuravel**: a operacao ganha criterio claro para tratar historico fora do match deterministico
- **Contexto Arquitetural**: deriva do legado `F2-03` e se conecta aos artefatos operacionais ja existentes
- **Definition of Done**:
  - [ ] protocolo de fallback esta definido
  - [ ] protocolo esta amarrado aos artefatos operacionais atuais

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F3-03-001 | Definir criterio operacional de fallback via bronze | 1 | todo | Feature 3 | `ISSUE-F2-03-001` do legado |
| ISSUE-F3-03-002 | Conectar protocolo aos artefatos operacionais do lote | 2 | todo | Feature 3 | `ISSUE-F2-03-002` do legado |

## Epico: Retirada controlada do heuristico residual

- **ID**: EPIC-F3-04
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: eliminar codigo residual de uniao heuristica que nao faca mais parte do caminho oficial
- **Resultado de Negocio Mensuravel**: os consumidores analiticos deixam de ter uma fonte paralela de verdade fora da semantica canonica
- **Contexto Arquitetural**: deriva do legado `F4-01` e depende do fechamento visivel das Features 1 e 2
- **Definition of Done**:
  - [ ] residuos heuristicas e codigo morto fora do caminho oficial foram removidos

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F3-04-001 | Remover heuristicos residuais e codigo morto | 3 | todo | Feature 3 | `ISSUE-F4-01-001` do legado |

## Epico: Observabilidade, rollback e auditoria final

- **ID**: EPIC-F3-05
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: consolidar o pacote operacional final para auditoria da remediacao
- **Resultado de Negocio Mensuravel**: o projeto termina com runbook, metricas e evidencias adequadas para o gate final
- **Contexto Arquitetural**: deriva do legado `F4-02`, sem alterar payload ou UX
- **Definition of Done**:
  - [ ] runbook de rollback esta descrito
  - [ ] metricas e evidencias finais estao consolidadas para auditoria

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature | Origem complementar |
|----------|------|-----|--------|---------|---------------------|
| ISSUE-F3-05-001 | Fechar observabilidade, rollback e pacote de auditoria | 2 | todo | Feature 3 | `ISSUE-F4-02-001` do legado |

---

# 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| `dashboard-leads` | modulo legado arquivado | `PROJETOS/FEITO/DASHBOARD-LEADS/` | evidencia complementar para backlog, status herdado e rastreabilidade | archived-support |
| `pipeline-etl-importacao` | data pipeline | NPBB | writers canonicos, backfill e fallback via bronze | active |
| `ticketing-importacao-de-ingressos` | integracao | NPBB | origem de leads diretos do evento e insumo para reconciliacao | active |
| `frontend-dashboard` | frontend-web | NPBB | consumidores priorizados e smoke de nao regressao | active |
