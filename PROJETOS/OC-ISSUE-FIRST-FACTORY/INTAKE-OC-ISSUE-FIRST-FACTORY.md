---
doc_id: "INTAKE-OC-ISSUE-FIRST-FACTORY.md"
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

# INTAKE - OC-ISSUE-FIRST-FACTORY

> Intake da capability que transforma uma ideia recebida via Telegram em um
> projeto novo com bootstrap canonico, intake, PRD e arvore `issue-first`
> materializada ate o nivel de task, sem deslocar a autoridade do Markdown.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: formalizar no framework a capability de abrir
  um novo projeto a partir de Telegram, bootstrapar o repositorio alvo,
  gerar `INTAKE` e `PRD` com HITL e depois materializar a arvore
  `issue-first` com gates do agente senior e handoff socratico.

### Fontes principais

- `src/nemoclaw-host/telegram-bridge-host.js`
- `scripts/criar_projeto.py`
- `bin/sync-openclaw-projects-db.sh`
- `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/COMUM/PROMPT-INTAKE-PARA-PRD.md`
- `PROJETOS/COMUM/PROMPT-PLANEJAR-FASE.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`

### Mapeamento de features prioritarias

- `Receber pedido de novo projeto via Telegram`
  - actor: PM falando com o `planner`
  - fontes: `telegram-bridge-host.js`, wrappers `SESSION-*`
- `Resolver repositorio alvo com HITL`
  - actor: PM e agente local
  - fontes: `scripts/criar_projeto.py`, bootstrap de sandbox, integracao GitHub
- `Gerar intake e PRD aprovaveis`
  - actor: planner local com gate humano obrigatorio
  - fontes: `SESSION-CRIAR-INTAKE.md`, `SESSION-CRIAR-PRD.md`,
    `PROMPT-INTAKE-PARA-PRD.md`
- `Materializar arvore issue-first ate task`
  - actor: planner local e agente senior
  - fontes: `SESSION-PLANEJAR-PROJETO.md`, `PROMPT-PLANEJAR-FASE.md`,
    `GOV-ISSUE-FIRST.md`
- `Aplicar preambulo socratico nos handoffs`
  - actor: planner, executor, revisor e auditor
  - fontes: topologia multi-agente e handoffs ja previstos no framework

## 1. Resumo Executivo

- nome curto da iniciativa: issue-first factory
- tese em 1 frase: permitir que o PM descreva uma ideia via Telegram e receba um
  projeto novo, com repositorio bootstrapado, `INTAKE` e `PRD` aprovaveis e
  arvore `issue-first` pronta para gates do framework.
- valor esperado em 3 linhas:
  - reduzir o tempo entre "tenho uma ideia" e "tenho um projeto governado"
  - padronizar criacao de repositorio, scaffold, `INTAKE`, `PRD` e planning
  - forcar raciocinio de especialista via preambulo socratico antes de cada
    handoff material

## 2. Problema ou Oportunidade

- problema atual: abrir um projeto novo ainda depende de coordenacao manual entre
  ideia, repositorio, scaffold, `INTAKE`, `PRD`, planning e handoffs.
- evidencia do problema: o repositiorio ja tem bridge Telegram, scaffold local,
  prompts canonicos e indice SQLite, mas nao tem uma capability unica que costure
  esse fluxo de ponta a ponta.
- custo de nao agir: novos projetos continuam nascendo com drift entre chat,
  GitHub, docs e planejamento, aumentando retrabalho e risco de escopo frouxo.
- por que agora: o framework ja esta maduro o bastante para formalizar essa
  camada como backlog proprio, sem misturar com a execucao das tasks de cada
  projeto criado.

## 3. Publico e Operadores

- usuario principal: PM que quer abrir um novo projeto e governa-lo pelo fluxo
  OpenClaw desde o primeiro prompt.
- usuario secundario: agente `planner`, agente senior e mantenedor do toolkit
  que precisam operar o fluxo sem drift entre Markdown, SQLite e repositorio alvo.
- operador interno: `planner`, `telegram-bridge`, adaptador GitHub,
  `scripts/criar_projeto.py` e sync do indice SQLite derivado.
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: transformar uma ideia declarada no Telegram em um projeto novo
  governado pelo framework ate o nivel de task.
- jobs secundarios:
  - resolver se o projeto usara repo existente ou repo novo com HITL
  - bootstrapar o repositorio alvo com scaffold canonico e indice derivado
  - gerar `INTAKE` e `PRD` aprovaveis antes do planning
  - materializar fases, epicos, issues, sprints e tasks com gate senior
  - aplicar raciocinio socratico antes de cada handoff relevante
- tarefa atual que sera substituida: coordenar manualmente abertura de projeto,
  criacao de repo, scaffold, `INTAKE`, `PRD` e planning

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. O PM envia ao `planner` via Telegram o `project_name`, a `project_idea`,
   o `repo_mode` e opcionalmente a `repo_url`.
2. O sistema normaliza o pedido inicial, valida o nome canonico e, se
   `repo_mode=create`, apresenta o plano de criacao do repositorio e espera
   aprovacao explicita.
3. O fluxo provisiona ou vincula o repositorio alvo, executa o scaffold
   canonico e sincroniza o indice SQLite derivado sem promover SQLite a fonte
   normativa.
4. O `planner` gera uma versao inicial de `INTAKE`, o PM aprova ou ajusta.
5. O `planner` gera o `PRD` feature-first a partir do intake aprovado, o PM
   aprova ou ajusta.
6. Depois do PRD aprovado, o `planner` materializa fases, epicos, issues,
   sprints e tasks com gates obrigatorios do agente senior.
7. Cada handoff relevante comeca por um preambulo socratico, e a capability
   encerra quando o projeto alvo esta pronto para seguir o fluxo normal de
   execucao de issue.

## 6. Escopo Inicial

### Dentro

- ingresso via Telegram para abertura de projeto
- contrato minimo do pedido inicial:
  `project_name`, `project_idea`, `repo_mode`, `repo_url?`
- resolucao de repo existente ou repo novo com HITL
- bootstrap do repositorio alvo com scaffold canonico
- geracao de `INTAKE` e `PRD` com gates humanos obrigatorios
- materializacao da arvore `issue-first` ate task
- contrato de handoff socratico aplicado a planning, review, audit e execucao
- sync do indice SQLite derivado, mantendo Markdown como autoridade

### Fora

- implementacao das tasks do projeto alvo apos a arvore estar pronta
- execucao automatica de repositorio novo sem aprovacao explicita do PM
- armazenamento de secrets de GitHub ou Telegram em Git ou em prompts
  persistidos
- transformar SQLite em fonte de verdade do projeto
- observabilidade ampla, dashboard dedicado ou controle financeiro

## 7. Resultado de Negocio e Metricas

- objetivo principal: reduzir o tempo e o atrito para abrir projetos novos no
  OpenClaw sem perder governanca documental.
- metricas leading:
  - tempo entre pedido inicial no Telegram e `INTAKE` gerado
  - tempo entre `INTAKE` aprovado e `PRD` gerado
  - tempo entre `PRD` aprovado e arvore `issue-first` materializada ate task
  - percentual de handoffs com preambulo socratico presente
- metricas lagging:
  - menor retrabalho na abertura de projetos novos
  - menor numero de projetos com drift entre repo, docs e indice derivado
  - menor numero de correcoes manuais no scaffold inicial
- criterio minimo para considerar sucesso: a partir de um pedido via Telegram,
  o PM consegue chegar a um projeto alvo com `INTAKE` e `PRD` aprovados e
  arvore `issue-first` pronta para execucao de issues, sem vazar secrets e sem
  deslocar a autoridade do Markdown.

## 8. Restricoes e Guardrails

- restricoes tecnicas:
  - o fluxo deve reutilizar o bridge Telegram atual e o `planner` ja existente
  - `scripts/criar_projeto.py` continua sendo a base do scaffold
  - SQLite permanece indice derivado/local; Markdown canonico prevalece
- restricoes operacionais:
  - criacao de repo GitHub exige HITL explicito antes da acao externa
  - `INTAKE` e `PRD` continuam com aprovacao humana obrigatoria
  - nao pode haver execucao de task do projeto alvo antes da arvore pronta
- restricoes legais ou compliance:
  - tokens GitHub/Telegram e credenciais seguem fora do Git
  - prompts persistidos nao devem conter segredos
- restricoes de prazo:
  - o v1 cobre criacao do projeto ate task; implementacao das tasks fica fora
- restricoes de design ou marca:
  - nenhuma alem de preservar o contrato conversacional existente do Telegram

## 9. Dependencias e Integracoes

- sistemas internos impactados:
  - `planner`
  - `telegram-bridge`
  - `scripts/criar_projeto.py`
  - wrappers `SESSION-*`
  - indice SQLite derivado de `PROJETOS/`
- sistemas externos impactados:
  - GitHub, quando houver repo novo ou repo existente remoto
- dados de entrada necessarios:
  - `project_name`
  - `project_idea`
  - `repo_mode`
  - `repo_url` quando aplicavel
  - aprovacoes humanas de `INTAKE` e `PRD`
- dados de saida esperados:
  - repositorio alvo resolvido
  - scaffold canonico do projeto
  - `INTAKE` e `PRD` persistidos
  - fases, epicos, issues, sprints e tasks
  - indice SQLite sincronizado como suporte derivado

## 10. Arquitetura Afetada

- backend:
  - orquestracao do `planner` para interpretar o pedido inicial
  - adaptador de repositorio alvo e bootstrap canonico
  - geracao documental de `INTAKE`, `PRD` e planning
- frontend:
  - interacao conversacional via Telegram com prompts de aprovacao e ajuste
- banco/migracoes:
  - sem banco canonico novo; o projeto usa Markdown versionado
  - SQLite continua derivado para consulta/sync, sem versionamento em Git
- observabilidade:
  - handoffs e progresso podem usar o feed host-side, sem virar dashboard proprio
- autorizacao/autenticacao:
  - tokens de Telegram/GitHub continuam fora do Git e fora dos prompts persistidos
- rollout:
  - piloto em um projeto alvo novo, depois generalizacao para novos projetos

## 11. Riscos Relevantes

- risco de produto: o fluxo pode produzir projeto com escopo frouxo se a ideia
  inicial vier vaga demais.
- risco tecnico: drift entre pedido inicial, repo alvo, scaffold e indice SQLite.
- risco operacional: criacao de repo novo sem HITL suficiente ou sincronizacao
  parcial entre Markdown e SQLite.
- risco de dados: vazamento de segredo de GitHub/Telegram ou promocao indevida
  de dado derivado a canonico.
- risco de adocao: o preambulo socratico pode virar ritual vazio se nao for
  acoplado ao objetivo subjacente de cada handoff.

## 12. Nao-Objetivos

- nao implementar as tasks do projeto alvo dentro desta capability
- nao substituir os gates humanos de `INTAKE` e `PRD`
- nao substituir os gates do agente senior em planning, review e auditoria
- nao versionar o arquivo SQLite do projeto alvo
- nao transformar a capability em produto de observabilidade ou dashboard

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: o framework possui componentes isolados do fluxo, mas nao a
  capability unica que costura Telegram -> repo -> `INTAKE` -> `PRD` ->
  planning `issue-first`.
- impacto operacional: o PM continua coordenando manualmente passos que deveriam
  estar governados pelo framework.
- evidencia tecnica: bridge Telegram, scaffold de projeto, sync SQLite e
  prompts canonicos ja existem, mas a orquestracao integrada ainda nao esta
  descrita como produto.
- componente(s) afetado(s): `planner`, bridge Telegram, integracao GitHub,
  gerador de scaffold, prompts documentais e indice SQLite derivado.
- riscos de nao agir: novos projetos continuam abrindo com procedimentos
  informais e baixa rastreabilidade.

## 14. Lacunas Conhecidas

- decidir a menor superficie de integracao GitHub do v1 sem acoplar demais a
  capability ao provedor
- calibrar o formato exato do preambulo socratico para ser curto e acionavel
- definir o minimo de telemetria necessario para depurar falhas de bootstrap sem
  ampliar demais o escopo
