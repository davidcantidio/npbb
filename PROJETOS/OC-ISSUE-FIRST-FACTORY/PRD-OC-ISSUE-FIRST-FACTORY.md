---
doc_id: "PRD-OC-ISSUE-FIRST-FACTORY.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-24"
project: "OC-ISSUE-FIRST-FACTORY"
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
data_sensitivity: "restrita"
integrations:
- "planner"
- "telegram-bridge"
- "github"
- "scripts/criar_projeto.py"
- "bin/sync-openclaw-projects-db.sh"
- "openclaw-projects.sqlite"
- "PROJETOS/COMUM"
change_type: "nova-capacidade"
audit_rigor: "elevated"
---

# PRD - OC-ISSUE-FIRST-FACTORY

> Origem: [INTAKE-OC-ISSUE-FIRST-FACTORY.md](INTAKE-OC-ISSUE-FIRST-FACTORY.md)
>
> Este PRD descreve a capability do framework que recebe uma ideia de novo
> projeto via Telegram, resolve o repositorio alvo, gera `INTAKE` e `PRD`
> com HITL e materializa a arvore `issue-first` ate task com gates do agente
> senior e preambulo socratico.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-OC-ISSUE-FIRST-FACTORY.md](INTAKE-OC-ISSUE-FIRST-FACTORY.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-24
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: OC-ISSUE-FIRST-FACTORY
- **Tese em 1 frase**: transformar uma ideia recebida via Telegram em um projeto
  novo, governado pelo framework desde o bootstrap do repositorio ate a arvore
  `issue-first` pronta para execucao.
- **Valor esperado em 3 linhas**:
  - reduzir o atrito para abrir projetos novos no OpenClaw
  - unificar Telegram, GitHub, scaffold, `INTAKE`, `PRD` e planning
  - preservar HITL, gates seniores e autoridade do Markdown mesmo com indice
    SQLite derivado

## 2. Problema ou Oportunidade

- **Problema atual**: o framework tem componentes para bridge Telegram,
  scaffold documental, sync SQLite e prompts de planejamento, mas ainda nao
  oferece uma capability unificada para abrir um projeto novo ponta a ponta.
- **Evidencia do problema**: hoje o PM ainda precisa coordenar manualmente a
  ideia inicial, o repositorio alvo, o scaffold, o `INTAKE`, o `PRD` e a
  decomposicao `issue-first`.
- **Custo de nao agir**: novos projetos continuam surgindo com drift entre
  chat, GitHub, docs e planning, aumentando retrabalho e risco de escopo mal
  fatiado.
- **Por que agora**: o bridge Telegram, a topologia `planner/builder/auditor`,
  o scaffold e o indice derivado ja existem no repo e permitem formalizar essa
  capability como backlog proprio.

## 3. Publico e Operadores

- **Usuario principal**: PM que quer abrir um novo projeto sem sair do fluxo
  conversacional do Telegram.
- **Usuario secundario**: mantenedor do framework que precisa garantir que
  projetos novos nascam em conformidade com `PROJETOS/COMUM`.
- **Operador interno**: `planner`, bridge Telegram, integracao GitHub,
  `scripts/criar_projeto.py`, sync do indice SQLite derivado e agente senior.
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: descrever uma nova iniciativa em linguagem natural e obter
  um projeto novo, com repo, `INTAKE`, `PRD` e arvore `issue-first` prontos para
  o fluxo normal do framework.
- **Jobs secundarios**:
  - resolver se o repositorio sera existente ou novo
  - criar scaffold canonico sem drift de docs e caminhos
  - garantir gates humanos de `INTAKE` e `PRD`
  - garantir gates do agente senior na decomposicao `issue-first`
  - aplicar um preambulo socratico antes de cada handoff relevante
- **Tarefa atual que sera substituida**: coordenar manualmente abertura de
  projeto, repo, scaffold, intake, PRD e planning

## 5. Escopo

### Dentro

- ingresso de novo projeto via Telegram no `planner`
- contrato minimo do pedido inicial:
  - `project_name`
  - `project_idea`
  - `repo_mode`
  - `repo_url` opcional
- repo existente ou repo novo com HITL
- bootstrap do repositorio alvo com scaffold canonico
- geracao de `INTAKE` com gate humano
- geracao de `PRD` com gate humano
- materializacao de fases, epicos, issues, sprints e tasks
- contrato de handoff socratico em planning, review, audit e execucao
- sync do indice SQLite derivado sem promover SQLite a autoridade

### Fora

- implementacao das tasks do projeto alvo
- criacao de repo sem aprovacao explicita quando houver acao externa
- armazenamento de secrets em Git ou em prompts persistidos
- dashboard de observabilidade completo
- substituir Markdown por SQLite como fonte normativa

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: reduzir o tempo entre a ideia inicial e um projeto
  novo governado pelo framework, sem sacrificar a cadeia normativa.
- **Metricas leading**:
  - tempo entre o pedido no Telegram e o `INTAKE` gerado
  - tempo entre `INTAKE` aprovado e `PRD` gerado
  - tempo entre `PRD` aprovado e arvore `issue-first` materializada ate task
  - percentual de handoffs com preambulo socratico presente
- **Metricas lagging**:
  - reducao de retrabalho manual na abertura de projetos
  - menos drift entre repositorio alvo, docs e indice derivado
  - menos correcoes estruturais apos o primeiro planning
- **Criterio minimo para considerar sucesso**: a partir de um pedido via
  Telegram, o PM chega a um repositorio alvo com `INTAKE` e `PRD` aprovados e
  arvore `issue-first` pronta para o fluxo de implementacao, sem vazar secrets
  e sem deslocar a autoridade do Markdown.

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**:
  - reutilizar o bridge Telegram atual e o `planner` ja existente
  - reutilizar `scripts/criar_projeto.py` como base do scaffold
  - manter SQLite como indice derivado/local, nunca como fonte normativa
- **Restricoes operacionais**:
  - `repo_mode=create` exige HITL explicito antes da acao externa
  - `INTAKE` e `PRD` continuam exigindo aprovacao humana
  - apos o PRD, o planning segue gates do agente senior sem checkpoints humanos
  - execucao das tasks do projeto alvo so comeca depois da arvore materializada
- **Restricoes legais ou compliance**:
  - tokens de GitHub e Telegram permanecem fora do Git
  - prompts persistidos nao podem registrar segredos
- **Restricoes de prazo**:
  - v1 encerra na arvore `issue-first` ate task; a implementacao do projeto
    alvo e tratada em outro escopo
- **Restricoes de design ou marca**:
  - manter o contrato conversacional existente do bridge Telegram

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**:
  - `planner`
  - `telegram-bridge`
  - `scripts/criar_projeto.py`
  - `bin/sync-openclaw-projects-db.sh`
  - wrappers `SESSION-*`
  - indice `openclaw-projects.sqlite`
- **Sistemas externos impactados**:
  - GitHub, quando houver repo novo ou repo existente remoto
- **Dados de entrada necessarios**:
  - `project_name`
  - `project_idea`
  - `repo_mode`
  - `repo_url` opcional
  - aprovacao humana do `INTAKE`
  - aprovacao humana do `PRD`
- **Dados de saida esperados**:
  - repositorio alvo resolvido
  - scaffold canonico do projeto
  - `INTAKE` persistido
  - `PRD` persistido
  - fases, epicos, issues, sprints e tasks
  - indice derivado sincronizado

## 9. Arquitetura Geral do Projeto

> Visao geral de impacto arquitetural (detalhes por feature na secao Features)

- **Backend**:
  - orquestracao do pedido inicial no `planner`
  - adaptador do repositorio alvo e do scaffold
  - geracao documental de `INTAKE`, `PRD` e planning
- **Frontend**:
  - interface conversacional via Telegram com prompts de ajuste e aprovacao
- **Banco/migracoes**:
  - sem banco canonico novo
  - uso de Markdown versionado no projeto alvo
  - SQLite derivado para indexacao e consulta, fora do Git
- **Observabilidade**:
  - progresso e handoffs podem usar o feed host-side existente
  - falhas devem deixar trilha suficiente para reproduzir o problema
- **Autorizacao/autenticacao**:
  - GitHub e Telegram continuam dependentes de credenciais locais fora do Git
- **Rollout**:
  - piloto com um projeto novo canario, depois generalizacao para novos projetos

## 10. Riscos Globais

- **Risco de produto**: uma ideia inicial vaga pode gerar `INTAKE` pobre e
  induzir planning ruim.
- **Risco tecnico**: drift entre Telegram, repo alvo, scaffold e indice derivado.
- **Risco operacional**: repo novo criado com parametros errados ou sync parcial
  entre Markdown e SQLite.
- **Risco de dados**: vazamento de secrets ou promocao de informacao derivada a
  canonica.
- **Risco de adocao**: o preambulo socratico pode virar ritual decorativo se nao
  estiver ligado ao objetivo subjacente do handoff.

## 11. Nao-Objetivos

- nao implementar as tasks do projeto alvo
- nao remover os gates humanos de `INTAKE` e `PRD`
- nao remover os gates do agente senior no planning
- nao versionar o SQLite do projeto alvo
- nao expandir o escopo para dashboard ou observabilidade completa

## 12. Features do Projeto

## Feature 1: Ingresso Telegram do novo projeto

#### Objetivo de Negocio

Permitir que o PM abra um projeto novo pelo canal ja operacional de Telegram sem
precisar preparar manualmente um pacote tecnico fora do fluxo.

#### Comportamento Esperado

O `planner` recebe uma mensagem inicial, normaliza o pedido em um contrato
minimo e orienta o proximo passo sem perder a natureza conversacional do canal.

#### Criterios de Aceite

- [ ] O fluxo aceita `project_name`, `project_idea`, `repo_mode` e `repo_url`
  opcional no pedido inicial.
- [ ] Nomes invalidos ou ambiguos geram follow-up objetivo antes de qualquer
  acao material.
- [ ] `repo_mode=create` entra em trilha de HITL explicito.
- [ ] O pedido inicial fica rastreavel para a geracao do `INTAKE`.

#### Dependencias com Outras Features

- nenhuma

#### Riscos Especificos

- briefing insuficiente ou ambiguidade no nome do projeto

#### Contrato Minimo do Pedido Inicial

| Campo | Obrigatorio | Regra |
|---|---|---|
| `project_name` | sim | nome canonico do projeto |
| `project_idea` | sim | descricao do objetivo em linguagem natural |
| `repo_mode` | sim | `existing` ou `create` |
| `repo_url` | nao | obrigatorio quando `repo_mode=existing` |

#### Fases de Implementacao

1. Normalizar o pedido inicial.
2. Validar nome e modo de repositorio.
3. Pedir esclarecimentos objetivos quando necessario.
4. Testar mensagens validas e invalidas.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | indice derivado | pedido inicial e docs posteriores sincronizados em SQLite sem virar autoridade |
| Backend | planner + bridge | normalizacao do pedido e roteamento do fluxo |
| Frontend | Telegram | prompts de follow-up e confirmacao |
| Testes | contrato conversacional | validacao de campos obrigatorios e cenarios invalidos |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Definir contrato minimo do pedido inicial | 2 | - |
| T2 | Roteiar `repo_mode` e follow-ups objetivos no Telegram | 3 | T1 |
| T3 | Validar cenarios invalidos e confirmacoes minimas | 2 | T2 |

## Feature 2: Bootstrap do repositorio alvo e scaffold canonico

#### Objetivo de Negocio

Garantir que o projeto novo nasca em um repositorio alvo coerente com o
framework, sem bootstrap manual e sem transformar SQLite em artefato canonico.

#### Comportamento Esperado

O fluxo vincula um repo existente ou cria um repo novo com HITL, aplica o
scaffold canonico e sincroniza o indice derivado.

#### Criterios de Aceite

- [ ] `repo_mode=existing` usa a `repo_url` informada e segue sem criar repo novo.
- [ ] `repo_mode=create` apresenta o plano de criacao e so executa depois de
  aprovacao explicita.
- [ ] O repositorio alvo recebe scaffold canonico com `INTAKE`, `PRD`,
  wrappers `SESSION-*` e bootstrap `issue-first`.
- [ ] O sync SQLite ocorre como derivacao local do Markdown, sem versionar o DB.

#### Dependencias com Outras Features

- Feature 1: pedido inicial normalizado

#### Riscos Especificos

- drift entre repositorio remoto, scaffold local e indice derivado

#### Fases de Implementacao

1. Resolver repo existente ou plano de repo novo.
2. Bootstrapar o repositorio alvo.
3. Gerar scaffold canonico.
4. Sincronizar o indice derivado e validar autoridade do Markdown.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | SQLite derivado | sync apos bootstrap sem versionar o arquivo |
| Backend | scaffold e adapter GitHub | bootstrap do repo alvo e execucao do `criar_projeto.py` |
| Frontend | Telegram | mensagens de aprovacao para repo novo |
| Testes | bootstrap canario | cenarios repo existente, repo novo e sync derivado |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Resolver adaptador de repo existente ou novo com HITL | 3 | - |
| T2 | Integrar scaffold canonico ao repositorio alvo | 5 | T1 |
| T3 | Sincronizar indice derivado e validar autoridade do Markdown | 3 | T2 |

## Feature 3: Intake inicial com aprovacao humana

#### Objetivo de Negocio

Transformar a ideia inicial em um `INTAKE` estruturado e aprovavel antes de
qualquer PRD ou planning.

#### Comportamento Esperado

O `planner` gera uma primeira versao do `INTAKE`, o PM ajusta ou aprova, e o
fluxo nao avanca enquanto o gate nao estiver satisfeito.

#### Criterios de Aceite

- [ ] O `INTAKE` nasce do contrato inicial e do contexto do repo alvo.
- [ ] O PM consegue responder com aprovacao ou ajuste sem perder o contexto.
- [ ] O gate `Intake -> PRD` continua humano e explicito.
- [ ] O projeto nao avanca para PRD enquanto o `INTAKE` estiver insuficiente.

#### Dependencias com Outras Features

- Feature 1: pedido inicial normalizado
- Feature 2: repositorio alvo e scaffold prontos

#### Riscos Especificos

- intake excessivamente genrico por falta de densidade da ideia inicial

#### Fases de Implementacao

1. Derivar o intake inicial a partir da ideia e do modo de repositorio.
2. Persistir o rascunho no repositorio alvo.
3. Coletar ajuste ou aprovacao do PM.
4. Bloquear avancos quando o intake estiver inseguro.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | indice derivado | intake novo sincronizado para consulta |
| Backend | planner documental | geracao e persistencia do `INTAKE` |
| Frontend | Telegram | prompt de aprovacao e ajustes |
| Testes | contrato do gate | geracao, ajuste, aprovacao e bloqueio |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Derivar `INTAKE` inicial a partir da ideia | 3 | - |
| T2 | Persistir e revisar o gate humano do intake | 3 | T1 |
| T3 | Bloquear PRD quando o intake estiver insuficiente | 2 | T2 |

## Feature 4: PRD feature-first com aprovacao humana

#### Objetivo de Negocio

Traduzir o `INTAKE` aprovado em um `PRD` implementavel, feature-first e
pronto para decomposicao `issue-first`.

#### Comportamento Esperado

O `planner` gera o `PRD`, o PM revisa e aprova, e o documento sai com
rastreabilidade minima `feature -> fase -> epico -> issue`.

#### Criterios de Aceite

- [ ] O `PRD` e derivado exclusivamente de um `INTAKE` aprovado.
- [ ] O `PRD` explicita features, criterios de aceite e rastreabilidade minima.
- [ ] O gate `PRD -> planning` continua humano e explicito.
- [ ] O fluxo nao avanca para planning enquanto o `PRD` nao estiver aprovado.

#### Dependencias com Outras Features

- Feature 3: intake aprovado

#### Riscos Especificos

- features mal definidas contaminarem todo o planejamento subsequente

#### Fases de Implementacao

1. Ler o intake aprovado.
2. Gerar o `PRD` feature-first no repositorio alvo.
3. Coletar aprovacao ou ajuste do PM.
4. Bloquear planning ate o gate estar fechado.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | indice derivado | PRD sincronizado para consultas e checagem de drift |
| Backend | planner documental | geracao do `PRD` e rastreabilidade |
| Frontend | Telegram | conversa de aprovacao do PRD |
| Testes | gate PRD | cenarios de aprovacao, ajuste e bloqueio |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Gerar `PRD` feature-first a partir do intake aprovado | 5 | - |
| T2 | Persistir gate humano do PRD | 3 | T1 |
| T3 | Validar rastreabilidade minima para planning seguro | 3 | T2 |

## Feature 5: Planejamento issue-first com gates seniores e preambulo socratico

#### Objetivo de Negocio

Materializar a arvore `issue-first` ate task e elevar a qualidade dos handoffs
com raciocinio de especialista antes de cada acao material.

#### Comportamento Esperado

Depois do `PRD` aprovado, o `planner` decompone o projeto em fases, epicos,
issues, sprints e tasks; o agente senior gateia cada nivel; e todo handoff
relevante comeca por um preambulo socratico curto e acionavel.

#### Criterios de Aceite

- [ ] A arvore `issue-first` vai de fase ate task antes de qualquer execucao do
  projeto alvo.
- [ ] Cada nivel passa por gate do agente senior conforme o fluxo canonico.
- [ ] O handoff socratico registra `objetivo_subjacente`,
  `pergunta_de_especialista`, `acao_operacional` e
  `evidencias_consideradas`.
- [ ] O sync SQLite roda apos as escritas documentais, mantendo Markdown como
  autoridade.
- [ ] A capability encerra na prontidao do projeto alvo para seguir o fluxo
  normal de implementacao de issue.

#### Dependencias com Outras Features

- Feature 4: PRD aprovado

#### Riscos Especificos

- o preambulo socratico virar formalismo sem melhorar a decisao

#### Contrato do Handoff Socratico

| Campo | Papel |
|---|---|
| `objetivo_subjacente` | o problema real que o handoff tenta resolver |
| `pergunta_de_especialista` | como a maior autoridade no assunto abordaria o objetivo |
| `acao_operacional` | o que o agente vai fazer de fato apos pensar |
| `evidencias_consideradas` | docs, handoffs e provas lidas antes da acao |

#### Fases de Implementacao

1. Decompor o PRD em fases e epicos.
2. Materializar issues, sprints e tasks.
3. Aplicar gate senior em cada nivel.
4. Aplicar preambulo socratico antes dos handoffs materiais.

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | indice derivado | sync apos cada lote documental relevante |
| Backend | planner + senior gates | planejamento e handoffs auditaveis |
| Frontend | Telegram e chat operativo | prompts de gate e raciocinio socratico |
| Testes | flow-to-task | cobertura da arvore, gates e handoffs socraticos |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Decompor o PRD em fases e epicos com gate senior | 5 | - |
| T2 | Materializar issues, sprints e tasks | 5 | T1 |
| T3 | Aplicar contrato de handoff socratico em planning, review, audit e execucao | 5 | T2 |

## 13. Estrutura de Fases

### Reconciliacao com o scaffold deste repositorio (OC-ISSUE-FIRST-FACTORY)

- IDs `EPIC-F*-*` e `ISSUE-F*-*` sob `PROJETOS/OC-ISSUE-FIRST-FACTORY/` (ex.: `EPIC-F1-01`, `ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO`) referem-se a **este** repositorio: governanca e bootstrap da capability.
- IDs com prefixo `EPIC-ALVO-*` e `ISSUE-ALVO-*` nas tabelas abaixo e na secao 14 descrevem o backlog **esperado no repositorio alvo** depois que a capability materializar o fluxo; nao sao pastas nem ficheiros neste repo ate existirem la.

## Fase 1: Ingresso e Bootstrap do Projeto Alvo

- **Objetivo**: receber o pedido inicial, resolver o repositorio alvo e aplicar o
  scaffold canonico com sync derivado.
- **Features incluídas**:
  - Feature 1
  - Feature 2
- **Gate de saída**: o projeto alvo esta com repositorio resolvido, scaffold
  canonico pronto e indice derivado sincronizado.
- **Critérios de aceite**:
  - pedido inicial normalizado e rastreavel
  - `repo_mode` resolvido com HITL quando houver criacao externa
  - scaffold canonico persistido no repositorio alvo
  - SQLite sincronizado como derivacao do Markdown

### Épicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-ALVO-F1-01 | Feature 1 | todo | 8 |
| EPIC-ALVO-F1-02 | Feature 2 | todo | 11 |

## Fase 2: Intake e PRD com HITL

- **Objetivo**: gerar `INTAKE` e `PRD` aprovados antes do planning.
- **Features incluídas**:
  - Feature 3
  - Feature 4
- **Gate de saída**: `INTAKE` e `PRD` aprovados e prontos para planning seguro.
- **Critérios de aceite**:
  - `INTAKE` persiste e fecha o gate humano
  - `PRD` feature-first persiste e fecha o gate humano
  - rastreabilidade minima do `PRD` esta presente

### Épicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-ALVO-F2-01 | Feature 3 | todo | 8 |
| EPIC-ALVO-F2-02 | Feature 4 | todo | 11 |

## Fase 3: Planning Issue-First e Handoff Socratico

- **Objetivo**: materializar a arvore `issue-first` ate task com gates do agente
  senior e preambulo socratico.
- **Features incluídas**:
  - Feature 5
- **Gate de saída**: o projeto alvo esta pronto para o fluxo normal de
  execucao de issue.
- **Critérios de aceite**:
  - fases, epicos, issues, sprints e tasks existem
  - gates do agente senior foram aplicados nos niveis do planning
  - handoffs relevantes incluem o contrato socratico

### Épicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-ALVO-F3-01 | Feature 5 | todo | 10 |
| EPIC-ALVO-F3-02 | Feature 5 | todo | 8 |

## 14. Epicos

### Épico: Ingresso Telegram do Projeto

- **ID**: EPIC-ALVO-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: normalizar o pedido inicial e deixar o fluxo apto a decidir o
  proximo passo do repositorio alvo.
- **Resultado de Negócio Mensurável**: o PM consegue iniciar um projeto novo via
  Telegram sem sair do canal e sem preencher um formulario tecnico fora do fluxo.
- **Contexto Arquitetural**: bridge Telegram atual, `planner` e contrato
  conversacional minimo do pedido inicial.
- **Definition of Done**:
  - [ ] pedido inicial normalizado
  - [ ] `repo_mode` resolvido
  - [ ] follow-ups objetivos cobrem lacunas de nome ou ideia
  - [ ] HITL explicito quando houver repo novo

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-ALVO-F1-01-001-NORMALIZAR-PEDIDO-INICIAL-DE-PROJETO | Normalizar pedido inicial de projeto | 3 | todo | Feature 1 |
| ISSUE-ALVO-F1-01-002-RESOLVER-MODO-DE-REPOSITORIO-E-HITL | Resolver modo de repositorio e HITL | 5 | todo | Feature 1 |

### Épico: Bootstrap do Repositorio Alvo

- **ID**: EPIC-ALVO-F1-02
- **Fase**: F1
- **Feature de Origem**: Feature 2
- **Objetivo**: provisionar ou vincular o repositorio alvo e aplicar o scaffold
  canonico com sync derivado.
- **Resultado de Negócio Mensurável**: um pedido valido gera um repositorio alvo
  pronto para `INTAKE` e `PRD`, sem bootstrap manual.
- **Contexto Arquitetural**: integracao GitHub, `scripts/criar_projeto.py`,
  sync do indice SQLite derivado.
- **Definition of Done**:
  - [ ] repo existente ou repo novo resolvido
  - [ ] scaffold canonico persistido
  - [ ] wrappers `SESSION-*` presentes
  - [ ] indice derivado sincronizado

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-ALVO-F1-02-001-PROVISIONAR-REPOSITORIO-ALVO | Provisionar repositorio alvo | 5 | todo | Feature 2 |
| ISSUE-ALVO-F1-02-002-GERAR-SCAFFOLD-CANONICO-E-SYNC-DERIVADO | Gerar scaffold canonico e sync derivado | 6 | todo | Feature 2 |

### Épico: Intake Inicial com HITL

- **ID**: EPIC-ALVO-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 3
- **Objetivo**: gerar o `INTAKE` inicial e fechar o gate humano do intake.
- **Resultado de Negócio Mensurável**: o projeto alvo tem um `INTAKE`
  estruturado, aprovavel e rastreavel a partir da ideia inicial.
- **Contexto Arquitetural**: prompts de intake, repo alvo e contexto do pedido
  inicial normalizado.
- **Definition of Done**:
  - [ ] `INTAKE` gerado e persistido
  - [ ] gate humano do intake encerrado
  - [ ] lacunas bloqueantes sao reportadas antes do PRD

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-ALVO-F2-01-001-GERAR-INTAKE-INICIAL-A-PARTIR-DA-IDEIA | Gerar intake inicial a partir da ideia | 5 | todo | Feature 3 |
| ISSUE-ALVO-F2-01-002-REGISTRAR-GATE-HUMANO-DO-INTAKE | Registrar gate humano do intake | 3 | todo | Feature 3 |

### Épico: PRD Feature-First com HITL

- **ID**: EPIC-ALVO-F2-02
- **Fase**: F2
- **Feature de Origem**: Feature 4
- **Objetivo**: gerar o `PRD` feature-first e fechar o gate humano do PRD.
- **Resultado de Negócio Mensurável**: o projeto alvo ganha um `PRD`
  implementavel, rastreavel e pronto para planning seguro.
- **Contexto Arquitetural**: prompts de PRD, rastreabilidade `feature -> fase ->
  epico -> issue` e persistencia no repo alvo.
- **Definition of Done**:
  - [ ] `PRD` gerado a partir de intake aprovado
  - [ ] gate humano do PRD encerrado
  - [ ] rastreabilidade minima pronta para planning

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-ALVO-F2-02-001-GERAR-PRD-FEATURE-FIRST-A-PARTIR-DO-INTAKE | Gerar PRD feature-first a partir do intake | 5 | todo | Feature 4 |
| ISSUE-ALVO-F2-02-002-REGISTRAR-GATE-HUMANO-DO-PRD | Registrar gate humano do PRD | 3 | todo | Feature 4 |

### Épico: Arvore Issue-First do Projeto Alvo

- **ID**: EPIC-ALVO-F3-01
- **Fase**: F3
- **Feature de Origem**: Feature 5
- **Objetivo**: decompor o PRD aprovado em fases, epicos, issues, sprints e tasks.
- **Resultado de Negócio Mensurável**: o projeto alvo chega ao nivel de task
  antes da primeira execucao de issue.
- **Contexto Arquitetural**: `SESSION-PLANEJAR-PROJETO.md`,
  `PROMPT-PLANEJAR-FASE.md`, templates `issue-first`.
- **Definition of Done**:
  - [ ] fases e epicos materializados
  - [ ] issues, sprints e tasks materializados
  - [ ] gates do agente senior aplicados

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-ALVO-F3-01-001-DECOMPOR-PRD-EM-FASES-E-EPICOS | Decompor PRD em fases e epicos | 5 | todo | Feature 5 |
| ISSUE-ALVO-F3-01-002-MATERIALIZAR-ISSUES-SPRINTS-E-TASKS | Materializar issues, sprints e tasks | 5 | todo | Feature 5 |

### Épico: Handoff Socratico e Gates Seniores

- **ID**: EPIC-ALVO-F3-02
- **Fase**: F3
- **Feature de Origem**: Feature 5
- **Objetivo**: formalizar o preambulo socratico e aplica-lo aos handoffs
  relevantes do fluxo.
- **Resultado de Negócio Mensurável**: planning, review, audit e execucao usam
  um raciocinio de especialista antes de agir.
- **Contexto Arquitetural**: contratos de handoff, topologia local/senior e
  fluxo canonico do framework.
- **Definition of Done**:
  - [ ] contrato do handoff socratico definido
  - [ ] preambulo socratico aplicado nos handoffs relevantes
  - [ ] sync derivado mantem rastreabilidade apos escritas documentais

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-ALVO-F3-02-001-DEFINIR-CONTRATO-DE-HANDOFF-SOCRATICO | Definir contrato de handoff socratico | 3 | todo | Feature 5 |
| ISSUE-ALVO-F3-02-002-APLICAR-PREAMBULO-SOCRATICO-AOS-GATES-DO-FLUXO | Aplicar preambulo socratico aos gates do fluxo | 5 | todo | Feature 5 |

## 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| Telegram bridge | canal | host toolkit | ingresso do pedido inicial | active |
| GitHub | repositorio | externo | repo existente ou repo novo com HITL | pending |
| scripts/criar_projeto.py | scaffold | openclaw | bootstrap canonico do projeto alvo | active |
| bin/sync-openclaw-projects-db.sh | indice derivado | openclaw | sync SQLite apos escritas documentais | active |
| OpenRouter senior gate | agente senior | runtime | gates de planning, review e auditoria | active |

## 16. Rollout e Comunicacao

- **Estratégia de deploy**: habilitar primeiro em um projeto canario criado via
  Telegram, validar o fluxo ate task e depois expandir para uso geral.
- **Comunicação de mudanças**: documentar o prompt inicial esperado,
  `repo_mode`, HITL de GitHub e o contrato do handoff socratico.
- **Treinamento necessário**: alinhamento curto do PM sobre campos minimos do
  pedido inicial e sobre o que o preambulo socratico significa.
- **Suporte pós-launch**: tratar falhas de bootstrap, drift de indice e lacunas
  de prompt como follow-ups de issue.

## 17. Revisões e Auditorias

- **Auditorias planejadas**:
  - F1-R01 para ingresso e bootstrap
  - F2-R01 para gates de `INTAKE` e `PRD`
  - F3-R01 para arvore `issue-first` e handoff socratico
- **Critérios de auditoria**:
  - aderencia ao fluxo canonicamente gated
  - ausencia de drift entre Markdown e SQLite derivado
  - ausencia de vazamento de secrets
  - presenca do preambulo socratico nos handoffs relevantes
- **Threshold anti-monolito**: a capability deve parar na arvore `issue-first`;
  qualquer tentativa de absorver a implementacao do projeto alvo no mesmo fluxo
  deve ser recusada como scope drift.

## 18. Checklist de Prontidão

- [x] Intake referenciado e versao confirmada
- [x] Features definidas com criterios de aceite verificaveis
- [x] Cada feature com impacts por camada preenchidos
- [x] Rastreabilidade explicita no PRD (`Feature -> Fase -> EPIC-ALVO-* / ISSUE-ALVO-*` na secao 14; ver reconciliacao na secao 13)
- [x] Epicos e issues ALVO definidos no texto do PRD e vinculados as features (secao 14)
- [ ] Arvore issue-first completa das fases F2 e F3 materializada neste repositorio (ainda nao existe sob `PROJETOS/OC-ISSUE-FIRST-FACTORY/`; apenas F1 do scaffold da capability)
- [x] Fases definidas com gates de saída
- [x] Dependências externas mapeadas
- [x] Riscos identificados e mitigacoes planejadas
- [x] Rollout planejado

## 19. Anexos e Referências

- [Intake](INTAKE-OC-ISSUE-FIRST-FACTORY.md)
- [Audit Log](AUDIT-LOG.md)
- [Fase](F1-FUNDACAO/F1_OC-ISSUE-FIRST-FACTORY_EPICS.md)
- [Epic](F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Issue bootstrap](F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md)
- [Relatorio de auditoria](F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md)
- `src/nemoclaw-host/telegram-bridge-host.js`
- `scripts/criar_projeto.py`
- `bin/sync-openclaw-projects-db.sh`
- `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`

> Frase Guia: "Ideia entra pelo Telegram, governanca entra pelo framework,
> especialista pensa antes de agir."
