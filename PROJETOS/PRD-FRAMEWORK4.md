---
doc_id: "PRD-FRAMEWORK3.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "FRAMEWORK3"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "governanca"
criticality: "alta"
data_sensitivity: "interna"
integrations:
  - "framework-governanca"
  - "agent-orchestrator"
  - "npbb-crud"
change_type: "nova-capacidade"
audit_rigor: "elevated"
---

# PRD - FRAMEWORK3

> Adaptado ao paradigma `delivery-first` / `feature-first` do FRAMEWORK4.
> O eixo principal deste PRD sao as features entregaveis; arquitetura aparece
> como impacto e capacidade habilitadora, nao como organizacao principal.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-FRAMEWORK3.md](./INTAKE-FRAMEWORK3.md)
- **Versao do intake**: 1.1
- **Data de criacao**: 2026-03-18
- **PRD derivado** (se aplicavel): nao_aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: FRAMEWORK3
- **Tese em 1 frase**: converter o framework documental de projetos em uma operacao assistida por IA, organizada por features demonstraveis e suportada por persistencia, CRUD e orquestracao.
- **Valor esperado em 3 linhas**:
  - reduzir o trabalho manual de criar e manter artefatos de planejamento e execucao.
  - permitir que o PM acompanhe e aprove um fluxo inteiro de projeto com visibilidade, gates e automacao progressiva.
  - transformar o historico operacional em ativo auditavel e reutilizavel para melhoria continua e treinamento futuro.

## 2. Problema ou Oportunidade

- **Problema atual**: o framework atual exige montagem manual de artefatos e controle artesanal da progressao do projeto, com pouca centralizacao de historico e baixa automacao.
- **Evidencia do problema**: o fluxo depende de copiar arquivos da pasta `COMUM/`, preencher frontmatter, manter aprovacoes sucessivas manualmente e consolidar contexto de execucao fora de um sistema persistente.
- **Custo de nao agir**: o PM continua preso a trabalho operacional repetitivo, o framework nao escala bem e o historico fica subutilizado para auditoria e treinamento.
- **Por que agora**: o contexto de governanca ja esta maduro o suficiente para migrar de um planejamento `architecture-first` para um planejamento `feature-first`, preservando a disciplina documental existente.

## 3. Publico e Operadores

- **Usuario principal**: PM responsavel por abrir, aprovar e acompanhar projetos
- **Usuario secundario**: engenheiros e agentes IA que executam issues e tasks
- **Operador interno**: AgentOrchestrator e subagentes
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: conduzir o ciclo de um projeto do intake ate a auditoria de fase com menos operacao manual e mais rastreabilidade.
- **Jobs secundarios**:
  - consultar o estado do projeto em qualquer nivel hierarquico
  - revisar aprovacoes, artefatos e execucoes em uma linha do tempo auditavel
  - configurar e aumentar a autonomia operacional de forma controlada
- **Tarefa atual que sera substituida**: copia/renomeacao de arquivos Markdown e orquestracao manual de gates, contexto e historico

## 5. Escopo

### Dentro

- intake, PRD e planejamento hierarquico assistidos a partir de features
- CRUD persistente para projetos e artefatos de governanca
- execucao orquestrada de issues e tasks com gates configuraveis
- revisao e auditoria formal integradas ao fluxo
- rastreabilidade operacional completa de prompts, outputs, aprovacoes e evidencias

### Fora

- substituicao total do sistema documental legado
- fine-tuning real de LLM nesta fase
- mobile e multi-tenancy avancado

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: reduzir em mais de 70% o esforco manual para abrir, planejar e operar projetos no framework.
- **Metricas leading**: quantidade de projetos iniciados via FRAMEWORK3, percentual de etapas automatizadas, quantidade de registros operacionais persistidos.
- **Metricas lagging**: tempo medio para abrir um projeto ate issue executavel, taxa de auditorias aprovadas, satisfacao do PM com o fluxo.
- **Criterio minimo para considerar sucesso**: o sistema consegue levar um projeto do intake aprovado ate a execucao auditavel de uma issue com historico e rastreabilidade completos.

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: manter o stack atual do NPBB e a coexistencia com a estrutura `PROJETOS/`.
- **Restricoes operacionais**: obedecer ao algoritmo de negocio e aos arquivos `GOV-*`, `SESSION-*` e `TEMPLATE-*`.
- **Restricoes legais ou compliance**: nao_aplicavel
- **Restricoes de prazo**: priorizar MVP funcional em iteracoes curtas
- **Restricoes de design ou marca**: manter o padrao de governanca documental vigente

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: backend FastAPI, frontend React/Vite, banco PostgreSQL, dashboard admin e ambiente de agentes
- **Sistemas externos impactados**: nenhum
- **Dados de entrada necessarios**: intake aprovado, governanca canonica, algoritmo do negocio e contexto do projeto fornecido pelo PM
- **Dados de saida esperados**: artefatos Markdown, registros estruturados no banco, timeline de execucao e trilha de auditoria

## 9. Arquitetura Geral do Projeto

> Visao geral de impacto arquitetural. O detalhamento principal aparece nas features.

- **Backend**: servicos para CRUD, planejamento, orquestracao, revisao e auditoria
- **Frontend**: modulo admin integrado ao dashboard para navegacao, aprovacao e consulta de historico
- **Banco/migracoes**: tabelas para artefatos, execucoes, aprovacoes, auditorias e estados do projeto
- **Observabilidade**: logs estruturados e historico auditavel de eventos
- **Autorizacao/autenticacao**: reutilizar auth atual do NPBB com guardas administrativas
- **Rollout**: incremental, coexistindo com o fluxo documental legado

## 10. Riscos Globais

- **Risco de produto**: o projeto virar uma reorganizacao tecnica sem entregar valor perceptivel ao PM.
- **Risco tecnico**: complexidade de sincronizar governanca documental, persistencia e orquestracao sem regressao.
- **Risco operacional**: gates de aprovacao mal calibrados gerarem automacao insegura ou burocracia excessiva.
- **Risco de dados**: historico salvo sem granularidade suficiente para auditoria e treinamento.
- **Risco de adocao**: baixa confianca no sistema se a rastreabilidade nao for clara.

## 11. Nao-Objetivos

- reescrever o framework existente descartando os artefatos Markdown
- tratar banco, backend ou frontend como macro-entregas independentes do valor entregue
- automatizar irrestritamente todos os gates sem politica clara de controle

---

# 12. Features do Projeto

> Cada feature abaixo representa um comportamento demonstravel para o PM.
> As camadas tecnicas entram como impacto de implementacao.

## Feature 1: Intake e PRD assistidos com aprovacao governada

### Objetivo de Negocio

Eliminar a abertura manual e inconsistente de projetos, garantindo que todo projeto
comece com intake e PRD padronizados, rastreaveis e prontos para decomposicao.

### Comportamento Esperado

O PM consegue informar o contexto do projeto, receber um intake estruturado,
aprova-lo, gerar um PRD coerente com a governanca e sair com base suficiente
para planejamento posterior.

### Criterios de Aceite

- [ ] o sistema gera intake completo com rastreabilidade, lacunas conhecidas e checklist de prontidao para PRD
- [ ] o sistema gera PRD derivado do intake aprovado sem perder taxonomias nem origem
- [ ] intake e PRD registram aprovacao humana e versao dos artefatos gerados

### Dependencias com Outras Features

- Feature 5: persistencia e trilha operacional para armazenar aprovacoes e artefatos

### Riscos Especificos

- intake gerar hipoteses como fatos
- PRD manter organizacao architecture-first e bloquear o planejamento posterior

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para projeto, intake, PRD, versoes e aprovacoes
2. **API**: endpoints para criar, revisar, aprovar e consultar intake/PRD
3. **UI**: formularios e telas de aprovacao assistida
4. **Testes**: cobertura de derivacao intake -> PRD, validacao de frontmatter e rastreabilidade

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | `projects`, `intakes`, `prds`, `approvals` | versionamento, origem, status e relacao entre artefatos |
| Backend | CRUD e geracao assistida | contratos para rascunho, aprovacao e materializacao de artefatos |
| Frontend | abertura e aprovacao de projeto | formularios, review diff e timeline de decisao |
| Testes | suites de intake/PRD | validacao do fluxo HITL e da consistencia dos documentos |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar entidades e estados de intake, PRD e aprovacao | 3 | - |
| T2 | Expor fluxo CRUD e geracao assistida de intake/PRD | 5 | T1 |
| T3 | Entregar UI de revisao e aprovacao com historico | 3 | T2 |

---

## Feature 2: Planejamento hierarquico rastreavel a partir de features

### Objetivo de Negocio

Fazer o planejamento de projeto nascer de entregas demonstraveis, e nao de camadas
tecnicas, permitindo decomposicao segura em fases, epicos, issues e tasks.

### Comportamento Esperado

Depois do PRD aprovado, o PM consegue gerar planejamento hierarquico em que cada
fase entrega features explicitas e cada epico/issue preserva `Feature de Origem`.

### Criterios de Aceite

- [ ] o PRD exibe features com criterios de aceite verificaveis e dependencias declaradas
- [ ] cada fase lista claramente quais features entrega e qual gate de saida a valida
- [ ] cada epico e issue conseguem repetir explicitamente o ID de feature definido no PRD

### Dependencias com Outras Features

- Feature 1: intake e PRD aprovados
- Feature 5: persistencia para armazenar hierarquia, status e historico

### Riscos Especificos

- features mal definidas virarem pseudo-camadas tecnicas
- fases serem organizadas por backend/frontend/banco em vez de comportamento entregue

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para fases, epicos, issues, tasks e relacao com features
2. **API**: contratos para decomposicao hierarquica e consulta da rastreabilidade
3. **UI**: navegacao hierarquica com filtros por feature e fase
4. **Testes**: validacao de rastreabilidade e bloqueios quando o PRD estiver insuficiente

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | `phases`, `epics`, `issues`, `tasks`, `feature_links` | IDs canonicos, dependencias e origem por feature |
| Backend | planejador hierarquico | geracao de fases, epicos, issues e tasks a partir do PRD |
| Frontend | visao de mapa do projeto | navegacao por fase, epico, issue e feature |
| Testes | suites de planejamento | consistencia `feature -> fase -> epico -> issue` |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Definir contratos e persistencia da hierarquia vinculada a features | 3 | - |
| T2 | Implementar geracao assistida de fases, epicos e issues rastreaveis | 5 | T1 |
| T3 | Entregar visao administrativa com filtros por feature | 3 | T2 |

---

## Feature 3: Execucao orquestrada de issues e tasks

### Objetivo de Negocio

Reduzir a operacao manual de execucao de projeto, permitindo que issues elegiveis
sejam executadas com contexto correto, sequenciamento e controle de autonomia.

### Comportamento Esperado

O sistema seleciona a proxima unidade executavel, monta o contexto da issue/task,
aciona subagentes, acompanha o progresso e encerra a issue conforme o workflow
governado.

### Criterios de Aceite

- [ ] o orquestrador identifica a proxima task elegivel sem violar dependencias e gates
- [ ] cada execucao registra contexto, entradas, saidas, status e evidencias relevantes
- [ ] o PM consegue configurar quando a execucao exige confirmacao humana e quando pode seguir automaticamente

### Dependencias com Outras Features

- Feature 2: hierarquia planejada e tasks elegiveis
- Feature 5: trilha operacional persistida

### Riscos Especificos

- execucao automatica fora de ordem
- contexto insuficiente para subagentes concluirem a task com seguranca

### Fases de Implementacao

1. **Modelagem e Migration**: estados de execucao, work orders e relacoes com tasks/issues
2. **API**: selecao de proxima unidade, disparo e acompanhamento de execucao
3. **UI**: painel de status operacional e proxima acao recomendada
4. **Testes**: elegibilidade, sequenciamento e tolerancia a bloqueios

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | `agent_executions`, `work_orders`, estados de task/issue | historico de execucao, evidencias e fechamento |
| Backend | AgentOrchestrator | elegibilidade, montagem de contexto e coordenacao de subagentes |
| Frontend | timeline operacional | status da issue, proxima acao e visibilidade de execucoes |
| Testes | suites de orquestracao | sequenciamento, gates HITL e falhas de execucao |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Persistir work orders, execucoes e estados de elegibilidade | 3 | - |
| T2 | Implementar orquestracao sequencial de tasks por issue | 5 | T1 |
| T3 | Expor painel de acompanhamento e controle de autonomia | 3 | T2 |

---

## Feature 4: Revisao e auditoria com gates formais

### Objetivo de Negocio

Garantir que a automacao preserve qualidade e governanca por meio de revisao
pos-issue e auditoria de fase com vereditos rastreaveis.

### Comportamento Esperado

Ao fim de uma issue ou fase, o sistema prepara o contexto de revisao/auditoria,
registra veredito, abre follow-ups quando necessario e impede avancos indevidos.

### Criterios de Aceite

- [ ] cada issue concluida pode gerar revisao formal com veredito e destino claro
- [ ] cada fase possui gate de auditoria com resultado `go` ou `hold`
- [ ] follow-ups de auditoria ficam vinculados ao artefato de origem e ao destino decidido

### Dependencias com Outras Features

- Feature 3: execucoes concluiveis
- Feature 5: persistencia de evidencias, vereditos e follow-ups

### Riscos Especificos

- revisao virar etapa informal sem efeito sobre o estado do projeto
- auditoria abrir follow-ups sem rastreabilidade de origem

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para reviews, auditorias, vereditos e follow-ups
2. **API**: geracao de contexto de revisao, registro de veredito e abertura de follow-up
3. **UI**: telas de review, auditoria e consulta de pendencias
4. **Testes**: transicoes de estado, regras de gate e destino de follow-ups

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | `reviews`, `audit_logs`, `follow_ups` | vereditos, destino, artefato de origem e historico |
| Backend | servicos de review e auditoria | regras de gate, hold/go e abertura de remediacao |
| Frontend | telas de governanca final | aprovacao, hold, motivos e acoes seguintes |
| Testes | suites de auditoria | regras de bloqueio, retomada e encadeamento de follow-up |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar vereditos, auditorias e follow-ups rastreaveis | 3 | - |
| T2 | Implementar fluxo de review pos-issue e gate de fase | 5 | T1 |
| T3 | Expor consultas e acoes de governanca para o PM | 3 | T2 |

---

## Feature 5: Persistencia e rastreabilidade operacional

### Objetivo de Negocio

Centralizar o historico operacional do framework para permitir auditoria,
analytics, depuracao de fluxo e futuro treinamento de modelos.

### Comportamento Esperado

O PM consegue inspecionar quem fez o que, em qual ordem, com qual contexto,
qual veredito e qual artefato foi produzido em cada etapa do projeto.

### Criterios de Aceite

- [ ] cada etapa relevante do fluxo registra entradas, saidas, aprovacoes, status e timestamps
- [ ] o sistema permite consultar timeline de projeto, issue ou task sem depender apenas de arquivos soltos
- [ ] os dados persistidos sao suficientes para auditoria formal e para curadoria futura de dataset

### Dependencias com Outras Features

- nao_aplicavel; esta feature habilita as demais

### Riscos Especificos

- historico incompleto ou dificil de consultar
- excesso de acoplamento entre persistencia e formato textual dos artefatos

### Fases de Implementacao

1. **Modelagem e Migration**: entidades transversais para eventos, aprovacoes, artefatos e timeline
2. **API**: endpoints de consulta, timeline e sincronizacao artefato <-> estado
3. **UI**: visao consolidada de historico e proxima acao
4. **Testes**: integridade de eventos, precedencia e sincronizacao

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | tabelas transversais de timeline e artefatos | storage auditavel, relacional e consultavel |
| Backend | sincronizacao e consulta operacional | leitura/gravação de historico e exposicao de timeline |
| Frontend | timeline e status consolidado | filtros por projeto, fase, issue, task e execucao |
| Testes | suites transversais | consistencia de historico, ordering e integridade |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Definir modelo de historico, eventos e sincronizacao de artefatos | 3 | - |
| T2 | Implementar consulta e persistencia de timeline operacional | 5 | T1 |
| T3 | Integrar timeline ao modulo admin e aos fluxos de aprovacao | 3 | T2 |

---

# 13. Estrutura de Fases

> As fases abaixo agrupam entregas por valor e dependencia entre features.
> Nenhuma fase e organizada por camada tecnica isolada.

## Fase 1: Fundacao da experiencia assistida

- **Objetivo**: permitir que um projeto nasca com intake, PRD e base de rastreabilidade consistentes.
- **Features incluidas**:
  - Feature 1
  - Feature 5
- **Gate de saida**: um projeto consegue gerar intake e PRD aprovaveis com historico persistido e timeline consultavel.
- **Criterios de aceite**: intake e PRD aprovados, historico consultavel e frontmatter completo.

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F1-01 | Feature 1 | todo | 11 |
| EPIC-F1-02 | Feature 5 | todo | 11 |

## Fase 2: Planejamento governado por features

- **Objetivo**: decompor o PRD aprovado em fases, epicos, issues e tasks rastreaveis.
- **Features incluidas**:
  - Feature 2
- **Gate de saida**: o projeto exibe planejamento hierarquico completo com `Feature de Origem` explicita.
- **Criterios de aceite**: rastreabilidade `feature -> fase -> epico -> issue` visivel e valida.

### Epicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F2-01 | Feature 2 | todo | 11 |

## Fase 3: Execucao governada e gates de qualidade

- **Objetivo**: executar issues com orquestracao, review e auditoria formais.
- **Features incluidas**:
  - Feature 3
  - Feature 4
- **Gate de saida**: uma issue pode ser executada, revisada e auditada com vereditos rastreaveis.
- **Criterios de aceite**: execucao sequencial, review pos-issue e auditoria de fase funcionando em fluxo integrado.

### Epicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F3-01 | Feature 3 | todo | 11 |
| EPIC-F3-02 | Feature 4 | todo | 11 |

---

# 14. Epicos

> Cada epico abaixo aponta explicitamente para a feature de origem.

## Epico: Intake e PRD assistidos

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: permitir abertura e aprovacao governada de intake e PRD.
- **Resultado de Negocio Mensuravel**: reduzir drasticamente o tempo do PM para abrir um projeto com documentacao inicial valida.
- **Contexto Arquitetural**: CRUD de artefatos iniciais, aprovacoes, versoes e UI de revisao.
- **Definition of Done**:
  - [ ] intake e PRD podem ser criados, aprovados e consultados com historico

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F1-01-001 | Implementar intake assistido com gate de aprovacao | 5 | todo | Feature 1 |
| ISSUE-F1-01-002 | Implementar geracao de PRD com rastreabilidade do gate | 6 | todo | Feature 1 |

---

## Epico: Timeline e artefatos canonicos

- **ID**: EPIC-F1-02
- **Fase**: F1
- **Feature de Origem**: Feature 5
- **Objetivo**: persistir trilha operacional e sincronizar artefatos com estado do projeto.
- **Resultado de Negocio Mensuravel**: permitir auditoria e consulta centralizada do historico do projeto.
- **Contexto Arquitetural**: tabelas transversais, sincronizacao Markdown/banco e timeline administrativa.
- **Definition of Done**:
  - [ ] timeline e historico operacional estao disponiveis por projeto

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F1-02-001 | Persistir prompts, outputs, aprovacoes e evidencias do planejamento | 5 | todo | Feature 5 |
| ISSUE-F1-02-002 | Materializar artefatos Markdown e estado de sincronizacao | 6 | todo | Feature 5 |

---

## Epico: Planejamento hierarquico orientado a features

- **ID**: EPIC-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 2
- **Objetivo**: gerar fases, epicos, issues e tasks a partir do PRD com rastreabilidade de feature.
- **Resultado de Negocio Mensuravel**: o PM consegue decompor o projeto inteiro sem reorganizar manualmente o plano por camada tecnica.
- **Contexto Arquitetural**: contratos de planejamento, IDs canonicos e navegacao hierarquica.
- **Definition of Done**:
  - [ ] fases, epicos, issues e tasks refletem as features do PRD

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F2-01-001 | Implementar planejamento assistido de fases e epicos com feature de origem | 5 | todo | Feature 2 |
| ISSUE-F2-01-002 | Implementar planejamento assistido de issues e tasks com rastreabilidade de feature | 6 | todo | Feature 2 |

---

## Epico: Execucao orquestrada de issues

- **ID**: EPIC-F3-01
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: selecionar unidades executaveis, montar work order e coordenar execucao sequencial.
- **Resultado de Negocio Mensuravel**: reduzir a operacao manual para executar uma issue do projeto.
- **Contexto Arquitetural**: orchestrator, work orders, estados de task e timeline de execucao.
- **Definition of Done**:
  - [ ] uma issue pode ser executada sequencialmente com contexto e evidencias registradas

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F3-01-001 | Selecionar proxima task elegivel e montar work order executavel | 5 | todo | Feature 3 |
| ISSUE-F3-01-002 | Registrar execucao sequencial e fechamento por task | 6 | todo | Feature 3 |

---

## Epico: Review e auditoria com veredito canonico

- **ID**: EPIC-F3-02
- **Fase**: F3
- **Feature de Origem**: Feature 4
- **Objetivo**: consolidar revisao pos-issue e auditoria de fase com follow-ups rastreaveis.
- **Resultado de Negocio Mensuravel**: impedir avancos sem gate de qualidade e permitir remediacao estruturada.
- **Contexto Arquitetural**: reviews, auditorias, vereditos e follow-ups.
- **Definition of Done**:
  - [ ] review pos-issue e auditoria de fase conseguem bloquear ou liberar a progressao do projeto

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F3-02-001 | Preparar review pos-issue com veredito canonico | 5 | todo | Feature 4 |
| ISSUE-F3-02-002 | Preparar auditoria de fase com gate persistido e follow-ups | 6 | todo | Feature 4 |

---

# 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| Governanca documental (`GOV-*`, `SESSION-*`, `TEMPLATE-*`) | Documento | Framework atual | define regras e formatos que o sistema deve obedecer | required |
| Algoritmo do negocio em [PROJETOS/Algoritmo.md](../Algoritmo.md) | Documento | Projeto atual | define sequencia operacional e gates do fluxo | required |
