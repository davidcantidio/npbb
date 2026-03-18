---
doc_id: "PRD-FW5.md"
version: "2.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "FW5"
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

# PRD - FW5

> Este PRD reconstroi o projeto a partir do intake aprovado e da governanca canonica.
> O nome canonico do projeto e `FW5`; referencias a `FRAMEWORK3` aparecem apenas
> como contexto historico da demanda original.
> O principio do projeto e `delivery-first`, materializado aqui como `feature-first`.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-FW5.md](./INTAKE-FW5.md)
- **Versao do intake**: 1.1
- **Data de criacao**: 2026-03-18
- **PRD derivado** (se aplicavel): nao_aplicavel
- **Contexto legado**: a demanda nasce da iniciativa antes descrita como `FRAMEWORK3`, agora normalizada como capacidade canonica `FW5`

## 1. Resumo Executivo

- **Nome do projeto**: FW5
- **Tese em 1 frase**: transformar o fluxo documental manual de planejamento e execucao de projetos em uma experiencia governada por features entregaveis, com aprovacao humana quando necessario, automacao segura quando possivel e rastreabilidade persistida ponta a ponta.
- **Valor esperado em 3 linhas**:
  - eliminar a copia manual de arquivos `SESSION-*` e `TEMPLATE-*` e reduzir o trabalho operacional repetitivo do PM.
  - permitir que o projeto seja aberto, planejado, executado e auditado a partir de features demonstraveis, sem perder a governanca existente.
  - persistir prompts, decisoes, aprovacoes e evidencias para auditoria, analytics e futuro treinamento de um LLM especialista em gestao de projetos.

## 2. Problema ou Oportunidade

- **Problema atual**: o framework atual depende de copia, renomeacao e preenchimento manual de artefatos Markdown, com baixa automacao operacional e pouca centralizacao de historico.
- **Evidencia do problema**: o fluxo corrente exige repetir a cada projeto a criacao manual de intake, PRD, fases, epicos, issues e tasks a partir de arquivos-base, alem de gates manuais sucessivos.
- **Custo de nao agir**: o PM continua consumindo tempo em trabalho mecanico, a operacao nao escala com seguranca e o historico fica fragmentado para auditoria e treinamento.
- **Por que agora**: o framework ja atingiu maturidade suficiente para migrar do planejamento orientado a arquitetura para um planejamento orientado a entrega, sem perder a governanca existente.

## 3. Publico e Operadores

- **Usuario principal**: PM / Product Manager responsavel por abrir, aprovar e acompanhar projetos
- **Usuario secundario**: engenheiros e agentes IA que executam issues e tasks
- **Operador interno**: AgentOrchestrator e subagentes especializados
- **Quem aprova ou patrocina**: PM, com poder de definir o nivel de autonomia operacional por projeto

## 4. Jobs to be Done

- **Job principal**: conduzir um projeto do intake ate a auditoria de fase com rastreabilidade completa e menor dependencia de operacao manual repetitiva.
- **Jobs secundarios**:
  - consultar o estado de qualquer feature, fase, epico, issue ou task
  - revisar historico de aprovacoes, prompts e artefatos gerados
  - usar os dados persistidos para melhoria continua e treinamento futuro
- **Tarefa atual que sera substituida**: copiar e adaptar arquivos da pasta `COMUM/`, preencher cabecalhos manualmente e controlar gates de aprovacao de forma artesanal

## 5. Escopo

### Dentro

- estruturar intake a partir de contexto bruto com rastreabilidade, lacunas explicitas e gate de aprovacao
- gerar PRD `feature-first` a partir de intake aprovado, preservando taxonomias, origem e restricoes
- derivar fases, epicos, issues e tasks com rastreabilidade `feature -> fase -> epico -> issue`
- selecionar e acompanhar a proxima unidade elegivel para execucao, com autonomia configuravel e gates humanos
- preparar review, auditoria e consulta de historico, decisoes, evidencias e artefatos no modulo administrativo do NPBB

### Fora

- substituicao completa do sistema documental atual como unica fonte de verdade
- interface mobile
- multi-tenancy avancado
- fine-tuning real de LLM nesta fase
- migracao obrigatoria de projetos legados para o fluxo assistido no MVP

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: reduzir em mais de 80% o tempo manual do PM no ciclo de governanca e planejamento de projeto.
- **Metricas leading**:
  - numero de projetos iniciados via FW5
  - percentual de etapas automatizadas com seguranca
  - volume de eventos operacionais persistidos por projeto
- **Metricas lagging**:
  - tempo medio para levar um projeto do intake ate a execucao de issue
  - qualidade percebida das entregas
  - taxa de auditorias aprovadas sem retrabalho estrutural
- **Criterio minimo para considerar sucesso**: o FW5 deve conseguir levar um projeto do intake aprovado ate uma issue executavel com rastreabilidade completa e historico persistido.

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: reutilizar o stack existente do NPBB (FastAPI, PostgreSQL, React/Vite) e preservar compatibilidade com a estrutura atual em `PROJETOS/`.
- **Restricoes operacionais**: obedecer aos arquivos `GOV-*`, `SESSION-*`, `TEMPLATE-*` e ao algoritmo de negocio sem inventar novas regras fora da governanca vigente.
- **Restricoes legais ou compliance**: nao_aplicavel
- **Restricoes de prazo**: buscar MVP funcional em poucas iteracoes, priorizando fluxo util antes de automacao total.
- **Restricoes de design ou marca**: manter a linguagem e a disciplina documental do framework atual.

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: backend FastAPI, banco PostgreSQL, frontend React/Vite, superficie administrativa do NPBB e sistema de agentes
- **Sistemas externos impactados**: nenhum
- **Dados de entrada necessarios**: conteudo dos arquivos `GOV-*`, `SESSION-*`, `TEMPLATE-*`, contexto do projeto fornecido pelo PM e regras do [PROJETOS/Algoritmo.md](../Algoritmo.md)
- **Dados de saida esperados**: artefatos Markdown canonicos, registros estruturados no banco, historico de execucao e trilha de auditoria

## 9. Arquitetura Geral do Projeto

> Visao geral de impacto arquitetural. O eixo do PRD continua sendo comportamento entregavel.

- **Backend**: novos servicos e contratos para intake, PRD, planejamento, elegibilidade, orquestracao e registro de execucoes
- **Frontend**: modulo admin para abrir projetos, revisar artefatos, navegar hierarquia e consultar historico operacional
- **Banco/migracoes**: novas entidades para projetos, artefatos, aprovacoes, rastreabilidade, execucoes e auditorias
- **Observabilidade**: logs estruturados de execucao, trilha de aprovacoes, evidencias e timeline consultavel
- **Autorizacao/autenticacao**: reutilizar o modelo atual do NPBB, com guardas adequadas para operacao administrativa
- **Rollout**: incremental, com coexistencia entre fluxo documental legado e fluxo assistido no FW5

## 10. Riscos Globais

- **Risco de produto**: transformar o projeto em uma plataforma excessivamente tecnica e perder o foco em entregas demonstraveis para o PM.
- **Risco tecnico**: manter compatibilidade com a governanca documental enquanto adiciona persistencia, CRUD e orquestracao.
- **Risco operacional**: calibrar corretamente quando exigir aprovacao humana e quando permitir execucao automatizada.
- **Risco de dados**: registrar historico incompleto ou pouco util para auditoria e treinamento futuro.
- **Risco de adocao**: o PM nao confiar na automacao se o fluxo ficar opaco ou dificil de inspecionar.

### Hipoteses Declaradas

- os niveis exatos de autonomia configuraveis por projeto serao detalhados na implementacao, mas o PRD ja fixa que a capacidade precisa existir
- a forma final de integracao entre o AgentOrchestrator e o ambiente/cliente de agentes em uso permanece decisao tecnica aberta
- o dataset de treinamento e as politicas finais de retencao ficam fora do MVP, mas o historico persistido deve nascer auditavel e reutilizavel
- a estrategia de migracao ou onboarding de projetos legados sera tratada como rollout posterior, sem bloquear o fluxo minimo do MVP

## 11. Nao-Objetivos

- nao substituir completamente os arquivos Markdown por banco de dados
- nao criar um novo framework de agentes do zero sem reaproveitar a governanca existente
- nao considerar a arquitetura como eixo principal de planejamento do projeto
- nao comprometer o MVP com migracao em massa de backlog legado

---

# 12. Features do Projeto

> Cada feature abaixo representa um comportamento utilizavel pelo PM dentro da jornada do projeto.
> Persistencia, CRUD, observabilidade e trilha operacional aparecem como impactos transversais de cada feature, e nao como feature separada.
> As secoes `Fases de Implementacao` abaixo descrevem apenas impactos internos necessarios para entregar a feature; elas nao autorizam organizar backlog, fase, epico ou issue por camada tecnica fora da cadeia `feature -> fase -> epico -> issue`.

## Feature 1: Intake governado a partir de contexto bruto

### Objetivo de Negocio

Eliminar a abertura manual e inconsistente de projetos, garantindo que o PM consiga sair de um contexto bruto para um intake estruturado, auditavel e pronto para gate `Intake -> PRD`.

### Comportamento Esperado

O PM informa o contexto inicial do projeto, recebe um intake estruturado com taxonomias, rastreabilidade, lacunas conhecidas e checklist de prontidao, revisa o material e registra aprovacao ou ajuste antes de seguir.

### Criterios de Aceite

- [ ] o sistema transforma contexto bruto em intake completo com problema, publico, fluxo principal, escopo, metricas, restricoes, riscos e lacunas conhecidas
- [ ] o intake distingue fatos, inferencias e hipoteses e bloqueia a subida para PRD quando houver lacuna critica real
- [ ] o PM consegue revisar, ajustar e aprovar o intake com registro de versao, timestamp e historico da decisao

### Dependencias com Outras Features

- nenhuma obrigatoria

### Riscos Especificos

- intake consolidar hipoteses como fatos e contaminar o restante da cadeia
- a experiencia de abertura virar apenas uma copia digital do processo manual atual

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para projeto, intake, versoes, aprovacoes e lacunas
2. **API**: contratos para criar, revisar, validar e aprovar intake
3. **UI**: formulario assistido de abertura, diff de revisao e estados de gate
4. **Testes**: cobertura de prontidao `Intake -> PRD`, taxonomias e persistencia de historico

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | projetos, intakes, aprovacoes | origem, versao, status, lacunas conhecidas e timestamps |
| Backend | servicos de intake | validacao do gate, geracao estruturada e aprovacao HITL |
| Frontend | abertura assistida do projeto | captura do contexto bruto, revisao do intake e decisao do PM |
| Testes | suites de intake | cobertura de completude, bloqueios e registro de aprovacao |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar intake, estados de versao e aprovacao | 3 | - |
| T2 | Implementar fluxo assistido de geracao e validacao do intake | 3 | T1 |
| T3 | Entregar revisao/aprovacao do intake com historico | 2 | T2 |

---

## Feature 2: PRD `feature-first` derivado de intake aprovado

### Objetivo de Negocio

Garantir que o projeto saia do intake aprovado com um PRD coerente, auditavel e orientado por features demonstraveis, sem voltar ao padrao `architecture-first`.

### Comportamento Esperado

Depois da aprovacao do intake, o PM consegue gerar um PRD completo que preserva as taxonomias do intake, explicita features entregaveis, criterios de aceite verificaveis, impactos arquiteturais por feature e rastreabilidade minima para planejamento posterior.

### Criterios de Aceite

- [ ] o PRD e gerado a partir do intake aprovado preservando frontmatter, origem, restricoes, riscos e nao-objetivos
- [ ] cada feature do PRD declara objetivo de negocio, comportamento esperado, criterios de aceite verificaveis e impactos por camada
- [ ] quando o intake nao sustentar uma nomeacao segura de escopo fino, o PRD deixa a lacuna explicita em vez de inventar comportamento ou issue

### Dependencias com Outras Features

- Feature 1: intake aprovado e pronto para PRD

### Riscos Especificos

- o PRD cair em organizacao por banco/backend/frontend e perder demonstrabilidade
- o documento fechar escopo ingenuamente em areas onde o intake ainda marca lacuna aberta

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para PRD, features e rastreabilidade de origem
2. **API**: contratos para derivar, revisar, ajustar e aprovar PRD
3. **UI**: visualizacao estruturada do PRD, diff e confirmacao de gravacao
4. **Testes**: consistencia intake -> PRD, frontmatter e criterios por feature

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | PRDs, features, versoes | ligacao com intake, historico de revisao e aprovacao |
| Backend | servicos de derivacao do PRD | transformacao `intake -> PRD`, validacao estrutural e rastreabilidade |
| Frontend | revisao do PRD | leitura por secoes, diff e confirmacao do PM |
| Testes | suites de PRD | validacao do template, preservacao de taxonomias e bloqueio de lacunas criticas |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar PRD, features e rastreabilidade com o intake | 3 | - |
| T2 | Implementar derivacao do PRD `feature-first` a partir do intake aprovado | 3 | T1 |
| T3 | Entregar revisao/aprovacao do PRD com validacoes estruturais | 2 | T2 |

---

## Feature 3: Planejamento executavel com rastreabilidade canonica

### Objetivo de Negocio

Permitir que o PM transforme o PRD aprovado em um plano executavel sem reorganizar manualmente o trabalho por camadas tecnicas, preservando a cadeia `feature -> fase -> epico -> issue`.

### Comportamento Esperado

Com o PRD aprovado, o sistema deriva fases, epicos, issues e tasks coerentes com as features do projeto, mantendo `Feature de Origem` explicita e respeitando os limites do modelo `issue-first`.

### Criterios de Aceite

- [ ] cada fase do projeto e definida por valor entregue, com gate de saida e features claramente alocadas
- [ ] cada epico e issue repete explicitamente a `Feature de Origem` usada no PRD
- [ ] a derivacao deixa lacunas explicitas quando uma issue nao puder ser nomeada com seguranca e evita criar itens acima dos limites canonicos sem sinalizacao

### Dependencias com Outras Features

- Feature 2: PRD aprovado com features e criterios de aceite suficientes

### Riscos Especificos

- fases e epicos serem montados por camada tecnica em vez de comportamento entregue
- decomposicao gerar issues grandes ou vagas, invalidando a execucao posterior

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para fases, epicos, issues, tasks e links com features
2. **API**: contratos para derivar hierarquia, dependencias e limites de decomposicao
3. **UI**: mapa do projeto com navegacao por fase, epico, issue e feature
4. **Testes**: rastreabilidade, consistencia de IDs e respeito aos limites de issue/task

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | fases, epicos, issues, tasks | IDs canonicos, dependencias, status e feature de origem |
| Backend | planejador hierarquico | geracao da cadeia executavel a partir do PRD |
| Frontend | mapa do projeto | navegacao da hierarquia e leitura da rastreabilidade |
| Testes | suites de planejamento | consistencia `feature -> fase -> epico -> issue` e sinalizacao de lacunas |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar a hierarquia planejada com links para features | 3 | - |
| T2 | Implementar derivacao de fases, epicos e issues rastreaveis | 3 | T1 |
| T3 | Expor visao administrativa da hierarquia com filtros por feature | 2 | T2 |

---

## Feature 4: Execucao assistida da proxima unidade elegivel

### Objetivo de Negocio

Reduzir o trabalho operacional manual do PM e dos executores, permitindo que o sistema identifique a proxima unidade executavel, monte o contexto correto e aplique gates humanos apenas quando necessario.

### Comportamento Esperado

O sistema identifica a proxima issue/task elegivel, monta contexto suficiente para execucao, aplica a politica de autonomia configurada para o projeto, aciona o fluxo de execucao e registra progresso, bloqueios, outputs e evidencias.

### Criterios de Aceite

- [ ] o sistema identifica a proxima unidade elegivel sem violar dependencias, gates ou regras de `task_instruction_mode`
- [ ] o PM consegue definir quando a execucao segue automaticamente e quando exige confirmacao humana
- [ ] cada execucao registra work order, contexto usado, status, outputs, evidencias e motivo de bloqueio quando houver

### Dependencias com Outras Features

- Feature 3: hierarquia executavel pronta e rastreavel

### Riscos Especificos

- a automacao avancar fora de ordem ou sem contexto suficiente
- a politica de autonomia ficar opaca e gerar desconfianca operacional

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para work orders, execucoes, estados operacionais e politica de autonomia
2. **API**: selecao de unidade elegivel, disparo de execucao e captura de evidencias
3. **UI**: painel da proxima acao recomendada, override humano e acompanhamento de status
4. **Testes**: elegibilidade, gates, bloqueios e persistencia de execucao

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | execucoes, work orders, politicas de autonomia | contexto, estado, evidencias e timestamps |
| Backend | orquestracao operacional | elegibilidade, montagem de contexto, disparo e bloqueio controlado |
| Frontend | acompanhamento da execucao | proxima unidade, status, override e feedback ao PM |
| Testes | suites de execucao | ordem de dependencias, HITL e consistencia do historico operacional |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar work order, estados de execucao e politica de autonomia | 3 | - |
| T2 | Implementar selecao e disparo da proxima unidade elegivel | 3 | T1 |
| T3 | Entregar painel operacional com override humano e visibilidade de evidencias | 2 | T2 |

---

## Feature 5: Governanca final percebida pelo PM

### Objetivo de Negocio

Dar ao PM controle visivel sobre qualidade, governanca e memoria do projeto, permitindo revisar o que foi feito, auditar fases e consultar a trilha completa de decisoes, artefatos e evidencias sem depender de leitura manual fragmentada.

### Comportamento Esperado

Ao fim de uma issue ou fase, o PM consegue abrir um contexto consolidado de review e auditoria, registrar vereditos e follow-ups rastreaveis e consultar a timeline do projeto por projeto, fase, epico, issue ou task.

### Criterios de Aceite

- [ ] cada issue concluida pode ser revisada com veredito claro e cada fase pode passar por auditoria formal com resultado `go` ou `hold`
- [ ] follow-ups de review ou auditoria ficam vinculados ao artefato de origem, ao destino definido e ao historico da decisao
- [ ] o PM consegue consultar linha do tempo, aprovacoes, prompts, outputs, diffs e evidencias relevantes sem depender apenas de arquivos soltos

### Dependencias com Outras Features

- Feature 2: artefatos de intake e PRD aprovados e versionados
- Feature 4: execucoes e evidencias operacionais registradas

### Riscos Especificos

- review e auditoria virarem etapas formais sem efeito real sobre o estado do projeto
- historico existir, mas ser incompleto ou dificil de consultar

### Fases de Implementacao

1. **Modelagem e Migration**: entidades para reviews, auditorias, follow-ups, eventos e timeline
2. **API**: registro de veredito, follow-up, consulta de historico e leitura consolidada de evidencias
3. **UI**: telas de governanca, auditoria, follow-ups e timeline do projeto
4. **Testes**: transicoes de gate, rastreabilidade de follow-up e consulta de historico

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | auditorias, follow-ups, eventos, timeline | vereditos, origem, destino, evidencias e consulta historica |
| Backend | servicos de review, auditoria e timeline | consolidacao de contexto, registro de veredito e leitura auditavel |
| Frontend | governanca final e historico | review, auditoria, follow-ups e timeline navegavel |
| Testes | suites de auditoria/historico | gates `go/hold`, origem de follow-up e integridade da trilha operacional |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|----|------------|
| T1 | Modelar auditoria, follow-ups e timeline auditavel | 3 | - |
| T2 | Implementar review/auditoria com registro de veredito e destino | 3 | T1 |
| T3 | Entregar consultas de historico, aprovacoes e evidencias para o PM | 2 | T2 |

---

# 13. Estrutura de Fases

> As fases agrupam comportamentos entregues ao PM. Nenhuma fase e organizada por camada tecnica isolada.

## Fase 1: Abertura governada do projeto

- **Objetivo**: levar o PM do contexto bruto a um PRD aprovado, rastreavel e pronto para planejamento posterior.
- **Features incluidas**:
  - Feature 1
  - Feature 2
- **Gate de saida**: intake e PRD existem, foram revisados/aprovados e preservam rastreabilidade, restricoes, riscos e hipoteses declaradas.
- **Criterios de aceite**:
  - intake pronto para PRD sem lacuna critica aberta
  - PRD `feature-first` aprovado com criterios de aceite por feature
  - historico de versoes e aprovacoes consultavel

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F1-01 | Feature 1 | todo | 8 |
| EPIC-F1-02 | Feature 2 | todo | 8 |

## Fase 2: Planejamento executavel por features

- **Objetivo**: derivar a cadeia executavel do projeto a partir das features aprovadas no PRD.
- **Features incluidas**:
  - Feature 3
- **Gate de saida**: o projeto exibe fases, epicos, issues e tasks com `Feature de Origem` explicita e sem drift para planejamento por camada.
- **Criterios de aceite**:
  - rastreabilidade `feature -> fase -> epico -> issue` visivel e consistente
  - lacunas de nomeacao fina aparecem explicitamente quando existirem
  - decomposicao respeita limites canonicos de issue/task ou sinaliza necessidade de quebra

### Epicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F2-01 | Feature 3 | todo | 8 |

## Fase 3: Operacao governada e validacao

- **Objetivo**: permitir execucao assistida, governanca de qualidade e consulta completa do historico operacional.
- **Features incluidas**:
  - Feature 4
  - Feature 5
- **Gate de saida**: o sistema executa a proxima unidade elegivel com autonomia controlada, suporta review/auditoria e expoe trilha auditavel de ponta a ponta.
- **Criterios de aceite**:
  - elegibilidade e execucao respeitam dependencias, gates e work order
  - review e auditoria conseguem produzir veredito e follow-up rastreavel
  - timeline operacional e evidencias sao consultaveis pelo PM

### Epicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F3-01 | Feature 4 | todo | 8 |
| EPIC-F3-02 | Feature 5 | todo | 8 |

---

# 14. Epicos

> Cada epico abaixo repete explicitamente a `Feature de Origem` e preserva a cadeia canonica do framework.

## Epico: Intake governado do projeto

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: transformar contexto bruto em intake estruturado, revisavel e aprovavel.
- **Resultado de Negocio Mensuravel**: reduzir fortemente o esforco manual do PM para abrir um projeto dentro da governanca.
- **Contexto Arquitetural**: captura de contexto, validacao de taxonomias, versionamento de intake e historico de aprovacao.
- **Definition of Done**:
  - [ ] intake pode ser criado, validado, revisado e aprovado com trilha consultavel

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F1-01-001 | Estruturar intake inicial a partir de contexto bruto | 5 | todo | Feature 1 |
| ISSUE-F1-01-002 | Registrar revisao e aprovacao governada do intake | 3 | todo | Feature 1 |

---

## Epico: PRD `feature-first` aprovado

- **ID**: EPIC-F1-02
- **Fase**: F1
- **Feature de Origem**: Feature 2
- **Objetivo**: gerar e aprovar um PRD coerente com o intake e com a governanca `feature-first`.
- **Resultado de Negocio Mensuravel**: sair da abertura do projeto com um PRD utilizavel para decomposicao posterior, sem retrabalho estrutural.
- **Contexto Arquitetural**: derivacao intake -> PRD, preservacao de frontmatter, estrutura de features e versoes aprovadas.
- **Definition of Done**:
  - [ ] PRD pode ser gerado, revisado e aprovado preservando origem e criterios por feature

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F1-02-001 | Gerar PRD `feature-first` a partir do intake aprovado | 5 | todo | Feature 2 |
| ISSUE-F1-02-002 | Validar rastreabilidade e gate de aprovacao do PRD | 3 | todo | Feature 2 |

---

## Epico: Planejamento executavel rastreavel

- **ID**: EPIC-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 3
- **Objetivo**: derivar fases, epicos, issues e tasks a partir do PRD, preservando `Feature de Origem`.
- **Resultado de Negocio Mensuravel**: permitir que o PM decomponha um projeto inteiro sem reorganizar manualmente o trabalho por camada tecnica.
- **Contexto Arquitetural**: hierarquia canonica, limites de issue/task, IDs estaveis e links de rastreabilidade.
- **Definition of Done**:
  - [ ] a cadeia `feature -> fase -> epico -> issue` e navegavel e consistente

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F2-01-001 | Derivar fases e epicos a partir das features do PRD | 5 | todo | Feature 3 |
| ISSUE-F2-01-002 | Derivar issues e tasks com `Feature de Origem` explicita | 5 | todo | Feature 3 |

---

## Epico: Execucao assistida com autonomia controlada

- **ID**: EPIC-F3-01
- **Fase**: F3
- **Feature de Origem**: Feature 4
- **Objetivo**: selecionar a proxima unidade elegivel, executar com contexto suficiente e aplicar gates humanos quando necessario.
- **Resultado de Negocio Mensuravel**: reduzir a operacao manual para colocar o projeto em movimento com seguranca e previsibilidade.
- **Contexto Arquitetural**: work orders, politica de autonomia, contexto de execucao, bloqueios e evidencias operacionais.
- **Definition of Done**:
  - [ ] a proxima unidade elegivel pode ser selecionada, executada e acompanhada com historico consultavel

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F3-01-001 | Selecionar a proxima unidade elegivel com contexto completo | 5 | todo | Feature 4 |
| ISSUE-F3-01-002 | Executar com autonomia configuravel e acompanhamento operacional | 5 | todo | Feature 4 |

---

## Epico: Governanca final e historico auditavel

- **ID**: EPIC-F3-02
- **Fase**: F3
- **Feature de Origem**: Feature 5
- **Objetivo**: permitir review, auditoria e consulta do historico operacional com rastreabilidade de follow-ups.
- **Resultado de Negocio Mensuravel**: aumentar a confianca do PM no fluxo e reduzir opacidade na operacao assistida.
- **Contexto Arquitetural**: timeline, auditorias, vereditos, follow-ups, origem/destino e consulta de evidencias.
- **Definition of Done**:
  - [ ] review, auditoria e timeline estao disponiveis com origem e historico claros

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|----|--------|---------|
| ISSUE-F3-02-001 | Preparar review pos-issue e gate de auditoria de fase | 5 | todo | Feature 5 |
| ISSUE-F3-02-002 | Expor timeline auditavel e follow-ups rastreaveis | 5 | todo | Feature 5 |

---

# 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| nenhuma dependencia externa critica no MVP | n-a | n-a | o escopo inicial depende apenas do stack e da governanca ja existentes no NPBB | n-a |
